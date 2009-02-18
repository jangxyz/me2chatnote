#!/usr/bin/python
# coding: utf-8

import unittest
from me2day import Me2day
from me2day import OpenStruct

class ParseJsonTestCase(unittest.TestCase):
    pass

class OpenStructTestCase(unittest.TestCase):
    def test_parse_dictionary_to_object(self):
        d = {
            'tags': ['woc', 'abc', 'def'], 
            'ooo': 'xxx'
        }
        o = OpenStruct.parse(d)
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
        os = OpenStruct.parse(ds)
        assert isinstance(os, list)
        assert isinstance(os[0], OpenStruct)
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
        o = OpenStruct.parse(d)
        assert isinstance(o.nested, OpenStruct)
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
        o = OpenStruct.parse(d)
        assert isinstance(o.nested[0], OpenStruct)
        assert o.nested[0].url == d['nested'][0]['url']

    
class Me2dayApiTestCase(unittest.TestCase):
    def test_get_recent_posts_by_username(self):
        user  = 'jangxyz'
        posts = Me2day.posts(username=user)
        assert isinstance(posts, list)
        assert isinstance(posts[0].body, str)

    def test_get_recent_posts_by_username_and_tags(self):
        user = 'jangxyz'
        tag = 'woc'
        posts = Me2day.posts(username=user, tag=tag)
        assert tag in map(lambda x: x.name, posts[0].tags)
        
    def test_encode_korean_correctly(self):
        result = "\\ud55c\\uae00"
        assert Me2day.convert(result) == u"\ud55c\uae00"


#class GetPageBySpringnoteApiTestCase(unittest.TestCase):
#    def test_get_springnote_page_by_page_id(self):
#        note = 'springmemo'
#        page_id = 3
#        page = Springnote.page(note=note, page_id=page_id)
#        page.source
#
#class SetPageBySpringnoteApiTestCase(unittest.TestCase):
#    def test_set_springnote_page(self):
#        note = 'springmemo'
#        page_id = 3
#        page = Springnote.page(note=note, page_id=page_id)
#        page.source = "something new"
#        page.save()

if __name__ == '__main__':
    unittest.main()

