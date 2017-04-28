from vumi.message import TransportUserMessage
from vumi.tests.helpers import VumiTestCase

from vumi_msisdn_normalize_middleware import NormalizeMsisdnMiddleware

SESSION_NEW, SESSION_CLOSE, SESSION_NONE = (
    TransportUserMessage.SESSION_NEW,
    TransportUserMessage.SESSION_CLOSE,
    TransportUserMessage.SESSION_NONE)


class TestNormalizeMisdnMiddleware(VumiTestCase):

    def mk_middleware(self, config):
        worker = object()
        mw = NormalizeMsisdnMiddleware("test_normalizer", config, worker)
        mw.setup_middleware()
        return mw

    def mk_msg(self, to_addr, from_addr, session_event=SESSION_NEW,
               session_start=None, session_end=None,
               transport_name='dummy_transport'):
        msg = TransportUserMessage(
            to_addr=to_addr, from_addr=from_addr,
            transport_name=transport_name,
            transport_type="dummy_transport_type",
            session_event=session_event)

        if session_start is not None:
            self._set_metadata(msg, 'session_start', session_start)

        if session_end is not None:
            self._set_metadata(msg, 'session_end', session_end)

        return msg

    def setUp(self):
        self.mw = self.mk_middleware({
            'country_code': '256'
        })

    def test_inbound_normalization(self):
        msg = self.mk_msg('12345', '256123456789')
        msg = self.mw.handle_inbound(msg, 'dummy_endpoint')

        self.assertEqual(msg['from_addr'], '+256123456789')

    def test_inbound_normalization_of_null_from_addr(self):
        msg = self.mk_msg('8007', None)
        msg = self.mw.handle_inbound(msg, 'dummy_endpoint')
        self.assertEqual(msg['from_addr'], None)

    def test_inbound_normalization_ignores_strip_plus(self):
        mw = self.mk_middleware({
            'country_code': '256',
            'strip_plus': True,
        })
        msg = self.mk_msg(
            to_addr='8007', from_addr='+256123456789')
        msg = mw.handle_inbound(msg, 'dummy_endpoint')
        self.assertEqual(msg['from_addr'], '+256123456789')

    def test_outbound_normalization(self):
        msg = self.mk_msg(
            to_addr='0123456789', from_addr='8007')
        msg = self.mw.handle_outbound(msg, 'dummy_endpoint')
        self.assertEqual(msg['to_addr'], '+256123456789')

    def test_outbound_normalization_of_null_to_addr(self):
        msg = self.mk_msg(
            to_addr=None, from_addr='8007')
        msg = self.mw.handle_outbound(msg, 'dummy_endpoint')
        self.assertEqual(msg['to_addr'], None)

    def test_outbound_normalization_applies_strip_plus(self):
        mw = self.mk_middleware({
            'country_code': '256',
            'strip_plus': True,
        })
        msg = self.mk_msg(
            to_addr='0123456789', from_addr='8007')
        msg = mw.handle_outbound(msg, 'dummy_endpoint')
        self.assertEqual(msg['to_addr'], '256123456789')
