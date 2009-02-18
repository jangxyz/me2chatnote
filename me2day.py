#!/usr/bin/python
import urllib2

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
        return eval(data)


class Me2day:
    @staticmethod
    def posts(username, **params):
        url = 'http://me2day.net/api/get_posts/%s' % username
        posts = Me2day.fetch_resource(url, params)
        return posts

    @staticmethod
    def fetch_resource(url, param={}):
        url += '.json'
        if param:
            query = '&'.join(['='.join([k,v]) for k,v in param.items()])
            url   = '%s?%s' % (url, query)
        url = url.replace(' ', '%20')
        # fetch from me2day
        data = urllib2.urlopen(url).read()
        data = Json.parse(data)
        return OpenStruct.parse(data)


