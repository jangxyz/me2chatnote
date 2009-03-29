#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib, urllib
import lib.simplejson as json
import lib.oauth as oauth

# consumer token for this application
CONSUMER_TOKEN  = 'CRX0pAbTqsacYKM5G9pA'
CONSUMER_SECRET = 'y98eIzZopkjdKJqqDtZuNgmqknslPKoCDVNRqliP1AU'

class SpringnoteResource:
    attributes = []

    def __init__(self, access_token, parent=None):
        self.access_token = access_token # 모든 request 시에 필요한 access token
        self.resource = None             # 스프링노트의 리소스를 담는 dictionary 
        self.raw      = ''               # request의 결과로 가져온 raw data
        return

    def request(self, path, method="GET", params={}, data=None):
        """ springnote에 request를 보냅니다. 
            SpringnoteResource를 상속 받는 모든 하위클래스에서 사용합니다. """

        url = "http://%s/%s" % (Springnote.BASEURL, path.lstrip('/'))
        headers = {'Content-Type': 'application/json'}
        if data: # set body if any
            data = {self.__class__.__name__.lower(): data}
            data = json.dumps(data, ensure_ascii=False)
            data = data.encode('utf-8')

        conn = Springnote.springnote_request(method, url, params, headers, data, sign_token=self.access_token, secure=False)

        # get response
        response = conn.getresponse()
        if response.status != httplib.OK:
            raise SpringnoteError.find_error(response)

        self.build_from_response(response.read())

    def build_from_response(self, data): 
        self.raw = data
        # build proper object
        object_name = self.__class__.__name__.lower()
        self.resource = json.loads(data)[object_name]

        #
        self.process_resource(self.resource)

        return self.resource

    def process_resource(self, resource_dict):
        """ 각 resource마다 필요한 후처리를 할 수 있다 """
        # set direct accessor
        [setattr(self, key, value) for key, value in resource_dict.iteritems()]
        # unicode
        for key, value in resource_dict.iteritems():
            if isinstance(value, str):
                setattr(self, key, eval('u"""%s"""' % value))
        # alias id
        if "identifier" in resource_dict:
            setattr(self, "id", resource_dict["identifier"])

class Page(SpringnoteResource):
    """ 스프링노트의 page에 대한 정보를 가져오거나, 수정할 수 있습니다.
        page의 하위 리소스에 접근할 수 있도록 해줍니다. """
    attributes = [
        "identifier",           # 페이지 고유 ID  예) 2
        "date_created",         # 페이지 최초 생실 일시(UTC)  예) datetime.datetime(2008, 1, 30, 10, 11, 16)
        "date_modified",        # 페이지 최종 수정 일시(UTC)  예) datetime.datetime(2008, 1, 30, 10, 11, 16)
        "rights",               # 페이지에 설정된 Creative Commons License  예) by-nc
        "creator",              # 페이지 소유자 OpenID
        "contributor_modified", # 최종 수정자 OpenID
        "title",                # 페이지 이름  예) TestPage
        "source",               # 페이지 원본.  예) &lt;p&gt; hello &lt;/p&gt; 
        "relation_is_part_of",  # 이 페이지의 부모 페이지의 ID  예) 2
        "tags"                  # 페이지에 붙은 태그  예) tag1,tag2
    ]
    writable_attributes = ["title", "source", "relation_is_part_of", "tags"]

    def __init__(self, access_token, parent=None):
        SpringnoteResource.__init__(self, access_token, parent)

    def process_resource(self, resource_dict):
        """ tags를 배열로 변환한다 """
        SpringnoteResource.process_resource(self, resource_dict)
        if "tags" in resource_dict:
            self.tags = filter(None, self.tags.split(','))

    def _writable_resources(self):
        writable_resource = {}
        for key, value in self.resource.iteritems():
            if key in self.writable_attributes:
                writable_resource[key] = getattr(self, key)
        if 'tags' in self.resource:
            writable_resource['tags'] = ' '.join(getattr(self, 'tags'))
        return writable_resource

    def save(self):
        """ /pages/:page_id.json에 접근하여 page를 수정합니다. """
        path = "/pages/%d.json" % self.id
        method = "PUT"

        self.request(path, method, data=self._writable_resources())
        return self


