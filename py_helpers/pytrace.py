#from common_includes import *
#
# pip install icecream
# https://github.com/gruns/icecream
#
import os
from refactor_old.pylogging import TraceLog


# global settings vars
pytrace_initialized = None
pytrace_stdout_enabled = (str(os.getenv('PYTRACE_STDOUT_ENABLED', 'No')) == 'Yes')
pytrace_logging_enabled = (str(os.getenv('PYTRACE_FILELOG_ENABLED', 'No')) == 'Yes')
pytrace_abspath_enabled = (str(os.getenv('PYTRACE_ABSPATH_ENABLED', 'No')) == 'Yes')


def save_trace_to_log(message):
	if pytrace_stdout_enabled: print(message, flush=True)
	if pytrace_logging_enabled: TraceLog.info(message)
	return


def install_trace():
	global pytrace_initialized
	if (pytrace_initialized is None):
		try:
			from icecream import ic
			from icecream import install
			install()
			ic.configureOutput(includeContext=True)
			ic.configureOutput(contextAbsPath=pytrace_abspath_enabled)
			ic.configureOutput(prefix='TRACE :> ')
			ic.configureOutput(outputFunction=save_trace_to_log)
			if pytrace_stdout_enabled:
				ic.enable()
			else:
				ic.disable()
		except ImportError:  # Graceful fallback if IceCream isn't installed. Important for production environments.
			# print("IMPORT Exception: ic module not installed - enabling a no op lambda fuction instead of ic to dummy it up.")
			ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa
		pytrace_initialized = True
		print("\nPYTrace Settings:")
		print("\tpytrace_initialized     =[" + str(pytrace_initialized) + "]")
		print("\tpytrace_stdout_enabled  =[" + str(pytrace_stdout_enabled) + "]")
		print("\tpytrace_logging_enabled =[" + str(pytrace_logging_enabled) + "]")
		print("\tpytrace_abspath_enabled =[" + str(pytrace_abspath_enabled) + "]")
		print("\n")
	return
