import os
import sys
import logging

from logging import StreamHandler
from logging import Formatter
from logging import Filter
from logging.handlers import SMTPHandler

LOG_FORMAT = ('%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d')


ilogger = logging.getLogger("espa-web")
ilogger.setLevel(logging.DEBUG)

ih = StreamHandler(stream=sys.stdout)
eh = SMTPHandler(mailhost='localhost', fromaddr='espa@usgs.gov', toaddrs=os.getenv('ESPA_WEB_EMAIL_RECEIVE').split(','), subject='ESPA WEB ERROR')

ih.setLevel(logging.DEBUG)
eh.setLevel(logging.CRITICAL)

for handler in [ih, dh, eh]:
    ilogger.addHandler(handler)

    if isinstance(handler, logging.StreamHandler):
        handler.setFormatter(Formatter(LOG_FORMAT))

    if handler.level == logging.DEBUG:
        handler.addFilter(DbgFilter())

