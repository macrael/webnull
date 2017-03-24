#!/usr/bin/env python

import datetime
import unittest

import webnull

class PrettyDateTests(unittest.TestCase):

    def setUp(self):
        self.now = datetime.datetime(2017, 3, 24, 13, 35, 22)


def generate_test(time_delta, expected_result):
    def fake_test(self):
        test_time = self.now + time_delta
        pretty_date = webnull.pretty_time(test_time, self.now)
        print pretty_date
        self.assertEqual(pretty_date, expected_result)
    return fake_test

def generate_delta_tests():
    test_deltas = {
        '5min': { 'delta': datetime.timedelta(minutes=5), 'pretty': '1:40 PM' },
        '5.5min': { 'delta': datetime.timedelta(minutes=5, seconds=32), 'pretty': '1:40 PM' },
        '10min': { 'delta': datetime.timedelta(minutes=10, seconds=2), 'pretty': '1:45 PM' },
        '2hours': { 'delta': datetime.timedelta(hours=2, seconds=4), 'pretty': '3:35 PM' },
        '14hours': { 'delta': datetime.timedelta(hours=14, seconds=2), 'pretty': '3:35 AM' },
        '24hours': { 'delta': datetime.timedelta(hours=24, minutes=10, seconds=2), 'pretty': 'tomorrow at 1:45 PM' },
        '2days': { 'delta': datetime.timedelta(days=2, minutes=10, seconds=2), 'pretty': 'Sunday at 1:45 PM' },
        '6days': { 'delta': datetime.timedelta(days=6, minutes=10, seconds=2), 'pretty': 'Thursday at 1:45 PM' },
        '7days': { 'delta': datetime.timedelta(days=7, minutes=10, seconds=2), 'pretty': 'Friday the 31st at 1:45 PM' },
        '8days': { 'delta': datetime.timedelta(days=8, minutes=10, seconds=2), 'pretty': 'April 1st at 1:45 PM' },
        '8years': { 'delta': datetime.timedelta(weeks=8*52, days=8, minutes=10, seconds=2), 'pretty': 'March 22nd 2025 at 1:45 PM' },
    }

    for label in test_deltas.keys():
        new_test = generate_test(test_deltas[label]['delta'], test_deltas[label]['pretty'])
        test_name = 'test_' + label
        setattr(PrettyDateTests, test_name, new_test)

generate_delta_tests()

if __name__ == '__main__':
    unittest.main()
