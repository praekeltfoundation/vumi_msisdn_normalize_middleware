from vumi.config import ConfigBool, ConfigText
from vumi.middleware.base import TransportMiddleware

from vumi.utils import normalize_msisdn


class NormalizeMsisdnMiddlewareConfig(TransportMiddleware.CONFIG_CLASS):
    """
    NormalizeMsisdnMiddleware configuration options.
    """

    country_code = ConfigText(
        "Country code prefix to normalize.",
        required=True, static=True)

    strip_plus = ConfigBool(
        "Whether to strip leading + signs.",
        default=False, static=True)


class NormalizeMsisdnMiddleware(TransportMiddleware):

    CONFIG_CLASS = NormalizeMsisdnMiddlewareConfig

    def setup_middleware(self):
        self.country_code = self.config.country_code
        self.strip_plus = self.config.strip_plus

    def _normalize_msisdn(self, addr, country_code, strip_plus):
        if addr is None:
            return addr
        addr = normalize_msisdn(addr, country_code=country_code)
        if strip_plus:
            addr = addr.lstrip('+')
        return addr

    def handle_inbound(self, message, endpoint):
        message['from_addr'] = self._normalize_msisdn(
            message.get('from_addr'), country_code=self.country_code,
            strip_plus=False)
        return message

    def handle_outbound(self, message, endpoint):
        message['to_addr'] = self._normalize_msisdn(
            message.get('to_addr'), country_code=self.country_code,
            strip_plus=self.strip_plus)
        return message
