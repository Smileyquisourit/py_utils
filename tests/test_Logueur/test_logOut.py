# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Test for a log's outputs
# ---------------------------------------------------------
# ./tests/test_Logueur/test_logOut.py
""" Tests for the log_out module 
"""

import io
import datetime
import unittest
import unittest.mock

import os
import shutil
import tempfile

from py_utils.Logueur.log_out import *
from py_utils.Logueur.log_topic import LogTopic as LogTopic

from tests import mockDatetime

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

        log = MockBaseLogHandler(LogLevel.INFO, LogTopicFilter("key1"))

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

        log = MockBaseLogHandler(LogLevel.INFO, LogTopicFilter("key1"))

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

    @classmethod
    def setUpClass(cls):
        cls._test_dir = tempfile.mkdtemp()
        return super().setUpClass()
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._test_dir)
        return super().tearDownClass()

    def tearDown(self):
        shutil.rmtree(self._test_dir)
        os.mkdir(self._test_dir,mode=0o700)
    
    def _create_file(self,filename):

        path = os.path.join(self._test_dir,filename)
        with open(path,"w"):
            pass

        return path

    def test_generateFilename(self):
        """ Testing FileLogHandler._generateLogFilename """
        mockDT = mockDatetime(datetime.datetime.now(datetime.UTC))
        with unittest.mock.patch('datetime.datetime',mockDT) as mock:
            expected = "log_"+mock.now().isoformat()
            self.assertEqual(expected,FileLogHandler._generateLogFilename())
        
        #
    def test_makeValdeFileName(self):
        """ Testing FileLogHandler._makeValideFilename """
        
        file1 = self._create_file("log.log")
        file2 = self._create_file("log_1.log")
        file3 = self._create_file("log_2.log")

        # Valid file
        expected = os.path.join(self._test_dir,'logfile')
        self.assertEqual(expected, FileLogHandler._makeValideFilename(expected))

        # Invalid file, need one iteration
        file4 = self._create_file('logfile')
        expected = os.path.join(self._test_dir,'logfile_1')
        self.assertEqual(expected, FileLogHandler._makeValideFilename(file4))

        # Invalid file, need multiple iteration
        expected = os.path.join(self._test_dir,'log_3.log')
        self.assertEqual(expected, FileLogHandler._makeValideFilename(file1))

    def test_write(self):
        """ Testing FileLogHandler._write """

        filename = self._create_file('logfile')
        log = FileLogHandler(
            LogLevel.DEBUG,LogTopicFilter("#"),
            filename=filename, action="append"
        )
        msg = LogMessage("body",LogLevel.INFO,LogTopic('topic'),fmt="{body}")

        log._write(msg)

        expected = "body"
        with open(filename,'r') as f:
            tested = f.read()
        self.assertEqual(expected,tested, f"Should have read '{expected}', but I've read '{tested}'")

    def test_optionOverwrite(self):
        
        filename = self._create_file('logfile')
        with open(filename, 'w') as f:
            f.write("something")
            
        expected = ""
        log = FileLogHandler(LogLevel.DEBUG,LogTopicFilter("#"),filename=filename, action="overwrite")
        with open(filename,'r') as f:
            tested = f.read()
            self.assertEqual(expected, tested, f"I should have read '{expected}', but I've read '{tested}'")

        #
    def test_optionVerwriteWarn(self):

        filename = self._create_file('logfile')
        with open(filename, 'w') as f:
            f.write("something")
            
        expected = ""
        with self.assertWarns(ResourceWarning) as cm:
            log = FileLogHandler(LogLevel.DEBUG,LogTopicFilter("#"),filename=filename, action="overwrite-warn")
        with open(filename,'r') as f:
            tested = f.read()
            self.assertEqual(expected, tested, f"I should have read '{expected}', but I've read '{tested}'")

        #
    def test_optionAbort(self):

        filename = self._create_file('logfile')
        with open(filename, 'w') as f:
            f.write("something")
            
        with self.assertRaises(FileExistsError):
            log = FileLogHandler(LogLevel.DEBUG,LogTopicFilter("#"),filename=filename, action="abort")
        
        #
    def test_optionAppend(self):
        
        filename = self._create_file('logfile')
        with open(filename, 'w') as f:
            f.write("some")
        msg = LogMessage("thing",LogLevel.INFO,LogTopic('topic'),fmt="{body}")
            
        expected = "something"
        log = FileLogHandler(LogLevel.DEBUG,LogTopicFilter("#"),filename=filename, action="append")
        log._write(msg)
        with open(filename,'r') as f:
            tested = f.read()
            self.assertEqual(expected, tested, f"I should have read '{expected}', but I've read '{tested}'")

        #
    def test_optionNew(self):
        
        filename = self._create_file('logfile')
        expected = filename + "_1"

        log = FileLogHandler(LogLevel.DEBUG,LogTopicFilter("#"),filename=filename, action="new")
        self.assertEqual(expected, log._filename)

