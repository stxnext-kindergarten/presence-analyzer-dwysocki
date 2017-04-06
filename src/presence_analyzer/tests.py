# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

import views# pylint: disable=relative-import
import main  # pylint: disable=relative-import
import utils  # pylint: disable=relative-import


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')

        self.assertEqual(resp.status_code, 302)

        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)

        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday_view(self):
        """
        Test by user id.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/0')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/api/v1/mean_time_weekday/11')

        self.assertEqual(resp.status_code, 200)
        data = dict(json.loads(resp.data))
        expected = {
            'Mon': 24123.0,
            'Tue': 16564.0,
            'Wed': 25321.0,
            'Thu': 22984.0,
            'Fri': 6426.0,
            'Sat': 0,
            'Sun': 0,
        }

        self.assertDictEqual(data, expected)

    def test_presence_weekday_view(self):
        """
        Test by user id.
        """
        resp = self.client.get('/api/v1/presence_weekday/0')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/api/v1/presence_weekday/11')
        self.assertEqual(resp.status_code, 200)

        data = dict(json.loads(resp.data))
        expected = {
            'Weekday': 'Presence (s)',
            'Mon': 24123,
            'Tue': 16564,
            'Wed': 25321,
            'Thu': 45968,
            'Fri': 6426,
            'Sat': 0,
            'Sun': 0
        }

        self.assertDictEqual(expected, data)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_group_by_weekday(self):
        """
        Test list of times of user.
        """
        data = utils.get_data()
        actual = utils.group_by_weekday(data[10])
        expected = [[], [30047], [24465], [23705], [], [], []]

        self.assertEqual(actual, expected)

    def test_seconds_since_midnight(self):
        """
        Test amount of seconds since midnight.
        """
        sample_time = datetime.time(2, 12, 6)
        expected_time = datetime.timedelta(
            hours=2,
            minutes=12,
            seconds=6,
        )
        data = utils.seconds_since_midnight(sample_time)

        self.assertEqual(expected_time.seconds, data)

    def test_interval(self):
        """
        Test inverval in seconds between two datetime.
        """
        start = datetime.time(18, 3, 16)
        end = datetime.time(11, 1, 36)
        time_one = datetime.timedelta(
            hours=18,
            minutes=3,
            seconds=16,
        )
        time_two = datetime.timedelta(
            hours=11,
            minutes=1,
            seconds=36,
        )
        actual = utils.interval(start, end)
        expected = time_one - time_two

        self.assertEqual(expected.seconds, abs(actual))

    def test_mean(self):
        """
        Test arithmetic mean.
        """
        items = [1, 2, 3, 4, 5, 6]
        actual = utils.mean(items)
        self.assertEqual(actual, 3.5)


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
