# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Test for a log's outputs
# ---------------------------------------------------------
# ./tests/test_Logueur/test_logOut.py
""" Tests for the log_out module 
"""

import io
import unittest

from py_utils.Logueur.log_out import *
from py_utils.Logueur.log_topic import LogTopic as LogTopic

mockVar = False
class MockBaseLogHandler(BaseLogHandler):
    def _write(self,msg:LogMessage):
        """ MockLogHandler._write """
        global mockVar
        mockVar = True


class test_baseLogHandler(unittest.TestCase):
    """ Tests for the BaseLogHandler class

    As this class is an abstract one, we defined the MockBaseLogHandler, enabling the 
    testing on this class. The _write method of this mock class only set a globale variable
    to True.

    We only test briefly the _filtrate and emit message, as they don't have a complicated
    logic and they mostly use functionality tested else where.
    """

    def test_baseFiltrate(self):

        log = MockBaseLogHandler(LogLevel.INFO, "key1")

        msg_good = LogMessage("body",LogLevel.WARNING, LogTopic("key1"))
        msg_bad1 = LogMessage("body",LogLevel.DEBUG, LogTopic("key1"))
        msg_bad2 = LogMessage("body",LogLevel.ERROR, LogTopic("NotKey1"))

        self.assertTrue(log._filtrate(msg_good))
        self.assertFalse(log._filtrate(msg_bad1))
        self.assertFalse(log._filtrate(msg_bad2))
    def test_baseEmit(self):

        # Testing emit by setting the global var to false, and checking if it
        # was modified to True (when the msg is emitted) or untouched (when the
        # msg isn't emited)

        global mockVar

        log = MockBaseLogHandler(LogLevel.INFO, "key1")

        msg_good = LogMessage("body",LogLevel.WARNING, LogTopic("key1"))
        msg_bad1 = LogMessage("body",LogLevel.DEBUG, LogTopic("key1"))
        msg_bad2 = LogMessage("body",LogLevel.ERROR, LogTopic("NotKey1"))
        
        mockVar = False; log.emit(msg_good)
        self.assertTrue(mockVar)

        mockVar = False; log.emit(msg_bad1)
        self.assertFalse(mockVar)

        mockVar = False; log.emit(msg_bad2)
        self.assertFalse(mockVar)