class Springnote:
    BASEURL           = 'api.springnote.com'
    REQUEST_TOKEN_URL = 'https://api.springnote.com/oauth/request_token'
    ACCESS_TOKEN_URL  = 'https://api.springnote.com/oauth/access_token/springnote'
    AUTHORIZATION_URL = 'https://api.springnote.com/oauth/authorize'
    signature_method  = oauth.OAuthSignatureMethod_HMAC_SHA1()
    consumer_token    = oauth.OAuthConsumer(CONSUMER_TOKEN, CONSUMER_SECRET)

    def __init__(self, access_token=None):
        # already have an access token
        if access_token:
            self.access_token = oauth.OAuthToken(*access_token)

    @staticmethod
    def springnote_request(method, url, params={}, headers={}, body=None, sign_token=None, secure=True, verbose=False):
        """ Springnote에서 사용하는 request를 생성합니다. 
        일반적인 springnote resource 요청 뿐 아니라 
        oauth 인증을 위해 request token과 access token을 요청할 때도 사용합니다.
        """
        # create oauth request
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(Springnote.consumer_token, sign_token, method, url, params)
        oauth_request.sign_request(Springnote.signature_method, Springnote.consumer_token, sign_token)

        # merge oauth header with user defined
        headers.update(oauth_request.to_header())

        #if verbose:
        #print oauth_request.http_method, oauth_request.http_url, body, headers

        # create http(s) connection and request
        if secure:
            conn = httplib.HTTPSConnection("%s:%d" % (Springnote.BASEURL, 443))
        else:
            conn = httplib.HTTPConnection(Springnote.BASEURL)
        conn.request(oauth_request.http_method, oauth_request.http_url, body=body, headers=headers)
        return conn


    def fetch_request_token(self):
        """ Consumer의 자격으로 Service Provider로부터 request token을 받아온다 """
        conn = self.springnote_request('POST', self.REQUEST_TOKEN_URL)

        response = conn.getresponse()
        if response.status == 401:
            springnote_error = SpringnoteError.find_error(response)
            raise springnote_error
        return oauth.OAuthToken.from_string(response.read())


    def authorize_url(self, token, callback=None):
        """ Consumer의 자격으로 User에게 request token을 승인받을 url """
        ret = "%s?oauth_token=%s" % (self.AUTHORIZATION_URL, token.key)
        if callback:
            ret += "&oauth_callback=%s" % escape(callback)
        return ret


    def fetch_access_token(self, token):
        """ Consumer의 자격으로 Service Provider로부터 access token을 받아온다  """
        conn = self.springnote_request('POST', self.ACCESS_TOKEN_URL, sign_token=token)

        response = conn.getresponse()
        self.access_token = oauth.OAuthToken.from_string(response.read())

        return self.access_token


    def set_access_token(self, token, key):
        """ 직접 access token을 지정한다 """
        self.access_token = oauth.OAuthToken(token, key)
        return self.access_token

    # ---

    def page(self, note, id, params={}):
        """ /pages/:page_id.json에 접근하여 page를 가져옵니다. """
        params['domain'] = note
        path  = "/pages/%d.json" % id
        path += "?%s" % urllib.urlencode(params) if params else ''
        method = "GET"

        new_page = Page(self.access_token)
        new_page.request(path, method, params)
        return new_page

# ---
class SpringnoteError:
    class Base(Exception):
        def __init__(self, error):
            self.error = error
        def __str__(self):
            error_tuple = lambda x: (x["error"]["error_type"], x["error"]["description"])
            error_tuple_str = lambda x: "%s: %s" % error_tuple(x)
            if isinstance(self.error, dict):
                return error_tuple_str(self.error)
            elif isinstance(self.error, list):
                error_msgs = [error_tuple_str(error) for error in self.error]
                return '\n'.join(error_msgs)
            else:
                return self.error
    class Unauthorized(Base): pass
    class NotFound(Base):     pass

    @staticmethod
    def find_error(response):
        body = response.read()
        try:
            errors = json.loads(body)
        except ValueError:
            errors = body
        if response.status == 401:
            return SpringnoteError.Unauthorized(errors)
        elif response.status == 404:
            return SpringnoteError.NotFound(errors)
        else:
            return SpringnoteError.Base(errors)

