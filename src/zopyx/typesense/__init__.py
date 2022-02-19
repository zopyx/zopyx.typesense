# -*- coding: utf-8 -*-
"""Init and utils."""
from huey.bin.huey_consumer import load_huey
from huey.consumer_options import ConsumerConfig
from zope.i18nmessageid import MessageFactory
from zopyx.plone.persistentlogger.file_logger import get_logger

import threading


_ = MessageFactory("zopyx.typesense")

LOG = get_logger("zopyx.typesense")

# Start huey consumer as thread

from huey.consumer import Consumer

import signal


# monkey-patch huey
def my_set_signal_handlers(self):
    """Ignore signal errors from Huey"""
    try:
        signal.signal(signal.SIGTERM, self._handle_stop_signal)
        signal.signal(signal.SIGINT, signal.default_int_handler)
        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, self._handle_restart_signal)
    except ValueError:
        LOG.warning("Huey signal exception ignored")


Consumer._set_signal_handlers = my_set_signal_handlers


consumer_options = {
    "backoff": 1.15,
    "check_worker_health": True,
    "extra_locks": None,
    "flush_locks": False,
    "health_check_interval": 10,
    "initial_delay": 0.1,
    "max_delay": 10.0,
    "periodic": True,
    "scheduler_interval": 1,
    "worker_type": "thread",
    "workers": 4,
    "logfile": "huey.log",
    "verbose": False,
}

h = load_huey("zopyx.typesense.huey_tasks.huey")

config = ConsumerConfig(**consumer_options)
config.validate()
config.setup_logger()
consumer = h.create_consumer(**config.values)

th = threading.Thread(target=consumer.run)
th.start()

LOG.info("Started Huey consumer thread")