class test_RotaryFileLogHandler(unittest.TestCase):
    """ Tests for the RotaryFileLogHandler class
    """

    @classmethod
    def setUpClass(cls):
        cls._test_dir = tempfile.mkdtemp()
        return super().setUpClass()
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._test_dir)
        return super().tearDownClass()

    def tearDown(self):
        shutil.rmtree(self._test_dir)
        os.mkdir(self._test_dir,mode=0o700)
        pass

    @staticmethod
    def _getFilename(dt:datetime.datetime,base:str,sep:str,ext:str):
        filename = base
        filename += dt.date().isoformat()
        filename += sep
        filename += dt.timetz().isoformat()
        filename += ext
        return filename

        #
    def _getLog(self, **kwargs):
        args = {
            'level'       : LogLevel.INFO,
            'filter'      : LogTopicFilter("#"),
            'baseFilename': "logfile_",
            'directory'   : self._test_dir,
            'log_ext'     : ".log",
            'timeSep'     : 'T',
            'tz'          : datetime.UTC,
            'maxSizeFile' : 1024,
            'maxLog'      : 3,
            'maxLogUnit'  : 'file'
        }
        args.update(kwargs)
        return RotaryFileLogHandler(**args)
    def _createFile(self,filename):
        path = os.path.join(self._test_dir,filename)
        with open(path,'w') as f:
            pass
        return os.path.abspath(path)

    # Test init dir
    def test_existingDir(self):
        try:
            log = self._getLog()
        except FileNotFoundError:
            self.fail(f"RotaryFileHandler didn't find the exisitng directory!")
        
        #
    def test_newDir(self):
        # create the new dir in self._test_dir to be sure it will be removed
        # after.
        new_dir = os.path.join(self._test_dir, "new_log_dir") 
        try:
            log = self._getLog(directory=new_dir)
        except FileNotFoundError:
            self.fail(f"RotaryFileHandler didn't find the existing parent drectory!")
        
        if not os.path.isdir(new_dir):
            self.fail(f"RotaryFileHanlder didn't create the log's directory!")
        
        #
    def test_noParentDir(self):
        # create the new dir in self._test_dir to be sure it will be removed
        # after.
        new_dir = os.path.join(self._test_dir, "new_parent_dir", "new_log_dir") 
        with self.assertRaises(FileNotFoundError):
            log = self._getLog(directory=new_dir)

    # Test logfiles property
    def test_reconstruct_time(self):
        # Test for each options (base, datetimeSep,ext) separatly. This should be
        # enough, with an uncorrect filename for each case.

        dt = datetime.datetime.now(datetime.UTC)

        # Test base
        good_filename = self._getFilename(dt,'logfile_','T','.log')
        bad_filename = self._getFilename(dt,'log-','T','.log')
        log = self._getLog()

        try:
            tested = log._reconstruct_time_from_filename(good_filename)
        except:
            self.fail(
                f"RotaryFileHandler didn't recognize the correct pattern in '{good_filename}'" + \
                f" (pattern was '{log._filename_pattern.pattern}')"
            )
        self.assertEqual(dt,tested)
        with self.assertRaises(ValueError):
            log._reconstruct_time_from_filename(bad_filename)


        # Test datetimeSep
        good_filename = self._getFilename(dt,'logfile_','::','.log')
        bad_filename = self._getFilename(dt,'logfile_','T','.log')
        log = self._getLog(timeSep='::')

        try:
            tested = log._reconstruct_time_from_filename(good_filename)
        except:
            self.fail(
                f"RotaryFileHandler didn't recognize the correct pattern in '{good_filename}'" + \
                f" (pattern was '{log._filename_pattern.pattern}')"
            )
        self.assertEqual(dt,log._reconstruct_time_from_filename(good_filename))
        with self.assertRaises(ValueError):
            log._reconstruct_time_from_filename(bad_filename)

        # Test ext
        good_filename = self._getFilename(dt,'logfile_','T','.log')
        bad_filename = self._getFilename(dt,'logfile_','T','')
        log = self._getLog()

        try:
            tested = log._reconstruct_time_from_filename(good_filename)
        except:
            self.fail(
                f"RotaryFileHandler didn't recognize the correct pattern in '{good_filename}'" + \
                f" (pattern was '{log._filename_pattern.pattern}')"
            )
        self.assertEqual(dt,log._reconstruct_time_from_filename(good_filename))
        with self.assertRaises(ValueError):
            log._reconstruct_time_from_filename(bad_filename)

        #
    def test_zeroLogfiles(self):

        log = self._getLog()

        self.assertEqual(0,len(log))
        #
    def test_multipleLogfiles(self):

        # Create 3 datetime for 3 differents files
        now = datetime.datetime.now(datetime.UTC)
        dt = [
            now - datetime.timedelta(weeks=0,days=1,hours=3,minutes=45,seconds=28,milliseconds=5),
            now - datetime.timedelta(weeks=0,days=4,hours=14,minutes=0,seconds=55,milliseconds=9),
            now - datetime.timedelta(weeks=1,days=0,hours=23,minutes=59,seconds=59,milliseconds=0)
        ]

        # Creates 3 files
        files = [
            self._createFile(self._getFilename(dt[0],'logfile_','T','.log')),
            self._createFile(self._getFilename(dt[1],'logfile_','T','.log')),
            self._createFile(self._getFilename(dt[2],'log','T','.log')),
        ]

        log = self._getLog()

        # Assert than only 2 files are found
        self.assertEqual(2,len(log))

        # Assert that the files are correctly determined
        for file in log.logfiles:
            self.assertIn(file.path,files)
            self.assertIn(file.creationTime,dt)

        # Assert that logfiles are sorted
        for ii in range(1,len(log.logfiles)):
            self.assertTrue( log.logfiles[ii].creationTime >= log.logfiles[ii-1].creationTime )

    # Test logfiles cleanup
    def test_cleanup_num(self):
        
        # Create 3 datetime for 3 differents files
        now = datetime.datetime.now(datetime.UTC)
        dt = [
            now - datetime.timedelta(weeks=0,days=1,hours=3,minutes=45,seconds=28,milliseconds=5),
            now - datetime.timedelta(weeks=0,days=4,hours=14,minutes=0,seconds=55,milliseconds=9),
            now - datetime.timedelta(weeks=1,days=0,hours=23,minutes=59,seconds=59,milliseconds=0)
        ]

        # Creates 3 files
        files = [
            self._createFile(self._getFilename(dt[0],'logfile_','T','.log')),
            self._createFile(self._getFilename(dt[1],'logfile_','T','.log')),
            self._createFile(self._getFilename(dt[2],'logfile_','T','.log')),
        ]

        log = self._getLog(maxLog=2)
        self.assertEqual(len(log),2)
    
        #
    def test_cleanup_date(self):

        # Create 3 datetime for 3 differents files
        now = datetime.datetime.now(datetime.UTC)
        dt = [
            now - datetime.timedelta(weeks=0,days=1,hours=3,minutes=45,seconds=28,milliseconds=5),
            now - datetime.timedelta(weeks=0,days=4,hours=14,minutes=0,seconds=55,milliseconds=9),
            now - datetime.timedelta(weeks=1,days=0,hours=23,minutes=59,seconds=59,milliseconds=0)
        ]

        # Creates 3 files
        files = [
            self._createFile(self._getFilename(dt[0],'logfile_','T','.log')),
            self._createFile(self._getFilename(dt[1],'logfile_','T','.log')),
            self._createFile(self._getFilename(dt[2],'logfile_','T','.log')),
        ]

        log = self._getLog(maxLog=2,maxLogUnit='day')
        self.assertEqual(len(log),1)
        self.assertEqual(dt[0], log.logfiles[0].creationTime)

    # Test initialisation of logfiles
    def test_init_zero_logfiles(self):
        # Test avec 0 log files. This is more the sketch of the different
        # tests that shoud be writtent when there is a customisation of the
        # behavior of the _init_logfiles function by the user.
        log = self._getLog()
        self.assertEqual(0,len(log))


        # Create the file
        now = datetime.datetime.now(datetime.UTC)
        dt = now - datetime.timedelta(weeks=1,days=0,hours=23,minutes=59,seconds=59,milliseconds=0)
        self._createFile(self._getFilename(dt,'logfile_','T','.log'))

        log = self._getLog(maxLog=1,maxLogUnit='week')
        self.assertEqual(0,len(log))

        #
    def test_init_multiple_logfiles(self):
        # Test avec multiple log files, with something writen
        # in the last ?

        # Create 3 datetime for 3 differents files
        now = datetime.datetime.now(datetime.UTC)
        dt = [
            now - datetime.timedelta(weeks=0,days=1,hours=3,minutes=45,seconds=28,milliseconds=5),
            now - datetime.timedelta(weeks=0,days=4,hours=14,minutes=0,seconds=55,milliseconds=9),
            now - datetime.timedelta(weeks=1,days=0,hours=23,minutes=59,seconds=59,milliseconds=0)
        ]

        # Creates 3 files
        files = [
            self._createFile(self._getFilename(dt[0],'logfile_','T','.log')),
            self._createFile(self._getFilename(dt[1],'logfile_','T','.log')),
            self._createFile(self._getFilename(dt[2],'logfile_','T','.log')),
        ]

        # Write something to the newest file
        with open(files[0],"w") as f:
            f.write("some")

        log = self._getLog(maxLog=2,maxLogUnit='file')
        log._write(LogMessage("thing",LogLevel.DEBUG,LogTopic("topic"),"{body}"))

        with open(files[0],'r') as f:
            self.assertEqual('something',f.read())