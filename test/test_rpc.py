import time
from ledger import Amount

import bitjws
from bitcoinrpc.authproxy import AuthServiceProxy
from desw import CFG
from sqlalchemy_models import wallet as wm, user as um

from desw_dash import get_new_address, get_balance, send_to_address, validate_address, create_client, CONFS, main,\
    ses

CURRENCY = 'DASH'
NETWORK = 'dash'
ADDYFIRSTCHARS = 'XYxy'

testclient = AuthServiceProxy(CFG.get('test', NETWORK))


def check_balances():
    info = testclient.getinfo()
    if info['balance'] <= 0.1:
        print "low balance, please deposit to %s" % testclient.getnewaddress()


def create_user():
    privkey = bitjws.PrivateKey()
    my_pubkey = privkey.pubkey.serialize()
    my_address = bitjws.pubkey_to_addr(my_pubkey)
    username = str(my_address)[0:8]
    user = um.User(username=username)
    ses.add(user)
    try:
        ses.commit()
    except Exception as ie:
        print ie
        ses.rollback()
        ses.flush()
    userkey = um.UserKey(key=my_address, keytype='public', user_id=user.id,
                         last_nonce=0)
    ses.add(userkey)
    ses.add(wm.Balance(total=0, available=0, currency=CURRENCY, reference='open account', user_id=user.id))
    try:
        ses.commit()
    except Exception as ie:
        print ie
        ses.rollback()
        ses.flush()
    return user


def assign_address(address, user):
    dbaddy = ses.query(wm.Address).filter(wm.Address.address == address).first()
    if dbaddy is None:
        ses.add(wm.Address(address, CURRENCY, NETWORK, 'active', user.id))
    elif dbaddy.user_id != user.id:
        dbaddy.user_id = user.id
        ses.add(dbaddy)
    else:
        return
    creds = ses.query(wm.Credit).filter(wm.Credit.address == address)
    for c in creds:
        ses.delete(c)
    try:
        ses.commit()
    except Exception as ie:
        ses.rollback()
        ses.flush()


def test_get_new_address():
    gotaddy = get_new_address()
    assert isinstance(gotaddy, str)
    assert len(gotaddy) > 10
    assert gotaddy[0:1] in ADDYFIRSTCHARS


def test_validate_address():
    gotaddy = get_new_address()
    assert validate_address(gotaddy)
    assert not validate_address(gotaddy[1:])
    assert not validate_address(gotaddy[0:-1])


def test_send_to_address():
    recaddy = testclient.getnewaddress()
    txid = send_to_address(recaddy, Amount("0.01 DASH"))
    assert isinstance(txid, str)
    assert len(recaddy) > 10

    tx = None
    for i in range(0, 60):
        txs = testclient.listtransactions()
        for t in txs:
            if t['txid'] == txid:
                tx = t
                break
        if tx is not None:
            break
        else:
            time.sleep(1)

    assert tx is not None
    assert tx['address'] == recaddy
    assert float(tx['amount']) == 0.01


def test_receive():
    user = create_user()
    address = get_new_address()
    assign_address(address, user)

    txid = testclient.sendtoaddress(address, 0.01)

    for i in range(0, 600):
        c = ses.query(wm.Credit).filter(wm.Credit.address == address).first()
        if c is not None:
            break
        else:
            time.sleep(0.1)
    assert c is not None
    assert c.address == address
    assert c.amount == Amount("0.0100000 DASH")
    assert c.currency == CURRENCY
    assert c.network == NETWORK
    assert c.transaction_state == 'unconfirmed'
    assert c.user_id == user.id
    assert txid in c.ref_id
    bal = ses.query(wm.Balance).filter(wm.Balance.user_id == user.id).filter(wm.Balance.currency == CURRENCY).first()
    assert bal.total == Amount("0.0100000 DASH")
    assert bal.available == 0


def test_receive_already_confirmed():
    txs = create_client().listtransactions("*", 100)
    tx = None
    for t in txs:
        if t['confirmations'] >= float(CFG.get('bitcoin', 'CONFS')) and t['category'] == 'receive':
            tx = t
            break

    if not tx:
        "skipping test_receive_already_confirmed"
        return
    user = create_user()
    assign_address(tx['address'], user)
    main(['transaction', tx['txid']])

    for i in range(0, 50):
        c = ses.query(wm.Credit).filter(wm.Credit.address == tx['address']).first()
        if c is not None:
            break
        else:
            time.sleep(0.1)
    assert c is not None
    assert c.address == tx['address']
    assert c.amount == Amount("%s DASH" % tx['amount'])
    assert c.currency == CURRENCY
    assert c.network == NETWORK
    assert c.transaction_state == 'complete'
    assert c.user_id == user.id
    assert tx['txid'] in c.ref_id
    bal = ses.query(wm.Balance).filter(wm.Balance.user_id == user.id).filter(wm.Balance.currency == CURRENCY).first()
    assert bal.total == Amount("%s DASH" % tx['amount'])
    assert bal.available == Amount("%s DASH" % tx['amount'])


def test_receive_then_confirm():
    txs = create_client().listtransactions("*", 100)
    tx = None
    for t in txs:
        if t['confirmations'] >= CONFS and t['category'] == 'receive':
            tx = t
            break

    if not tx:
        "skipping test_receive_already_confirmed"
        return
    user = create_user()
    assign_address(tx['address'], user)
    print "confirmed tx to credit: %s" % tx['txid']
    main(['transaction', tx['txid']])

    for i in range(0, 50):
        c = ses.query(wm.Credit).filter(wm.Credit.address == tx['address']).first()
        if c is not None:
            break
        else:
            time.sleep(0.1)
    assert c is not None
    c.transaction_state = 'unconfirmed'
    ses.add(c)
    ses.commit()

    main(['block', ""])
    c.load_commodities()
    assert c.address == tx['address']
    assert c.amount == Amount("%s DASH" % tx['amount'])
    assert c.currency == CURRENCY
    assert c.network == NETWORK
    assert c.transaction_state == 'complete'
    assert c.user_id == user.id
    assert tx['txid'] in c.ref_id
    assert len(c.ref_id) > len(tx['txid'])
    bal = ses.query(wm.Balance).filter(wm.Balance.user_id == user.id).filter(wm.Balance.currency == CURRENCY).first()
    assert bal.total == Amount("%s DASH" % tx['amount'])
    assert bal.available == Amount("%s DASH" % tx['amount'])


def test_get_balance():
    bals = get_balance()
    assert 'total' in bals
    assert 'available' in bals
    assert bals['total'] >= bals['available']

    recaddy = testclient.getnewaddress()
    txid = send_to_address(recaddy, Amount("0.01 DASH"))

    time.sleep(0.25)

    bals2 = get_balance()
    assert bals2['available'] <= bals['available'] - Amount("0.01 DASH")
    assert bals2['total'] <= bals['total'] - Amount("0.01 DASH")

