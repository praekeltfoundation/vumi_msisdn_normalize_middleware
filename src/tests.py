
from twisted.internet.defer import inlineCallbacks, returnValue

from zope.interface import implements

from vumi.tests.helpers import VumiTestCase, generate_proxies, IHelper
from vumi.worker import BaseWorker

from go.vumitools.app_worker import GoWorkerMixin, GoWorkerConfigMixin
from go.vumitools.middleware import NormalizeMsisdnMiddleware
from go.vumitools.tests.helpers import VumiApiHelper, GoMessageHelper


class ToyWorkerConfig(BaseWorker.CONFIG_CLASS, GoWorkerConfigMixin):
    pass


class ToyWorker(BaseWorker, GoWorkerMixin):
    CONFIG_CLASS = ToyWorkerConfig

    def setup_worker(self):
        return self._go_setup_worker()

    def teardown_worker(self):
        return self._go_teardown_worker()

    def setup_connectors(self):
        pass


class MiddlewareHelper(object):
    implements(IHelper)

    def __init__(self, middleware_class):
        self._vumi_helper = VumiApiHelper()
        self._msg_helper = GoMessageHelper()
        self.middleware_class = middleware_class
        self._middlewares = []

        generate_proxies(self, self._vumi_helper)
        generate_proxies(self, self._msg_helper)

    def setup(self):
        return self._vumi_helper.setup(setup_vumi_api=False)

    @inlineCallbacks
    def cleanup(self):
        for mw in self._middlewares:
            yield mw.teardown_middleware()
        yield self._vumi_helper.cleanup()

    @inlineCallbacks
    def create_middleware(self, config=None, middleware_class=None,
                          name='dummy_middleware'):
        worker_helper = self._vumi_helper.get_worker_helper()
        dummy_worker = yield worker_helper.get_worker(
            ToyWorker, self.mk_config({}))
        config = self.mk_config(config or {})
        if middleware_class is None:
            middleware_class = self.middleware_class
        mw = middleware_class(name, config, dummy_worker)
        self._middlewares.append(mw)
        yield mw.setup_middleware()
        returnValue(mw)


class TestNormalizeMisdnMiddleware(VumiTestCase):

    @inlineCallbacks
    def setUp(self):
        self.mw_helper = self.add_helper(
            MiddlewareHelper(NormalizeMsisdnMiddleware))
        self.mw = yield self.mw_helper.create_middleware({
            'country_code': '256',
        })

    def test_inbound_normalization(self):
        msg = self.mw_helper.make_inbound(
            "foo", to_addr='8007', from_addr='256123456789')
        msg = self.mw.handle_inbound(msg, 'dummy_endpoint')
        self.assertEqual(msg['from_addr'], '+256123456789')

    def test_inbound_normalization_of_null_from_addr(self):
        msg = self.mw_helper.make_inbound(
            "foo", to_addr='8007', from_addr=None)
        msg = self.mw.handle_inbound(msg, 'dummy_endpoint')
        self.assertEqual(msg['from_addr'], None)

    @inlineCallbacks
    def test_inbound_normalization_ignores_strip_plus(self):
        mw = yield self.mw_helper.create_middleware({
            'country_code': '256',
            'strip_plus': True,
        })
        msg = self.mw_helper.make_inbound(
            "foo", to_addr='8007', from_addr='+256123456789')
        msg = mw.handle_inbound(msg, 'dummy_endpoint')
        self.assertEqual(msg['from_addr'], '+256123456789')

    def test_outbound_normalization(self):
        msg = self.mw_helper.make_outbound(
            "foo", to_addr='0123456789', from_addr='8007')
        msg = self.mw.handle_outbound(msg, 'dummy_endpoint')
        self.assertEqual(msg['to_addr'], '+256123456789')

    def test_outbound_normalization_of_null_to_addr(self):
        msg = self.mw_helper.make_outbound(
            "foo", to_addr=None, from_addr='8007')
        msg = self.mw.handle_outbound(msg, 'dummy_endpoint')
        self.assertEqual(msg['to_addr'], None)

    @inlineCallbacks
    def test_outbound_normalization_applies_strip_plus(self):
        mw = yield self.mw_helper.create_middleware({
            'country_code': '256',
            'strip_plus': True,
        })
        msg = self.mw_helper.make_outbound(
            "foo", to_addr='0123456789', from_addr='8007')
        msg = mw.handle_outbound(msg, 'dummy_endpoint')
        self.assertEqual(msg['to_addr'], '256123456789')
