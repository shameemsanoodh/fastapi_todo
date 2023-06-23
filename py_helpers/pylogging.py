from common_includes import *

from refactor_old.misc_utils import get_now

ROOT_LOG_DIR = "./logs/"
ROOT_SERVERLOG_FILE = "server.log"
ROOT_APPLOG_FILE = "app.log"
ROOT_TRACELOG_FILE = 'trace.log'

# Total is upto 512MB of log space per log type
#MAX_LOGFILESIZE = int((1024 * 16) * 1)
#MAX_LOGFILECOUNT = 16

# Setup these objects here to supress link warnings
initialized_pylog = None
pylogs_stdout_enabled = (str(os.getenv('PYLOGS_STDOUT_ENABLED', 'No')) == "Yes")
pylogs_filelog_enabled = (str(os.getenv('PYLOGS_FILELOG_ENABLED', 'No')) == "Yes")
MAX_LOGFILESIZE = int(os.getenv('PYLOGS_MAX_LOGFILESIZE', 32768))
MAX_LOGFILECOUNT = int(os.getenv('PYLOGS_MAX_LOGFILECOUNT', 10))
# Debug (10), Info (20), Warning (30), Error (40), Critical (50)
STDOUT_LEVEL = int(os.getenv('PYLOGS_STDOUT_LEVEL', logging.DEBUG))
FILELOG_LEVEL = int(os.getenv('PYLOGS_FILELOG_LEVEL', logging.DEBUG))

Log = AppLog = TraceLog = None


def logger_initialize_rolling(log_name=None):
    # btoconsole=True, btofile=True, file_level=logging.DEBUG, console_level=logging.INFO):
    if log_name is None:
        return None
    new_log_path = os.path.join(str(ROOT_LOG_DIR), str(str(log_name)))
    new_log = logging.getLogger(str(new_log_path))
    new_log.setLevel(STDOUT_LEVEL)

    # previous formats
    #logformat = logging.Formatter('%(asctime)s %(levelname)-9s %(message)-s', datefmt='%Y-%m-%d %H:%M:%S')
    #logformat = logging.Formatter('%(asctime)s - %(levelname)-9s| %(message)-90s [L:%(lineno)-04d M:%(module)-s F:%(funcName)-s]', datefmt='%Y-%m-%d %H:%M:%S')
    new_log_format = logging.Formatter('%(asctime)s - %(levelname)-9s| [L:%(lineno)-04d M:%(module)-s F:%(funcName)-s]| %(message)-90s', datefmt='%Y-%m-%d %H:%M:%S')

    # create a file handler if log_file is supplied as parameter
    if pylogs_filelog_enabled:
        new_log_filehandler = logging.handlers.RotatingFileHandler(new_log_path, maxBytes=MAX_LOGFILESIZE, backupCount=MAX_LOGFILECOUNT)
        new_log_filehandler.setFormatter(new_log_format)
        new_log_filehandler.setLevel(FILELOG_LEVEL)
        new_log.addHandler(new_log_filehandler)
    if pylogs_stdout_enabled:
        new_console_handler = logging.StreamHandler()
        new_console_handler.setFormatter(new_log_format)
        new_console_handler.setLevel(STDOUT_LEVEL)
        new_log.addHandler(new_console_handler)
    return(new_log)


def load_loggers ():
    global Log, AppLog, TraceLog, initialized_pylog
    if ('initialized_pylog' not in globals()) or (initialized_pylog is None) or (Log is None) or (AppLog is None) or (TraceLog is None):
        print("**** IITIALIZING LOGS - START ****")
        initialized_pylog = True

        Log = logger_initialize_rolling(log_name=ROOT_SERVERLOG_FILE)
        AppLog = logger_initialize_rolling(log_name=ROOT_APPLOG_FILE)
        TraceLog = logger_initialize_rolling(log_name=ROOT_TRACELOG_FILE)

        Log.debug("Testing Log.debug")
        Log.info("Testing Log.info")
        Log.warning("Testing Log.warning")
        Log.error("Testing Log.error")
        Log.critical("Testing Log.critical")
        AppLog.info("Testing AppLog.info")
        TraceLog.info("Testing TraceLog.info")

        print("\nPYLogging Settings:")
        print("\tSTDOUT_LEVEL           =[" + str(STDOUT_LEVEL) + "]")
        print("\tFILELOG_LEVEL          =[" + str(FILELOG_LEVEL) + "]")
        print("\tpylogs_stdout_enabled  =[" + str(pylogs_stdout_enabled) + "]")
        print("\tpylogs_filelog_enabled =[" + str(pylogs_filelog_enabled) + "]")
        print("\tMAX_LOGFILESIZE        =[" + str(MAX_LOGFILESIZE) + "]")
        print("\tMAX_LOGFILECOUNT       =[" + str(MAX_LOGFILECOUNT) + "]")
        print("\n")

        print("**** IITIALIZING LOGS - FINISH ****")
    else:
        print("**** LOGS MODULE: ALREADY LOADED ... IGNORING SUBSEQUENT LOAD CALL ****")
    return

# Ensure log module is initiated
load_loggers()
