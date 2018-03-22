#!/usr/bin/env python

import redis


class Data:

    def __init__(self):
        self._redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self._keys = [
            'graph',
            'cons_w',
            'cons_w_rel',
            'cons_cnt',
            'cons_avg_hour',
            'cons_avg_day',
            'cons_avg_week',
            'cons_avg_month',
            'cons_avg_year',
            'prod_w',
            'prod_w_rel',
            'prod_cnt',
            'gas_cnt',
            'gas_avg_hour',
            'gas_avg_day',
            'gas_avg_week',
            'gas_avg_month',
            'gas_avg_year'
        ]

        self.reset()

    def reset(self, keys=None):
        if keys is None:
            for key in self._keys:
                self.set(key, 0)
            self.set_list('graph', [0, 0, 0, 0, 0, 0, 0, 0])
        else:
            for key in keys:
                self.set(key, 0)

    def set(self, key, value):
        self._redis.set(key, str(value))

    def get(self, key):
        return float(self._redis.get(key))

    def set_list(self, key, the_list):
        self._redis.set(key, ','.join(str(i) for i in the_list))

    def get_list(self, key):
        return [float(i) for i in self._redis.get(key).split(',')]

    def all(self):
        _dict = {}

        for key in self._redis.keys():
            _dict[key] = self.get(key)

        return _dict
