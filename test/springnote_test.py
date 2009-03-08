#!/usr/bin/python
# coding: utf-8

import unittest
from lib.mock import Mock
import springnote

class SpringnoteRequestTestCase(unittest.TestCase):
    def test_korean_must_be_preserved(self):
        pass

class OAuthTestCase(unittest.TestCase):
    def set_https_connection_response_for_request_token(self, response_mock=None):
        if response_mock is None:
            response_mock = Mock({'read': "oauth_token=cd&oauth_token_secret=ab&open_id=http%3A%2F%2Fchanju.myid.net%2F"})

        springnote.httplib = Mock({
            'HTTPSConnection': Mock({
                'request':     None,
                'getresponse': response_mock
            })
        })         

    @staticmethod
    def should_behave_like_oauth_header(cls, header):
        """ behaving like oauth header means 
            it has proper keys for oauth authorization """
        cls.assertTrue('Authorization' in header)
        key_values = header['Authorization'].split(', ')
        oauth_header = dict([kv.split('=') for kv in key_values])

        oauth_keys = ['OAuth realm', 'oauth_nonce', 'oauth_timestamp', 'oauth_consumer_key', 'oauth_signature_method', 'oauth_version', 'oauth_token', 'oauth_signature']
        oauth_keys.sort()
        oauth_header_keys = oauth_header.keys()
        oauth_header_keys.sort()
        cls.assertEqual(oauth_header_keys, oauth_keys)

        #for key in ['OAuth realm', 'oauth_nonce', 'oauth_timestamp', 
        #            'oauth_consumer_key', 'oauth_signature_method', 
        #            'oauth_version', 'oauth_token', 'oauth_signature']:
        #    print key, oauth_header
        #    cls.assertTrue(key in oauth_header)

    def setUp(self):
        self.client = springnote.Springnote()

    def test_oauth_consumer_token(self):
        ''' Springnote should have OAuthConsumer instance consumer,
            that have token key and token secret '''
        self.assertTrue(isinstance(self.client.consumer_token.key, str))
        self.assertTrue(isinstance(self.client.consumer_token.secret, str))
        
    def test_fetching_request_token_receives_proper_data(self):
        self.set_https_connection_response_for_request_token()
            
        data = self.client.fetch_request_token()
        self.assertEqual(type(data), springnote.oauth.OAuthToken)
        self.assertEqual(type(data.key), str)
        self.assertEqual(type(data.secret), str)
        
    def test_fetching_request_token_raises_not_authorized_exception_when_token_is_wrong(self):
        """ raise exception when unauthorized """
        # set mock for http request response
        response_mock = Mock({'read': "Invalid OAuth Request (signature_invalid, base string: POST&https%3A%2F%2Fapi.springnote.com%2Foauth%2Frequest_token&oauth_consumer_key%3Dsome%252Bconsumer%252Btoken%252Bkey%26oauth_nonce%3D39982135%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1234870498%26oauth_version%3D1.0)"})
        response_mock.status = 401
        self.set_https_connection_response_for_request_token(response_mock)
        
        self.assertRaises(springnote.SpringnoteError.Unauthorized, self.client.fetch_request_token)
        
    def test_fetching_access_token_receives_proper_data(self):
        self.set_https_connection_response_for_request_token()
            
        request_token = self.client.fetch_request_token()
        data = self.client.fetch_access_token(request_token)
        self.assertEqual(type(data), springnote.oauth.OAuthToken)
        self.assertEqual(type(data.key), str)
        self.assertEqual(type(data.secret), str)
        

    def test_oauth_directly_set_access_token(self):
        """ should directly set access token """
        key, secret = "yz", "uF"
        access_token = self.client.set_access_token(key,secret)

        self.assertEqual(access_token.key, self.client.access_token.key)
        self.assertEqual(access_token.secret, self.client.access_token.secret)

    def test_can_intialize_with_access_token(self):
        key, secret = "yz", "uF"
        client = springnote.Springnote((key, secret))

        self.assertEqual(client.access_token.key, key)
        self.assertEqual(client.access_token.secret, secret)

    def test_oauth_request_makes_oauth_header(self):
        access_token_tuple = ("yz", "uF")
        access_token = self.client.set_access_token(*access_token_tuple)
        oauth_request = springnote.oauth.OAuthRequest.from_consumer_and_token(self.client.consumer_token, token=self.client.access_token, http_url='http://some.com/url/')
        oauth_request.sign_request(self.client.signature_method, self.client.consumer_token, self.client.access_token)
        
        # oauth header
        self.should_behave_like_oauth_header(self, oauth_request.to_header())


