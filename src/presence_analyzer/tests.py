# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import json
import os.path
import unittest
from datetime import date, time, timedelta

import main  # pylint: disable=relative-import
import utils  # pylint: disable=relative-import
import views  # pylint: disable=relative-import


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
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday_view(self):
        """
        Test mean presence time of given user grouped by weekday.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/0')

        self.assertEqual(resp.status_code, 404)

        bad_resp = self.client.get('/api/v1/mean_time_weekday/11')
        data = dict(json.loads(bad_resp.data))

        self.assertEqual(bad_resp.status_code, 200)
        self.assertDictEqual(
            data, {
                'Mon': 24123.0,
                'Tue': 16564.0,
                'Wed': 25321.0,
                'Thu': 22984.0,
                'Fri': 6426.0,
                'Sat': 0,
                'Sun': 0,
            }
        )

    def test_presence_weekday_view(self):
        """
        Test by user id, for existing user and non existing user.
        """
        resp = self.client.get('/api/v1/presence_weekday/0')

        self.assertEqual(resp.status_code, 404)

        bad_resp = self.client.get('/api/v1/presence_weekday/11')
        data = dict(json.loads(bad_resp.data))

        self.assertEqual(bad_resp.status_code, 200)
        self.assertDictEqual(
            data, {
                'Weekday': 'Presence (s)',
                'Mon': 24123,
                'Tue': 16564,
                'Wed': 25321,
                'Thu': 45968,
                'Fri': 6426,
                'Sat': 0,
                'Sun': 0
            }
        )


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
        sample_date = date(2013, 9, 10)

        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            time(9, 39, 5)
        )

    def test_group_by_weekday(self):
        """
        Test groups entries by weekdays.
        """
        self.assertEqual(
            utils.group_by_weekday(utils.get_data()[10]),
            [[], [30047], [24465], [23705], [], [], []],
        )
        self.assertEqual(
            utils.group_by_weekday(utils.get_data()[11]),
            [[24123], [16564], [25321], [22969, 22999], [6426], [], []],
        )

    def test_seconds_since_midnight(self):
        """
        Test amount of seconds since midnight.
        """
        self.assertEqual(
            utils.seconds_since_midnight(time(2, 12, 6)),
            timedelta(
                hours=2,
                minutes=12,
                seconds=6
            ).seconds
        )
        self.assertEqual(
            utils.seconds_since_midnight(time(12, 0, 35)),
            timedelta(
                hours=12,
                minutes=0,
                seconds=35
            ).seconds
        )
        self.assertEqual(
            utils.seconds_since_midnight(time(1, 1, 59)),
            timedelta(
                hours=1,
                minutes=1,
                seconds=59
            ).seconds
        )

    def test_interval(self):
        """
        Test calculating interval between two time objects.

        """
        self.assertEqual(
            25300,
            abs(utils.interval(time(18, 3, 16), time(11, 1, 36)))
        )
        self.assertEqual(
            61300,
            abs(utils.interval(time(18, 3, 16), time(1, 1, 36)))
        )
        self.assertEqual(
            3696,
            abs(utils.interval(time(0, 0, 0), time(1, 1, 36)))
        )

    def test_mean(self):
        """
        Test arithmetic mean.
        """
        self.assertEqual(utils.mean([1, 2, 3, 4, 5, 6]), 3.5)
        self.assertEqual(utils.mean([]), 0)
        self.assertEqual(utils.mean([1, 4, 7]), 4)
        self.assertEqual(utils.mean([1, 99]), 50)


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
