# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Tests for log messages
# ---------------------------------------------------------
# ./tests/test_Logueur/test_logMessage.py
""" Tests for the log_message module """

import unittest

from Logueur.log_message import *

class test_LogMessage(unittest.TestCase):
    """ Tests for the LogMessage class

    The only functionality to be tested of the LogMessage
    class is it's formatting functionality.
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