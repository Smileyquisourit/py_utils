# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Test for a log's outputs
# ---------------------------------------------------------
# ./tests/test_Logueur/test_logOut.py
""" Tests for the log_out module """

import io
import unittest

from Logueur.log_out import *
from Logueur.log_topic import LogTopic as LogTopic

mockVar = False
class MockBaseLogHandler(BaseLogHandler):
    def _write(self,msg:LogMessage):
        global mockVar
        mockVar = True


class test_baseLogHandler(unittest.TestCase):
    """ Tests for the BaseLogHandler class

    As this class is an abstract one, we defined the
    MockBaseLogHandler, enabling the testing on this class.

    We test each method separalty, excepted for the _write
    method. The emit method is tested with the _write of the
    MockBaseLogHandler _write method, which set a global variable
    to True if the message is writted or not.
    """
    
    def setUp(self):

        level = LogLevel.INFO
        filter = LogTopicFilter("key1")
        self.log = MockBaseLogHandler(level,filter)

        self.message_good = LogMessage("A msg body",LogLevel.WARNING,LogTopic("key1"))
        self.message_bad1 = LogMessage("A msg body",LogLevel.WARNING,LogTopic("key2"))
        self.message_bad2 = LogMessage("A msg body",LogLevel.DEBUG,LogTopic("key1"))
        self.message_bad3 = LogMessage("A msg body",LogLevel.DEBUG,LogTopic("key2"))

    def test_baseFiltrate(self):

        self.assertTrue(self.log._filtrate(self.message_good))
        self.assertFalse(self.log._filtrate(self.message_bad1))
        self.assertFalse(self.log._filtrate(self.message_bad2))
        self.assertFalse(self.log._filtrate(self.message_bad3))
    def test_baseEmit(self):

        global mockVar
        
        mockVar = False; self.log.emit(self.message_good)
        self.assertTrue(mockVar)

        mockVar = False; self.log.emit(self.message_bad1)
        self.assertFalse(mockVar)

        mockVar = False; self.log.emit(self.message_bad2)
        self.assertFalse(mockVar)

        mockVar = False; self.log.emit(self.message_bad3)
        self.assertFalse(mockVar)

class test_logConsoleHandler(unittest.TestCase):
    """ Tests for the LogConsoleHandler class

    As this class herits from the BaseLogHandler one,
    we only test here the _write method, by capturing the
    output of the console.
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

class test_logFileHandler(unittest.TestCase): #TODO
    """ Tests for the LogFileHandler class
    """