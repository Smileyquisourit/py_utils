# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Tests for log messages
# ---------------------------------------------------------
# ./tests/test_Logueur/test_logMessage.py
""" Tests for the log_message module """

import unittest
import datetime
import unittest.mock

from tests import mockDatetime
from py_utils.Logueur.log_message import *

class test_LogMessage(unittest.TestCase):
    """ Tests for the LogMessage class

    We test for the format and the time.
    """

    def test_defaultFmt(self):

        body = "some message's body"
        level = LogLevel(1)
        topic = LogTopic("msg.topic")
        message = LogMessage(body,level,topic)

        good_fmt = "[INFO] msg.topic\nsome message's body\n\n"

        self.assertEqual(good_fmt,str(message))

    def test_goodFmt(self):

        body = "some message's body"
        level = LogLevel(1)
        topic = LogTopic("msg.topic")
        fmt = "({level}) {body}\n"
        message = LogMessage(body,level,topic,fmt=fmt)

        good_fmt = "(INFO) some message's body\n"

        self.assertEqual(good_fmt,str(message))
    
    def test_badFmt(self):

        body = "some message's body"
        level = LogLevel(1)
        topic = LogTopic("msg.topic")
        fmt = "({level}) {topic}\n"

        with self.assertRaises(ValueError):
            LogMessage(body,level,topic,fmt=fmt)

    def test_fmtWithTime(self):

        args = {
            'body'  : "some message's body",
            'level' : LogLevel(1),
            'topic' : LogTopic("msg.topic"),
            'fmt'   : '{date}T{time} :: {body}\n'
        }

        _mockDatetime = mockDatetime(datetime.datetime.now())
        with unittest.mock.patch('datetime.datetime',_mockDatetime) as mock:
            expected = args["fmt"].format(
                date=mock.now().date(), time=mock.now().time(), **args
            )
            msg = LogMessage(**args)
            self.assertEqual(expected, str(msg))

        _mockDatetime = mockDatetime(datetime.datetime.now(datetime.UTC))
        with unittest.mock.patch('datetime.datetime',_mockDatetime) as mock:
            expected = args["fmt"].format(
                date=mock.now().date(), time=mock.now().timetz(), **args
            )
            msg = LogMessage(tz=datetime.UTC,**args)
            self.assertEqual(expected, str(msg))