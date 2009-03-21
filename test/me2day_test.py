#!/usr/bin/python
# coding: utf-8
import test_env

import unittest
import me2day
from lib.mock import Mock

class OpenStructTestCase(unittest.TestCase):
    def test_parse_dictionary_to_object(self):
        d = {
            'tags': ['woc', 'abc', 'def'], 
            'ooo': 'xxx'
        }
        o = me2day.OpenStruct.parse(d)
        assert o.tags == d['tags']
        assert o.ooo  == d['ooo']

    def test_parse_array_of_dictionary_to_object(self):
        ds = [
            {
                'tags': ['woc1', 'abc1', 'def1'], 
                'ooo': 'xxx1'
            },
            {
                'tags': ['woc2', 'abc2', 'def2'], 
                'ooo': 'xxx2'
            }
        ]
        os = me2day.OpenStruct.parse(ds)
        assert isinstance(os, list)
        assert isinstance(os[0], me2day.OpenStruct)
        assert len(os) == 2
        assert os[-1].ooo == 'xxx2'

    def test_parse_nested_dictionary_to_nested_object(self):
        d = {
            'tags': ['woc', 'abc', 'def'], 
            'ooo': 'xxx',
            'nested': {
                'url': 'www.some.where/over?the=rainbow'
            }
        }
        o = me2day.OpenStruct.parse(d)
        assert isinstance(o.nested, me2day.OpenStruct)
        assert o.nested.url == d['nested']['url']

    def test_parse_nested_list_of_dictionaries_to_nested_list_of_ojects(self):
        d = {
            'ooo': 'xxx',
            'tags': ['woc', 'abc', 'def'], 
            'nested': [
                {'url': 'www.some.where/over?the=rainbow'},
                {'url': 'www.some.otherplace/over?the=cloud'}
            ]
        }
        o = me2day.OpenStruct.parse(d)
        assert isinstance(o.nested[0], me2day.OpenStruct)
        assert o.nested[0].url == d['nested'][0]['url']

    
class Me2dayApiTestCase(unittest.TestCase):
    def setUp(self):
        self.basic_response = '[]'
        
    def test_encode_korean_correctly(self):
        result = "\\ud55c\\uae00"
        assert me2day.Me2day.convert(result) == u"\ud55c\uae00"

    def test_posts_calls_proper_url(self):
        username = 'jangxyz'
        get_post_url = "http://me2day.net/api/get_posts/%s.json" % username
        def assert_url(url):
            assert url == get_post_url
            return Mock({'read': self.basic_response})
        me2day.urllib2.urlopen = assert_url

        posts = me2day.Me2day.posts(username)

    def test_posts_with_tags_calls_proper_url(self):
        username = 'jangxyz'
        tag = 'woc'
        get_post_url = "http://me2day.net/api/get_posts/%s.json?tag=%s" % (username, tag)
        def assert_url(url):
            assert url == get_post_url
            return Mock({'read': self.basic_response})
        me2day.urllib2.urlopen = assert_url

        posts = me2day.Me2day.posts(username, tag='woc')

    def test_posts_with_from_calls_proper_url(self):
        username = 'jangxyz'
        since = me2day.datetime.fromtimestamp(0)
        get_post_url = "http://me2day.net/api/get_posts/%s.json?from=%s" % (username, me2day.time_iso8601(since))
        def assert_url(url):
            assert url == get_post_url
            return Mock({'read': self.basic_response})
        me2day.urllib2.urlopen = assert_url

        posts = me2day.Me2day.posts(username, since=since)

    def test_posts_with_from_and_to_calls_proper_query(self):
        since = me2day.datetime.fromtimestamp(0)
        until = me2day.datetime.now()
        convert = me2day.time_iso8601
        from_to_query = "from=%s&to=%s" % (convert(since), convert(until))
        def assert_url(url):
            queries = me2day.urllib2.splitquery(url)[-1].split('&')
            queries.sort()
            assert '&'.join(queries) == from_to_query
            return Mock({'read': self.basic_response})
        me2day.urllib2.urlopen = assert_url

        posts = me2day.Me2day.posts('somename', since=since, to=until)

class ParseJsonTestCase(unittest.TestCase):
    def setUp(self):
        self.me2day_response = """[{
            "pubDate":"2009-02-27T00:00:32+0900",
            "me2dayPage":"http:\/\/me2day.net\/jangxyz",
            "commentsCount":1,
            "author":{
                "nickname":"\uae40\uc7a5\ud658",
                "id":"jangxyz",
            },
            "permalink":"http:\/\/me2day.net\/jangxyz\/2009\/02\/27#00:00:32",
            "body":"this is woc!",
            "post_id":"p147x3",
            "tags":[
                {"name":"woc", "url":"url"},
                {"name":"tag1", "url":"http:\/\/me2day.net\/jangxyz\/tag\/tag1" }
            ]
        }]"""

    def set_response(self, response='[]'):
        me2day.urllib2 = Mock({
            "urlopen": Mock({"read": response})
        })

    def test_parsing_me2day_response(self):
        self.set_response(self.me2day_response)
        post = me2day.Me2day.posts('someuser')[0]
        assert post.body == "this is woc!"
        assert post.permalink == "http:\/\/me2day.net\/jangxyz\/2009\/02\/27#00:00:32"

    def test_parsing_nested_me2day_response(self):
        self.set_response(self.me2day_response)
        post = me2day.Me2day.posts('someuser')[0]
        assert post.author.id == "jangxyz"
        assert map(lambda x: x.name, post.tags) == ["woc", "tag1"]

    def test_commentsCount_should_be_integer(self):
        self.set_response(self.me2day_response)
        post = me2day.Me2day.posts('someuser')[0]
        assert post.commentsCount == 1

    def test_pubDate_should_be_datetime(self):
        self.set_response(self.me2day_response)
        post = me2day.Me2day.posts('someuser')[0]
        assert isinstance(post.pubDate, me2day.datetime)
        assert post.pubDate.timetuple()[:6] == (2009, 2, 27, 0, 0, 32)


class Me2dayApiAcceptanceTestCase(unittest.TestCase):
    def test_get_recent_posts_by_username(self):
        user  = 'jangxyz'
        posts = me2day.Me2day.posts(user)
        assert isinstance(posts, list)
        assert isinstance(posts[0].body, str)

    def test_get_recent_posts_by_username_and_tags(self):
        user = 'jangxyz'
        tag = 'woc'
        posts = me2day.Me2day.posts(user, tag=tag)
        assert tag in map(lambda x: x.name, posts[0].tags)


if __name__ == '__main__':
    try:
        import testoob
        unittest.main()
    except ImportError:
        testoob.main()


