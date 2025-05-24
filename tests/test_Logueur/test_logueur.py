# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Test for the logueur
# ---------------------------------------------------------
# ./tests/test_Logueur/test_logueur.py
""" Tests for the logueur module 
"""

import unittest
from unittest import mock
import unittest.mock

import io
import datetime

from py_utils.Logueur.logueur import *
from py_utils.Logueur.log_out import BaseLogHandler
from tests import mockDatetime

# Helpers classes
class DummyHanlder(BaseLogHandler):
    """ A dummy handler that log the messages to a attribut. """
    def __init__(self, level, filter):
        super().__init__(level, filter)
        self.logs: str = ""
        self._logs: list[LogMessage] = list()

    def _write(self, msg):
        self.logs += str(msg)
        self._logs.append(msg)

    def clear(self):
        self.logs = ""

class test_Logueur(unittest.TestCase):

    def setUp(self):
        Logueur._instance = None
        return super().setUp()
    def tearDown(self):
        Logueur._instance = None
        return super().tearDown()

    # Test constructor
    def test_nominalConstructor_oneHandler(self):
        
        handler = DummyHanlder(LogLevel.DEBUG, LogTopicFilter("#"))
        log = Logueur(handler)

        self.assertEqual([handler], log._out)
        
        #
    def test_nominalConstructor_multipleHandlers(self):

        hanlder = [
            DummyHanlder(LogLevel.DEBUG, LogTopicFilter("#")),
            DummyHanlder(LogLevel.DEBUG, LogTopicFilter("#")),
            DummyHanlder(LogLevel.DEBUG, LogTopicFilter("#"))
        ]
        log = Logueur(hanlder)
        
        self.assertEqual(hanlder, log._out)

        #
    def test_errorConstructor_topicGenerationMethod(self):

        handler = DummyHanlder(LogLevel.DEBUG, LogTopicFilter("#"))
        
        with self.assertRaises(ValueError):
            log = Logueur(handler,'not_a_method')
        
        #
    def test_errorConstructor_msgFmt(self):

        handler = DummyHanlder(LogLevel.DEBUG, LogTopicFilter("#"))
        
        with self.assertRaises(ValueError):
            log = Logueur(handler,messageFormat="format")

    # Singleton pattern
    def test_singletonPattern(self):
        handler1 = DummyHanlder(LogLevel.DEBUG, LogTopicFilter("#"))
        handler2 = DummyHanlder(LogLevel.DEBUG, LogTopicFilter("#"))

        log1 = Logueur(handler1)
        log2 = Logueur(handler2)

        self.assertIs(log1,log2)
        self.assertIs(log1._out, log2._out)
        #TODO: implement the Singeton metaclass!!
        #self.assertEqual([handler1], log1._out, "The first log was errased by the second!!")

        # We should add a test with register_output that check that calling Logueur() a second
        # time doesn't change the _out (like the TODO)

    # Logging func
    def test_defaultLogging(self):
        log = Logueur.get_loggingFunc()

        with unittest.mock.patch('sys.stderr', io.StringIO()) as mockSTDERR:
            log("ERROR", "body","topic")
            self.assertEqual("[ERROR] topic :: body\n",mockSTDERR.getvalue())
        
        #
    def test_correctRedirectingOfTheDefaultLog(self):

        handler = DummyHanlder(LogLevel.INFO, LogTopicFilter('#'))
        logueur = Logueur(handler, messageFormat='[{level}] {topic} :: {body}\n')
        log = Logueur.get_loggingFunc()

        with unittest.mock.patch('sys.stderr', io.StringIO()) as mockSTDERR:
            log("INFO","body","topic")
            self.assertEqual("",mockSTDERR.getvalue())
        self.assertEqual("[INFO] topic :: body\n",handler.logs)

    # log class method
    def test_log_classMethod(self):

        handler = DummyHanlder(LogLevel.DEBUG,LogTopicFilter("#"))
        log = Logueur(handler)

        msg = LogMessage(
            "body",LogLevel.INFO, LogTopic("topic"),
            fmt="[{level}] {topic} :: {body}"
        )
        log.log(msg)

        self.assertEqual("[INFO] topic :: body", handler.logs)


    # loging functions (debug, info, ...)
    def test_loggingFunc_allProvided(self):
        # We create a dummy handler with debug level and '#' as a topic
        # filter to catch all messages, and check that the the messages
        # are correctly constructed (without tzinfo)

        handler = DummyHanlder(LogLevel.DEBUG,LogTopicFilter("#"))
        log = Logueur(handler)

        args = ("body","topic")
        kwargs = {"format":"{body}"}

        mockDT = mockDatetime(datetime.datetime.now()) 
        with unittest.mock.patch('datetime.datetime',mockDT) as mocked:

            # Debug
            log.debug(*args,**kwargs)
            self.assertEqual("body",        handler._logs[-1].body,     "Incorrect body for func debug")
            self.assertEqual(LogLevel.DEBUG,handler._logs[-1].level,    "Incorrect level for func debug")
            self.assertEqual("topic",       handler._logs[-1].topic,    "Incorrect topic for func debug")
            self.assertEqual("{body}",      handler._logs[-1].msg_fmt,  "Incorrect fmt for func debug")
            self.assertEqual(mocked.now(),  handler._logs[-1].datetime, "Incorrect datetime for func debug")

            # Info
            log.info(*args,**kwargs)
            self.assertEqual("body",        handler._logs[-1].body,     "Incorrect body for func info")
            self.assertEqual(LogLevel.INFO, handler._logs[-1].level,    "Incorrect level for func info")
            self.assertEqual("topic",       handler._logs[-1].topic,    "Incorrect topic for func info")
            self.assertEqual("{body}",      handler._logs[-1].msg_fmt,  "Incorrect fmt for func info")
            self.assertEqual(mocked.now(),  handler._logs[-1].datetime, "Incorrect datetime for func info")
            
            # Warning
            log.warning(*args,**kwargs)
            self.assertEqual("body",          handler._logs[-1].body,     "Incorrect body for func warning")
            self.assertEqual(LogLevel.WARNING,handler._logs[-1].level,    "Incorrect level for func warning")
            self.assertEqual("topic",         handler._logs[-1].topic,    "Incorrect topic for func warning")
            self.assertEqual("{body}",        handler._logs[-1].msg_fmt,  "Incorrect fmt for func warning")
            self.assertEqual(mocked.now(),    handler._logs[-1].datetime, "Incorrect datetime for func warning")
            
            # Error
            log.error(*args,**kwargs)
            self.assertEqual("body",        handler._logs[-1].body,     "Incorrect body for func error")
            self.assertEqual(LogLevel.ERROR,handler._logs[-1].level,    "Incorrect level for func error")
            self.assertEqual("topic",       handler._logs[-1].topic,    "Incorrect topic for func error")
            self.assertEqual("{body}",      handler._logs[-1].msg_fmt,  "Incorrect fmt for func error")
            self.assertEqual(mocked.now(),  handler._logs[-1].datetime, "Incorrect datetime for func error")

            # Fatal
            log.fatal(*args,**kwargs)
            self.assertEqual("body",        handler._logs[-1].body,     "Incorrect body for func fatal")
            self.assertEqual(LogLevel.FATAL,handler._logs[-1].level,    "Incorrect level for func fatal")
            self.assertEqual("topic",       handler._logs[-1].topic,    "Incorrect topic for func fatal")
            self.assertEqual("{body}",      handler._logs[-1].msg_fmt,  "Incorrect fmt for func fatal")
            self.assertEqual(mocked.now(),  handler._logs[-1].datetime, "Incorrect datetime for func fatal")
            

        #
    def test_loggingFunc_withTZ(self):
        # We create a dummy handler with debug level and '#' as a topic
        # filter to catch all messages, and check that the the messages
        # are correctly constructed (with tzinfo)
        
        handler = DummyHanlder(LogLevel.DEBUG,LogTopicFilter("#"))
        log = Logueur(handler,tz=datetime.UTC)

        args = ("body","topic")
        kwargs = {"format":"{body}"}

        mockDT = mockDatetime(datetime.datetime.now(datetime.UTC)) 
        with unittest.mock.patch('datetime.datetime',mockDT) as mocked:

            # Debug
            log.debug(*args,**kwargs)
            self.assertEqual(mocked.now(),  handler._logs[-1].datetime, "Incorrect datetime for func debug")

            # Info
            log.info(*args,**kwargs)
            self.assertEqual(mocked.now(),  handler._logs[-1].datetime, "Incorrect datetime for func info")
            
            # Warning
            log.warning(*args,**kwargs)
            self.assertEqual(mocked.now(),    handler._logs[-1].datetime, "Incorrect datetime for func warning")
            
            # Error
            log.error(*args,**kwargs)
            self.assertEqual(mocked.now(),  handler._logs[-1].datetime, "Incorrect datetime for func error")

            # Fatal
            log.fatal(*args,**kwargs)
            self.assertEqual(mocked.now(),  handler._logs[-1].datetime, "Incorrect datetime for func fatal")
        
        #
    def test_loggingFunc_withTopicGen(self):
        # We test that the topic generation method specified in the
        # logueur is used (by mocking the factory function to always
        # return LogTopic('topic'))
        
        
        handler = DummyHanlder(LogLevel.DEBUG,LogTopicFilter("#"))
        log = Logueur(handler,tz=datetime.UTC)

        mockDT = mockDatetime(datetime.datetime.now(datetime.UTC))
        def mockTopicFactory(*args,**kwargs):
            return LogTopic("_topic_")
        with unittest.mock.patch('datetime.datetime',mockDT) as mocked:
            with unittest.mock.patch('py_utils.Logueur.log_topic.LogTopic.topicFactory',mockTopicFactory):
                # Debug
                log.debug("body",format="{body}")
                self.assertEqual("_topic_",  handler._logs[-1].topic, "Incorrect topic for func debug")

                # Info
                log.info("body",format="{body}")
                self.assertEqual("_topic_",  handler._logs[-1].topic, "Incorrect topic for func info")

                # Warning
                log.warning("body",format="{body}")
                self.assertEqual("_topic_",  handler._logs[-1].topic, "Incorrect topic for func warning")

                # Error
                log.error("body",format="{body}")
                self.assertEqual("_topic_",  handler._logs[-1].topic, "Incorrect topic for func error")

                # Fatal
                log.fatal("body",format="{body}")
                self.assertEqual("_topic_",  handler._logs[-1].topic, "Incorrect topic for func fatal")

        #
    def test_loggingFunc_withFormat(self):
        # We test for the formatting functionality when
        # the format is passed to the logueur
        
        handler = DummyHanlder(LogLevel.DEBUG,LogTopicFilter("#"))
        log = Logueur(handler,tz=datetime.UTC,messageFormat="{body}")

        # Debug
        log.debug("body")
        self.assertEqual("{body}", handler._logs[-1].msg_fmt, "Incorrect fmt for func debug")

        # Info
        log.info("body")
        self.assertEqual("{body}", handler._logs[-1].msg_fmt, "Incorrect fmt for func info")
        
        # Warning
        log.warning("body")
        self.assertEqual("{body}", handler._logs[-1].msg_fmt, "Incorrect fmt for func warning")
        
        # Error
        log.error("body")
        self.assertEqual("{body}", handler._logs[-1].msg_fmt, "Incorrect fmt for func error")

        # Fatal
        log.fatal("body")
        self.assertEqual("{body}", handler._logs[-1].msg_fmt, "Incorrect fmt for func fatal")

    def test_register(self):

        # All handlers:
        handlers = [
            DummyHanlder(LogLevel.DEBUG, LogTopicFilter("#")),
            DummyHanlder(LogLevel.DEBUG, LogTopicFilter("#")),
            DummyHanlder(LogLevel.DEBUG, LogTopicFilter("#")),
            DummyHanlder(LogLevel.DEBUG, LogTopicFilter("#"))
        ]

        # Initial log
        log = Logueur(handlers[0])
        self.assertEqual(1,len(log._out))
        
        # Register 1 handler
        log.register_output(handlers[1])
        self.assertEqual(handlers[0:2],log._out)

        # Register multiple handler:
        log.register_output(handlers[2:])
        self.assertEqual(handlers,log._out)


class test_ConsoleLogueurFactory(unittest.TestCase):
    def test_nominal(self):
        log = ConsoleLogueurFactory(
            LogLevel.DEBUG,
            LogTopicFilter("filter"),
            supportColor=False,
            useStderr=False
        )

        self.assertEqual(1,len(log._out))
        self.assertEqual(LogLevel.DEBUG,log._out[0].level)
        self.assertEqual(LogTopicFilter("filter"),log._out[0].filter)
        self.assertFalse(log._out[0]._supportColor)
        self.assertFalse(log._out[0]._useStderr)