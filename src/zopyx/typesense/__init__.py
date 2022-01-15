# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory
from zopyx.plone.persistentlogger.file_logger import get_logger
import threading
from huey.bin.huey_consumer import load_huey
from huey.consumer_options import ConsumerConfig


_ = MessageFactory("zopyx.typesense")

LOG = get_logger("zopyx.typesense")

# Start huey consumer as thread

config = {'backoff': 1.15,
 'check_worker_health': True,
 'extra_locks': None,
 'flush_locks': False,
 'health_check_interval': 10,
 'initial_delay': 0.1,
 'max_delay': 10.0,
 'periodic': True,
 'scheduler_interval': 1,
 'worker_type': 'thread',
 'workers': 4}

h = load_huey("zopyx.typesense.huey_tasks.huey")
consumer = h.create_consumer(**config)

th = threading.Thread(target=consumer.run)
th.start()

LOG.info("Started Huey consumer thread")
