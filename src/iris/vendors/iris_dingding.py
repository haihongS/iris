from iris.constants import DINGDING_SUPPORT
from iris.custom_import import import_custom_module
import json
import logging
import requests
import time

logger = logging.getLogger(__name__)


class iris_dingding(object):
    supports = frozenset([DINGDING_SUPPORT])

    def __init__(self, config):
        self.config = config

        self.modes = {
            DINGDING_SUPPORT: self.send_dingding,
        }

        self.proxy = None
        if 'proxy' in self.config:
            host = self.config['proxy']['host']
            port = self.config['proxy']['port']
            self.proxy = {'http': 'http://%s:%s' % (host, port),
                          'https': 'https://%s:%s' % (host, port)}
        self.timeout = config.get('timeout', 10)

        push_config = config.get('push_notification', {})
        self.push_active = push_config.get('activated', False)
        if self.push_active:
            self.notifier = import_custom_module('iris.push', push_config['type'])(push_config)

    def send_dingding(self, message):
        # TODO: message decode & encode to dingding
        start = time.time()

        msg = {
            'msgtype': 'markdown',
            'markdown': {
                'title': 'xx',
                'text': 'yy \n\n zz \n\n'
            },
            'at': {
                'atMobiles': [],
                'isAtAll': True,
            }
        }
        headers = {'content-type': 'application/json'}

        try:
            response = requests.post(
                self.config['base_url'],
                data=json.dumps(msg),
                headers=headers,
                proxies=self.proxy,
                timeout=self.timeout,
            )

            if response.status_code == 200:
                data = response.json()
                if data['errcode'] == 0:
                    return time.time() - start
                else:
                    logger.error('received an err from dingding: %s', data['errmsg'])
            else:
                logger.error('send msg to dingding failed: %d', response.status_code)
        except Exception:
            logger.exception('dingding post request failed')

        return time.time() - start

    def send(self, message, cutomizations=None):
        if self.push_active:
            self.notifier.send_push(message)
        return self.modes[message['mode']](message)
