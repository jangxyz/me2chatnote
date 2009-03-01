#!/usr/bin/python
import urllib2
from datetime import datetime

ME2DAY_DATETIME_FORMAT="%Y-%m-%dT%X+0900"

def time_iso8601(time):
    return time.strftime("%Y-%m-%dT%H:%M:%S")

class OpenStruct:
    def __init__(self, params=None):
        if params:
            self.parse(params)

    def parse(self, params, recursive=True):
        d = OpenStruct.parse_dictionary(params, recursive)
        for key, value in d.iteritems():
            setattr(self, key, value)

    @staticmethod
    def parse(params, recursive=True):
        result = OpenStruct.parse_dictionary(params, recursive)
        def pack_open_struct(param):
            o = OpenStruct()
            for key, value in param.iteritems():
                setattr(o, key, value)
            return o
        # list of objects
        if isinstance(result, list):
            return [pack_open_struct(d) for d in result]
        # single object
        else:
            return pack_open_struct(result)

    @staticmethod
    def parse_dictionary(params, recursive=True):
        # list of objects
        if isinstance(params, list):
            return [OpenStruct.parse_dictionary(d) for d in params]
        # single object
        elif isinstance(params, dict):
            def nestable(value):
                return isinstance(value, dict) and recursive
            d = {}
            for key, value in params.iteritems():
                # nest if value is dictionary
                if nestable(value):
                    value = OpenStruct.parse(value, recursive)
                # check if value is list with dictionary inside
                elif isinstance(value, list):
                    value = [
                        OpenStruct.parse(v, recursive)  \
                        if nestable(v) else v           \
                        for v in value[:]               \
                    ]
                # type conversion
                if key == "pubDate":
                    value = datetime.strptime(value, ME2DAY_DATETIME_FORMAT)
                d[key] = value
            return d
        else:
            return params


class Json:
    @staticmethod
    def parse(data):
        data = data.replace('null', 'None')     \
                    .replace('false', 'False')  \
                    .replace('true', 'True')
        e_data = eval(data)
        if "pubDate" in e_data:
            e_data["pubDate"] = datetime.strptime(e_data["pubDate"], ME2DAY_DATETIME_FORMAT)
        return e_data


class Me2day:
    @staticmethod
    def posts(username, **params):
        url = 'http://me2day.net/api/get_posts/%s' % username
        for key in ['since', 'to']:
            if key in params:
                value = params[key]
                if isinstance(value, datetime):
                    value = time_iso8601(value)
                params[key] = value
        if 'since' in params:
            params['from'] = params.pop('since')
          
        posts = Me2day.fetch_resource(url, params)
        return posts

    @staticmethod
    def fetch_resource(url, param={}):
        url += '.json'
        if param:
            query = '&'.join(['='.join([k,v]) for k,v in param.items()])
            url  += '?%s' % query
        url = url.replace(' ', '%20')
        # fetch from me2day
        data = urllib2.urlopen(url).read()
        data = Json.parse(data)
        return OpenStruct.parse(data)

    @staticmethod
    def convert(s):
        """ '\\ud55c\\uae00' => u'\ud55c\uae00' """
        return eval("u'%s'" % s)


