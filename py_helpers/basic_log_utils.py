import os
import datetime
import time
from pytz import timezone

import logging
import logging.handlers

LOG_FILESIZE = int(1024 * 1024 * 16)
LOG_FILECOUNT = 10

ROOT_LOG_DIR = "./logs/"
ROOT_LOG_FILE = "server.log"
ROOT_APPLOG_FILE = "app.log"
ROOT_APILOG_FILE = 'api.log'


# Setup these objects here to supress link warnings
initialized_logobj = None
Log = None
AppLog = None
ApiLog = None

print("**** LOGS LOGS MODULE ****")

# Debug (10), Info (20), Warning (30), Error (40), Critical (50)


def append_to_log_file(sfile="", smsg=""):
    Log.debug("append_to_log_file: IN sfile=[" + str(sfile) + "] smsg=[" + str(smsg) + "]")
    exitstr = None
    try:
        if sfile is None or sfile == "":
            now = datetime.datatime.now(timezone('Asia/Calcutta'))
            datetime_text = str(now.strftime("%Y_%m_%d_%H_%M_%S"))
            sfile = os.path.join(str(ROOT_LOG_DIR), str(str(datetime_text) + str("_") + str("CertificationReport.log")))
        Log.debug("append_to_log_file: sfile=[" + str(sfile) + "]")
        with open(sfile, 'a') as f:
            now = datetime.datetime.now(timezone('Asia/Calcutta'))
            datetime_text = str(now.strftime("%Y-%m-%d %H:%M:%S"))
            f.write(datetime_text + ": " + smsg + "\n")
        exitstr = sfile
    except Exception as error_msg:
        Log.debug("append_to_log_file: failed error_msg=[" + str(error_msg) + "]")
        exitstr = None
        pass
    return


def logger_initialize(slogname=ROOT_LOG_FILE, sdir=ROOT_LOG_DIR, btoconsole=True,
                      btofile=True, file_level=logging.DEBUG, console_level=logging.INFO):
    
    logger = filehandler = consolehandler = None

    slogpath = os.path.join(str(sdir), str(str(slogname)))
    logformat = logging.Formatter(
            '%(asctime)s - %(levelname)-9s| %(message)-90s [L:%(lineno)-04d M:%(module)-s F:%(funcName)-s]',
            datefmt='%Y-%m-%d %H:%M:%S')

    if logger is None:
        logger = logging.getLogger(str(slogpath))
        logger.setLevel(logging.DEBUG)
    else:
        if filehandler is not None:
            logger.removeHandler(filehandler)
            del filehandler
        if consolehandler is not None:
            logger.removeHandler(consolehandler)
            del consolehandler

    filehandler = consolehandler = None

    # create a file handler if log_file is supplied as parameter
    if btofile:
        if (str(slogpath) is not None) and (len(str(slogpath)) > 0):
            filehandler = logging.FileHandler(str(slogpath), mode='a')
            filehandler.setFormatter(logformat)
            filehandler.setLevel(file_level)
            logger.addHandler(filehandler)

    if btoconsole:
        consolehandler = logging.StreamHandler()
        consolehandler.setFormatter(logformat)
        consolehandler.setLevel(console_level)
        logger.addHandler(consolehandler)

    return logger


if __name__ == "__main__":
    if ('initialized_logobj' not in globals()) or (initialized_logobj is None) or (Log is None) or (AppLog is None) or (ApiLog is None):

        print("**** LOGS LOGS MODULE ****")
        
        initialized_logobj = True
        Log = logger_initialize(slogname=ROOT_LOG_FILE, sdir=ROOT_LOG_DIR, btoconsole=True, btofile=True, file_level=logging.DEBUG, console_level=logging.INFO)
        Log.debug("*** LOADING MODULE = [LOGUTILS] DEBUG ***")
        Log.info("*** LOADING MODULE = [LOGUTILS] INFO ***")
        Log.warning("*** LOADING MODULE = [LOGUTILS] WARNING ***")
        Log.error("*** LOADING MODULE = [LOGUTILS] ERROR ***")
        Log.critical("*** LOADING MODULE = [LOGUTILS] CRITICAL ***")

        AppLog = logger_initialize(slogname=ROOT_APPLOG_FILE, sdir=ROOT_LOG_DIR, btoconsole=True, btofile=True, file_level=logging.DEBUG, console_level=logging.INFO)
        AppLog.debug("*** LOADING MODULE = [LOGUTILS] DEBUG ***")
        AppLog.info("*** LOADING MODULE = [LOGUTILS] INFO ***")
        AppLog.warning("*** LOADING MODULE = [LOGUTILS] WARNING ***")
        AppLog.error("*** LOADING MODULE = [LOGUTILS] ERROR ***")
        AppLog.critical("*** LOADING MODULE = [LOGUTILS] CRITICAL ***")

        slogpath = os.path.join(str(ROOT_LOG_DIR), str(str(ROOT_APILOG_FILE)))
        ApiLog = logging.getLogger(str(slogpath))
        ApiLog.setLevel(logging.DEBUG)
        ApiLog_filehandler = logging.handlers.RotatingFileHandler(slogpath, maxBytes=LOG_FILESIZE, backupCount=LOG_FILECOUNT)
        ApiLog_filehandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-9s (L:%(lineno)-03d M:%(module)-12s) | %(message)-s', datefmt='%Y-%m-%d %H:%M:%S'))
        ApiLog_filehandler.setLevel(logging.DEBUG)
        ApiLog.addHandler(ApiLog_filehandler)
        ApiLog.debug("*** LOADING MODULE = [LOGUTILS] DEBUG ***")
        ApiLog.info("*** LOADING MODULE = [LOGUTILS] INFO ***")
        ApiLog.warning("*** LOADING MODULE = [LOGUTILS] WARNING ***")
        ApiLog.error("*** LOADING MODULE = [LOGUTILS] ERROR ***")
        ApiLog.critical("*** LOADING MODULE = [LOGUTILS] CRITICAL ***")

