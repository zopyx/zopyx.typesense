# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory
from zopyx.plone.persistentlogger.file_logger import get_logger


_ = MessageFactory('zopyx.typesense')

LOG = get_logger('zopyx.typesense')
