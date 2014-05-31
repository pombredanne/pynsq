import os
import sys
import signal
import subprocess
import time
import ssl

import tornado.httpclient
import tornado.testing

# shunt '..' into sys.path since we are in a 'tests' subdirectory
base_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import nsq


class ReaderIntegrationTest(tornado.testing.AsyncTestCase):
    identify_options = {
        'user_agent': 'sup',
        'snappy': True,
        'tls_v1': True,
        'tls_options': {'cert_reqs': ssl.CERT_NONE},
        'heartbeat_interval': 10,
        'output_buffer_size': 4096,
        'output_buffer_timeout': 50
    }

    def setUp(self):
        super(ReaderIntegrationTest, self).setUp()
        self.processes = []
        proc = subprocess.Popen(['nsqd', '--verbose', '--snappy',
                                 '--tls-key=%s/tests/key.pem' % base_dir,
                                 '--tls-cert=%s/tests/cert.pem' % base_dir])
        self.processes.append(proc)
        http = tornado.httpclient.HTTPClient()
        start = time.time()
        while True:
            try:
                resp = http.fetch('http://127.0.0.1:4151/ping')
                if resp.body == 'OK':
                    break
                continue
            except:
                if time.time() - start > 5:
                    raise
                time.sleep(0.1)
                continue

    def tearDown(self):
        super(ReaderIntegrationTest, self).tearDown()
        for proc in self.processes:
            os.kill(proc.pid, signal.SIGKILL)
            proc.wait()

    def test_conn_identify(self):
        c = nsq.async.AsyncConn('127.0.0.1', 4150, io_loop=self.io_loop)
        c.on('identify_response', self.stop)
        c.connect()
        response = self.wait()
        print response
        assert response['conn'] is c
        assert isinstance(response['data'], dict)

    def test_conn_identify_options(self):
        c = nsq.async.AsyncConn('127.0.0.1', 4150, io_loop=self.io_loop,
                                **self.identify_options)
        c.on('identify_response', self.stop)
        c.connect()
        response = self.wait()
        print response
        assert response['conn'] is c
        assert isinstance(response['data'], dict)
        assert response['data']['snappy'] is True
        assert response['data']['tls_v1'] is True

    def test_conn_subscribe(self):
        topic = 'test_conn_suscribe_%s' % time.time()
        c = nsq.async.AsyncConn('127.0.0.1', 4150, io_loop=self.io_loop,
                                **self.identify_options)

        def _on_ready(*args, **kwargs):
            c.on('response', self.stop)
            c.send(nsq.subscribe(topic, 'ch'))

        c.on('ready', _on_ready)
        c.connect()
        response = self.wait()
        print response
        assert response['conn'] is c
        assert response['data'] == 'OK'

    def _send_messages(self, topic, count, body):
        c = nsq.async.AsyncConn('127.0.0.1', 4150, io_loop=self.io_loop)
        c.connect()

        def _on_ready(*args, **kwargs):
            for i in range(count):
                c.send(nsq.pub(topic, body))

        c.on('ready', _on_ready)

    def test_conn_messages(self):
        self.msg_count = 0

        topic = 'test_conn_suscribe_%s' % time.time()
        self._send_messages(topic, 5, 'sup')

        c = nsq.async.AsyncConn('127.0.0.1', 4150, io_loop=self.io_loop,
                                **self.identify_options)

        def _on_message(*args, **kwargs):
            self.msg_count += 1
            if c.rdy == 0:
                self.stop()

        def _on_ready(*args, **kwargs):
            c.on('message', _on_message)
            c.send(nsq.subscribe(topic, 'ch'))
            c.send_rdy(5)

        c.on('ready', _on_ready)
        c.connect()

        self.wait()
        assert self.msg_count == 5

    def test_reader_messages(self):
        self.msg_count = 0
        num_messages = 500

        topic = 'test_reader_msgs_%s' % time.time()
        self._send_messages(topic, num_messages, 'sup')

        def handler(msg):
            assert msg.body == 'sup'
            self.msg_count += 1
            if self.msg_count >= num_messages:
                self.stop()
            return True

        nsq.Reader(nsqd_tcp_addresses=['127.0.0.1:4150'], topic=topic, channel='ch',
                   io_loop=self.io_loop, message_handler=handler, max_in_flight=100,
                   **self.identify_options)

        self.wait()

    def test_reader_heartbeat(self):
        this = self
        this.count = 0

        def handler(msg):
            return True

        class HeartbeatReader(nsq.Reader):
            def heartbeat(self, conn):
                this.count += 1
                if this.count == 2:
                    this.stop()

        topic = 'test_reader_hb_%s' % time.time()
        HeartbeatReader(nsqd_tcp_addresses=['127.0.0.1:4150'], topic=topic, channel='ch',
                        io_loop=self.io_loop, message_handler=handler, max_in_flight=100,
                        heartbeat_interval=1)
        self.wait()