class test_logConsoleHandler(unittest.TestCase):
    """ Tests for the LogConsoleHandler class

    As this class herits from the BaseLogHandler one, there is only two
    functinality to be aspect of the class to be tested: the constructor
    and the _write method.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.debug_msg = LogMessage("debug message",LogLevel.DEBUG,LogTopic("topic"),fmt='{body}\n')
        cls.info_msg = LogMessage("info message",LogLevel.INFO,LogTopic("topic"),fmt='{body}\n')
        cls.warning_msg = LogMessage("warning message",LogLevel.WARNING,LogTopic("topic"),fmt='{body}\n')
        cls.error_msg = LogMessage("error message",LogLevel.ERROR,LogTopic("topic"),fmt='{body}\n')
        cls.fatal_msg = LogMessage("fatal message",LogLevel.FATAL,LogTopic("topic"),fmt='{body}\n')
        return super().setUpClass()

    def setUp(self) -> None:
        self.mockStdout = io.StringIO()
        self.mockStdErr = io.StringIO()
        sys.stdout = self.mockStdout
        sys.stderr = self.mockStdErr
        
    def tearDown(self) -> None:
        self.mockStdout.close()
        self.mockStdErr.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    # With or whitout color:
    def test_uniqueOutput(self):
        """ test without differencing between stdout and stderr, and without color """
        log = ConsoleLogHandler(LogLevel.DEBUG,LogTopicFilter("#"),supportColor=False,useStderr=False)

        log._write(self.debug_msg)
        log._write(self.info_msg)
        log._write(self.warning_msg)
        log._write(self.error_msg)
        log._write(self.fatal_msg)

        expected_stdout = "debug message\ninfo message\nwarning message\nerror message\nfatal message\n"
        expected_stderr = ""

        self.assertEqual(self.mockStdout.getvalue(),expected_stdout)
        self.assertEqual(self.mockStdErr.getvalue(),expected_stderr)
    def test_uniqueOutputWithColor(self):
        """ test without differencing between stdout and stderr, and with color """
        log = ConsoleLogHandler(LogLevel.DEBUG,LogTopicFilter("#"),supportColor=True,useStderr=False)

        log._write(self.debug_msg)
        log._write(self.info_msg)
        log._write(self.warning_msg)
        log._write(self.error_msg)
        log._write(self.fatal_msg)

        expected_stdout = \
            f"{ConsoleLogHandler._FG_COLORS['DEBUG']}debug message\n{ConsoleLogHandler._FG_RS}" + \
            f"{ConsoleLogHandler._FG_COLORS['INFO']}info message\n{ConsoleLogHandler._FG_RS}" + \
            f"{ConsoleLogHandler._FG_COLORS['WARNING']}warning message\n{ConsoleLogHandler._FG_RS}" + \
            f"{ConsoleLogHandler._FG_COLORS['ERROR']}error message\n{ConsoleLogHandler._FG_RS}" + \
            f"{ConsoleLogHandler._FG_COLORS['FATAL']}fatal message\n{ConsoleLogHandler._FG_RS}"
        expected_stderr = ""

        self.assertEqual(self.mockStdout.getvalue(),expected_stdout)
        self.assertEqual(self.mockStdErr.getvalue(),expected_stderr)

    # stdout and stderr:
    def test_multipleOutput(self):
        """ Test stdout and stderr, without color """
        log = ConsoleLogHandler(LogLevel.DEBUG,LogTopicFilter("#"),supportColor=False,useStderr=True)

        log._write(self.debug_msg)
        log._write(self.info_msg)
        log._write(self.warning_msg)
        log._write(self.error_msg)
        log._write(self.fatal_msg)

        expected_stdout = "debug message\ninfo message\n"
        expected_stderr = "warning message\nerror message\nfatal message\n"

        self.assertEqual(self.mockStdout.getvalue(),expected_stdout)
        self.assertEqual(self.mockStdErr.getvalue(),expected_stderr)
    def test_multipleOutputWithColor(self):
        """ Test stdout and stderr, with color """
        log = ConsoleLogHandler(LogLevel.DEBUG,LogTopicFilter("#"),supportColor=True,useStderr=True)

        log._write(self.debug_msg)
        log._write(self.info_msg)
        log._write(self.warning_msg)
        log._write(self.error_msg)
        log._write(self.fatal_msg)

        expected_stdout = \
            f"{ConsoleLogHandler._FG_COLORS['DEBUG']}debug message\n{ConsoleLogHandler._FG_RS}" + \
            f"{ConsoleLogHandler._FG_COLORS['INFO']}info message\n{ConsoleLogHandler._FG_RS}"
        expected_stderr = \
            f"{ConsoleLogHandler._FG_COLORS['WARNING']}warning message\n{ConsoleLogHandler._FG_RS}" + \
            f"{ConsoleLogHandler._FG_COLORS['ERROR']}error message\n{ConsoleLogHandler._FG_RS}" + \
            f"{ConsoleLogHandler._FG_COLORS['FATAL']}fatal message\n{ConsoleLogHandler._FG_RS}"

        self.assertEqual(self.mockStdout.getvalue(),expected_stdout)
        self.assertEqual(self.mockStdErr.getvalue(),expected_stderr)

class test_FileLogHandler(unittest.TestCase):
    """ Tests for the LogFileHandler class
    """

class test_RotaryFileLogHandler(unittest.TestCase): #TODO
    """ Tests for the RotaryFileLogHandler class
    """
    log = RotaryFileLogHandler()