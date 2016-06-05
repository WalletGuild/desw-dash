from desw import CFG, models, ses, logger

hwb = models.HWBalance(0, 0, 'DASH', 'dash')
ses.add(hwb)
try:
    ses.commit()
except Exception as ie:
    ses.rollback()
    ses.flush()

