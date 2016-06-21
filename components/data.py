#!/usr/bin/env python

import redis

class Data:

    def __init__(self):
        self._redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self._keys = [
            'cons_w',
            'cons_w_rel',
            'cons_cnt',
            'prod_w',
            'prod_w_rel',
            'prod_cnt',
            'gas_cnt'
        ]

        for key in self._keys:
            self.set(key, 0)

    def set(self, key, value):
        self._redis.set(key, str(value))

    def get(self, key):
        return float(self._redis.get(key))

    def all(self):
        _dict = {}

        for key in self._redis.keys():
            _dict[key] = self.get(key)

        return _dict



