from datetime import datetime, timedelta, timezone
from time import sleep

import pytest

from reactivex.scheduler.eventloop import TwistedScheduler

twisted = pytest.importorskip("twisted")
from twisted.internet import defer, reactor  # isort: skip
from twisted.trial import unittest  # isort: skip


class TestTwistedScheduler(unittest.TestCase):
    def test_twisted_schedule_now(self):
        scheduler = TwistedScheduler(reactor)
        diff = scheduler.now - datetime.fromtimestamp(
            float(reactor.seconds()), tz=timezone.utc
        )
        assert abs(diff) < timedelta(milliseconds=1)

    def test_twisted_schedule_now_units(self):
        scheduler = TwistedScheduler(reactor)
        diff = scheduler.now
        sleep(0.1)
        diff = scheduler.now - diff
        assert timedelta(milliseconds=80) < diff < timedelta(milliseconds=180)

    @defer.inlineCallbacks
    def test_twisted_schedule_action(self):
        scheduler = TwistedScheduler(reactor)
        promise = defer.Deferred()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        def done():
            promise.callback("Done")

        scheduler.schedule(action)
        reactor.callLater(0.1, done)

        yield promise
        assert ran is True

    @defer.inlineCallbacks
    def test_twisted_schedule_action_due(self):
        scheduler = TwistedScheduler(reactor)
        promise = defer.Deferred()
        starttime = reactor.seconds()
        endtime = None

        def action(scheduler, state):
            nonlocal endtime
            endtime = reactor.seconds()

        def done():
            promise.callback("Done")

        scheduler.schedule_relative(0.2, action)
        reactor.callLater(0.3, done)

        yield promise
        diff = endtime - starttime
        assert diff > 0.18

    @defer.inlineCallbacks
    def test_twisted_schedule_action_cancel(self):
        scheduler = TwistedScheduler(reactor)
        promise = defer.Deferred()
        ran = False

        def action(scheduler, state):
            nonlocal ran
            ran = True

        def done():
            promise.callback("Done")

        d = scheduler.schedule_relative(0.01, action)
        d.dispose()

        reactor.callLater(0.1, done)
        yield promise
        assert ran is False
