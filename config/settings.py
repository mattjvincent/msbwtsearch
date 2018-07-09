# host to listen on, 0.0.0.0 means allow anyone to connect
HOST = '0.0.0.0'

# port to use, make sure you have permission
PORT = 9000

# single threaded = False
THREADED = True

# to debug or not debug, that is the question
DEBUG = False

# secret key, probably just leave alone
SECRET_KEY = 'QTLWEB-SECRET'

LOG_LEVEL = 'DEBUG' # CRITICAL / ERROR / WARNING / INFO / DEBUG

result_backend = 'redis://redis:6379/0'
broker_url = 'redis://redis:6379/0'

###############################################################################
#
# API CONFIGURATION
#
###############################################################################

API_R_BASE = 'http://myapiisawesome:8000'

###############################################################################
#
# DISPLAY CONFIGURATION
#
###############################################################################

MAIN_TITLE = 'QTL Viewer'
