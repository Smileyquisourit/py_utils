# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Test for log messages' topic and topic filter
# ---------------------------------------------------------
# ./tests/test_Logueur/test_logTopic.py
""" Tests for the log_topic module """

import unittest

from Logueur.log_topic import *
from Logueur.log_topic import _generateFromModule
from Logueur.log_topic import _generateFromStack

class test_func(unittest.TestCase):
    """ Tests for the different function of the log_topic module.

    The functions tested here are:
    - _generateFromStack
    - _generateFromModule
    """
    correct_stack = "run.__call__.run.__call__.run._callTestMethod"

    # _generateFromStack:
    # ===================
    def test_fromStack(self):
        correct_stack = self.correct_stack + ".test_fromStack._generateFromStack"
        self.assertEqual(correct_stack, _generateFromStack(0))
    def test_fromStack_ignoreLast(self):
        correct_stack = self.correct_stack + ".test_fromStack_ignoreLast"
        self.assertEqual(correct_stack, _generateFromStack(1))

    # _generateFromModule:
    # ====================
    def test_fromModule_withoutClass(self):
        correct_topic = "log_topic._generateFromModule"
        self.assertEqual(correct_topic,_generateFromModule(0))
    def test_fromModule_withClass(self):
        correct_topic = "test_logTopic.test_func.test_fromModule_withClass"
        self.assertEqual(correct_topic, _generateFromModule(1))


class test_LogTopic(unittest.TestCase):
    """ Tests for the LogTopic class.

    As this class dosn't give much functionality as the 2 functions,
    this test class may be redundant.
    """

    correctStack = LogTopic("run.__call__.run.__call__.run._callTestMethod.test_fromStack")
    correctModule = LogTopic("test_logTopic.test_LogTopic.test_fromModule")

    def test_fromStack(self):
        self.assertEqual(self.correctStack, LogTopic.topicFactory(method="stack",n_frame=2))
    def test_fromModule(self):
        self.assertEqual(self.correctModule, LogTopic.topicFactory(method="module",n_frame=2))


class test_logTopicFilter(unittest.TestCase):
    """ Tests for the LogTopicFilter class.

    A LogTopicFilter must support 2 wildcard, so
    we test the filtering using zero wildcard, the
    first one, then the second one, and finally the 2
    togethere.
    """

    def test_zeroWildcard(self):
        topic_good = LogTopic("key1.key2.key3")
        topic_bad = LogTopic("key3.key2.key1")
        filter = LogTopicFilter("key1.key2.key3")

        self.assertTrue(filter.match(topic_good))
        self.assertFalse(filter.match(topic_bad))

    def test_firstWildcard(self):
        topic_1 = LogTopic("key1.key2.key3")
        topic_2 = LogTopic("key3.key2.key1")
        topic_3 = LogTopic("notKey1.key2")
        topic_4 = LogTopic("")

        filter_1 = LogTopicFilter("key1.*")
        filter_2 = LogTopicFilter("key*.key2.*")
        filter_3 = LogTopicFilter("*.*")
        filter_4 = LogTopicFilter("key3.key2.*")

        self.assertFalse(filter_1.match(topic_1))
        self.assertFalse(filter_1.match(topic_2))
        self.assertFalse(filter_1.match(topic_3))
        self.assertFalse(filter_1.match(topic_4))

        self.assertTrue(filter_2.match(topic_1))
        self.assertTrue(filter_2.match(topic_2))
        self.assertFalse(filter_2.match(topic_3))
        self.assertFalse(filter_2.match(topic_4))

        self.assertFalse(filter_3.match(topic_1))
        self.assertFalse(filter_3.match(topic_2))
        self.assertTrue(filter_3.match(topic_3))
        self.assertFalse(filter_3.match(topic_4))

        self.assertFalse(filter_4.match(topic_1))
        self.assertTrue(filter_4.match(topic_2))
        self.assertFalse(filter_4.match(topic_3))
        self.assertFalse(filter_4.match(topic_4))

    def test_secondWildcard(self):
        topic_1 = LogTopic("")
        topic_2 = LogTopic("key1.key2.key3")
        topic_3 = LogTopic("key1.key2.key3.key4.key5")

        filter_1 = LogTopicFilter("#")
        filter_2 = LogTopicFilter("key1.#")
        filter_3 = LogTopicFilter("#.key3.#")
        filter_4 = LogTopicFilter("#.key3")

        self.assertTrue(filter_1.match(topic_1))
        self.assertTrue(filter_1.match(topic_2))
        self.assertTrue(filter_1.match(topic_3))

        self.assertFalse(filter_2.match(topic_1))
        self.assertTrue(filter_2.match(topic_2))
        self.assertTrue(filter_2.match(topic_3))

        self.assertFalse(filter_3.match(topic_1))
        self.assertFalse(filter_3.match(topic_2))
        self.assertTrue(filter_3.match(topic_3))

        self.assertFalse(filter_4.match(topic_1))
        self.assertTrue(filter_4.match(topic_2))
        self.assertFalse(filter_4.match(topic_3))
    
    def test_allWildcard(self):
        topic_1 = LogTopic("")
        topic_2 = LogTopic("key1.key2.key3.key4.key5")
        topic_3 = LogTopic("key1a.key2b.key3c.key4d.key5e.key6f")

        filter_1 = LogTopicFilter("#.*.#")
        filter_2 = LogTopicFilter("#.*3*.#")
        filter_3 = LogTopicFilter("#.*3.#")

        self.assertFalse(filter_1.match(topic_1))
        self.assertTrue(filter_1.match(topic_2))
        self.assertTrue(filter_1.match(topic_3))

        self.assertFalse(filter_2.match(topic_1))
        self.assertFalse(filter_2.match(topic_2))
        self.assertTrue(filter_2.match(topic_3))

        self.assertFalse(filter_3.match(topic_1))
        self.assertTrue(filter_3.match(topic_2))
        self.assertFalse(filter_3.match(topic_3))