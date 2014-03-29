import json
import unittest

import requests
from mock import MagicMock, patch

from bux_grader_framework.xqueue import XQueueClient, InvalidXReply
from bux_grader_framework.exceptions import BadCredentials, BadQueueName

XQUEUE_TEST_CONFIG = {
    "url": "http://localhost:18040",
    "username": "test",
    "password": "passwd",
    "timeout": 10
}


class TestXQueueClient(unittest.TestCase):

    @patch('bux_grader_framework.xqueue.requests.session')
    def setUp(self, mock_session):
        self.client = XQueueClient(**XQUEUE_TEST_CONFIG)

    def test_login(self):
        xqueue_response = {"return_code": 0, "content": "Logged in"}
        response = MagicMock(spec=requests.Response())
        response.content = json.dumps(xqueue_response)

        self.client.session.post = MagicMock(return_value=response)

        self.assertEquals(True, self.client.login())

        post_data = {
            "username": XQUEUE_TEST_CONFIG["username"],
            "password": XQUEUE_TEST_CONFIG["password"]
        }
        self.client.session.post.assert_called_with(
            XQUEUE_TEST_CONFIG["url"] + "/xqueue/login/",
            data=post_data
            )

    def test_login_invalid_requests_response(self):
        bad_response = MagicMock(spec=requests.Response())
        bad_response.ok = False
        bad_response.text = "Bad response"

        self.client.session.post = MagicMock(return_value=bad_response)

        self.assertRaises(BadCredentials, self.client.login)

    def test_login_invalid_credentials(self):
        xreply = {"return_code": 1, "content": "Incorrect login credentials"}
        bad_response = MagicMock(spec=requests.Response())
        bad_response.ok = True
        bad_response.content = json.dumps(xreply)

        self.client.session.post = MagicMock(return_value=bad_response)

        self.assertRaises(BadCredentials, self.client.login)

    def test_parse_xreply(self):
        xreply = json.dumps({"return_code": 0, "content": "Test content"})
        self.assertEquals((True, "Test content"),
                          self.client._parse_xreply(xreply))

    def test_parse_xreply_missing_content(self):
        xreply = json.dumps({"return_code": 1})
        self.assertRaises(InvalidXReply,
                          self.client._parse_xreply, xreply)

    def test_parse_xreply_not_dict(self):
        xreply = json.dumps(['not', 'dict'])
        self.assertRaises(InvalidXReply,
                          self.client._parse_xreply, xreply)

    def test_parse_xreply_not_json(self):
        xreply = {"return_code": 1, "content": "Not JSON string"}
        self.assertRaises(InvalidXReply,
                          self.client._parse_xreply, xreply)

    def test_parse_xreply_empty(self):
        xreply = ""
        self.assertRaises(InvalidXReply,
                          self.client._parse_xreply, xreply)

    def test_get_queuelen(self):
        xreply = {"return_code": 0, "content": 2}
        response = MagicMock(spec=requests.Response())
        response.content = json.dumps(xreply)
        self.client.session.get = MagicMock(return_value=response)

        self.assertEquals(2, self.client.get_queuelen("foo"))

        self.client.session.get.assert_called_with(
            XQUEUE_TEST_CONFIG["url"] + "/xqueue/get_queuelen/",
            params={"queue_name": "foo"}
            )

    @patch('bux_grader_framework.XQueueClient.login', return_value=True)
    def test_get_queuelen_with_login(self, mock_login):
        # Initial `GET "/xqueue/queuelen/"` response
        initial_response = {"return_code": 1, "content": "login_required"}
        pre_login_response = MagicMock(spec=requests.Response())
        pre_login_response.content = json.dumps(initial_response)

        # Post-login `GET "/xqueue/queuelen/"` response
        final_response = {"return_code": 0, "content": 2}
        post_login_response = MagicMock(spec=requests.Response())
        post_login_response.content = json.dumps(final_response)

        side_effect = [pre_login_response, post_login_response]
        self.client.session.get = MagicMock(side_effect=side_effect)

        self.assertEquals(2, self.client.get_queuelen("foo"))

    @patch('bux_grader_framework.XQueueClient.login',
           side_effect=BadCredentials)
    def test_get_queuelen_with_login_failure(self, mock_login):
        # Initial `GET "/xqueue/queuelen/"` response
        initial_response = {"return_code": 1, "content": "login_required"}
        pre_login_response = MagicMock(spec=requests.Response())
        pre_login_response.content = json.dumps(initial_response)

        self.client.session.get = MagicMock(return_value=pre_login_response)

        self.assertRaises(BadCredentials, self.client.get_queuelen, "foo")

    def test_get_queuelen_invalid_queue_name(self):
        xqueue_response = {"return_code": 1, "content": "Valid queue names "
                           "are: certificates, edX-Open_DemoX, open-ended, "
                           "test-pull"}
        response = MagicMock(spec=requests.Response())
        response.content = json.dumps(xqueue_response)
        self.client.session.get = MagicMock(return_value=response)

        self.assertRaises(BadQueueName, self.client.get_queuelen, "bar")


if __name__ == '__main__':
    unittest.main()
