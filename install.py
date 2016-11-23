from desw import ses
from sqlalchemy_models import wallet as wm

hwb = wm.HWBalance(0, 0, 'DASH', 'dash')
ses.add(hwb)
try:
    ses.commit()
except Exception as ie:
    ses.rollback()
    ses.flush()