class PageTestHelper:
    @staticmethod
    def response_data(page_id=3, title='testing springnote api', source='test source', tags=['test','springnote']):
        return """{
            "page": {
                "identifier": %d, 
                "uri": "http://jangxyz.springnote.com/pages/%d", 
                "title": "%s", 
                "source": "%s", 
                "tags": "%s", 
                "relation_is_part_of": 49, 
                "date_created": "2009/02/25 10:27:16 +0000", 
                "version": 22, 
                "creator": "http://jangxyz.myid.net/", 
                "contributor_modified": "http://jangxyz.myid.net/", 
                "date_modified": "2009/02/27 15:01:56 +0000", 
                "rights": null
            }
        }""" % (page_id, page_id, title, source, ','.join(tags))

    @staticmethod
    def response_mock(read=None, status=200):
        if read is None:
            read = PageTestHelper.response_data()

        mock = Mock({'read': read})
        mock.status = status
        return mock

    @staticmethod
    def http_connection_mock(request=None, getresponse=None):
        if getresponse is None:
            getresponse = PageTestHelper.response_mock()

        mock = Mock({
            'request':     request,
            'getresponse': getresponse
        })
        return mock
    
    @staticmethod
    def set_httplib_mock(response_data=None, http_connection=None, connection_type='http'):
        response_mock = PageTestHelper.response_mock(response_data)
        if http_connection is None:
            http_connection = PageTestHelper.http_connection_mock(getresponse=response_mock)

        connection_type = 'HTTPSConnection' if connection_type.lower() == 'https' else 'HTTPConnection'

        # set httplib mock
        springnote.httplib = Mock({
            connection_type: http_connection
        })         
        springnote.httplib.OK = 200

    @staticmethod
    def build_page_and_return_with_connection(access_token, page_id=3, title='testing springnote api', source='test source', tags=['test','springnote']):
        response_data = PageTestHelper.response_data(page_id, title, source, tags)
        response_mock = PageTestHelper.response_mock(response_data)
        connection_mock = PageTestHelper.http_connection_mock(response_mock)
        httplib_mock = PageTestHelper.set_httplib_mock(http_connection=connection_mock)
        
        page = springnote.Page(access_token)
        page.build_from_response(response_data)
        return (page, connection_mock)

    @staticmethod
    def should_behave_like_json_body_for_writable_resource(cls, json_body):
        body = springnote.json.loads(json_body)
        cls.assertTrue('page' in body)
        body_inside = body['page']
        for attr in springnote.Page.writable_attributes:
            cls.assertTrue(attr in body_inside)


class GetPageBySpringnoteApiTestCase(unittest.TestCase):
    def setUp(self):
        self.note    = 'springmemo'
        self.page_id = 3
        response_data = PageTestHelper.response_data(self.page_id)
        PageTestHelper.set_httplib_mock(response_data)

        self.access_token = ('ACCESS', 'TOKEN')
        self.client = springnote.Springnote(self.access_token)

    def test_fetching_page_by_id_should_have_correct_id(self):
        page = self.client.page(note=self.note, id=self.page_id)
        self.assertEqual(page.id, self.page_id)
        self.assertTrue(isinstance(page.source, unicode))

    def test_page_should_have_id_as_alias_to_identifier(self):
        page = self.client.page(note=self.note, id=self.page_id)
        self.assertEqual(page.id, page.identifier, ".id seems to be not set")

    def test_tags_in_page_should_be_list(self):
        page = self.client.page(note=self.note, id=self.page_id)
        self.assertTrue(isinstance(page.tags, list), "tags must be a list, but got '%s'" % page.tags)
        self.assertEqual(page.tags, ["test", "springnote"])

    def test_should_convert_to_proper_unicode(self):
        response_data = PageTestHelper.response_data(source='\\ud55c\\uae00')
        response_mock = PageTestHelper.response_mock(response_data)

        page = springnote.Page(self.access_token)
        page.build_from_response(response_data)
        self.assertEqual(page.source, u'\ud55c\uae00')


class SetPageBySpringnoteApiTestCase(unittest.TestCase):
    def setUp(self):
        access_token = ('Ac', 'cS')
        client = springnote.Springnote(access_token)
        self.access_token = client.access_token

    def test_saving_page_sends_proper_request(self):
        page_id = 3
        page, http_connection_mock = PageTestHelper.build_page_and_return_with_connection(self.access_token, page_id=page_id, source='something old')

        new_source = "something new"
        self.assertNotEqual(page.source, new_source)
        page.source = new_source
        page.save()

        #
        request = http_connection_mock.mockGetNamedCalls('request')[0]
        self.assertEqual(request.getParam(0), 'PUT')
        self.assertEqual(request.getParam(1), "http://api.springnote.com/pages/%d.json" % page_id)
        # body is json form of Page writable attributes
        PageTestHelper.should_behave_like_json_body_for_writable_resource(self, request.getParam('body'))
        # request header behaves like oauth header - it actually is
        OAuthTestCase.should_behave_like_oauth_header(self, request.getParam('headers'))

    def test_saving_unicode_encodes_to_proper_encoding(self):
        page, http_connection_mock = PageTestHelper.build_page_and_return_with_connection(self.access_token)

        source = u"한글"
        encoded_source = source.encode('utf-8') # '\xed\x95\x9c\xea\xb8\x80'
        page.source = source
        page.save()

        #
        request = http_connection_mock.mockGetNamedCalls('request')[0]
        self.assertTrue(encoded_source in request.getParam('body'))


class ExceptionTestCase(unittest.TestCase):
    def test_no_network_raises_exception(self):
        pass


if __name__ == '__main__':
    #unittest.main()
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test'
    unittest.main(testLoader = loader)


