from iris.constants import CALL_SUPPORT
from iris.custom_import import import_custom_module
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkdyvmsapi.request.v20170525.SingleCallByTtsRequest import SingleCallByTtsRequest
import datetime
import logging
import time
import json

logger = logging.getLogger(__name__)


class iris_aliyun(object):
    supports = frozenset([CALL_SUPPORT])

    def __init__(self, config):
        self.config = config
        self.proxy = None
        if 'proxy' in self.config:
            host = self.config['proxy']['host']
            port = self.config['proxy']['port']
            self.proxy = {'http': 'http://%s:%s' % (host, port),
                          'https': 'https://%s:%s' % (host, port)}
        self.modes = {
            CALL_SUPPORT: self.send_call,
        }
        self.timeout = config.get('timeout', 10)
        push_config = config.get('push_notification', {})
        self.push_active = push_config.get('activated', False)
        if self.push_active:
            self.notifier = import_custom_module('iris.push', push_config['type'])(push_config)

    def get_aliyun_client(self):
        client = AcsClient(
            self.config['access_key_id'],
            self.config['access_secret'],
            self.config['region'],
        )
        return client

    def send_call(self, message):
        start = time.time()

        client = self.get_aliyun_client()

        req = SingleCallByTtsRequest()
        req.set_accept_format('json')
        req.set_CalledShowNumber(self.config['number'])
        req.set_TtsCode(self.config['tts_code'])
        req.set_endpoint('dyvmsapi.aliyuncs.com')

        req.set_CalledNumber(message['destination'])

        ts = message['incident_created'].strftime("%Y%m%d and %H%M")
        params = {
            'system': message['context']['title'],
            'level': message['context']['message'],
            'time': ts,
        }
        req.set_TtsParam(json.dumps(params))

        try:
            resp0 = client.do_action_with_exception(req)
            resp = json.loads(resp0)
            if resp['Code'] == 'OK':
                return time.time() - start
            else:
                print(resp)
                logger.warning('aliyun resp failed: (code: %s, msg: %s, reqId: %s)', resp['Code'], resp['Message'], resp['RequestId'])
        except Exception:
            logger.exception('aliyun call failed')

        return time.time() - start

    def send(self, message, customizations=None):
        if self.push_active:
            self.notifier.send_push(message)
        return self.modes[message['mode']](message)
