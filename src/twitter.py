import logging
import base64
import json
import requests

from datetime import datetime

class Twitter:
    TIMEOUT = 10

    ENDPOINTS = {
        # resource:                                (method, subdomain)

        'statuses/filter':                         ('POST', 'stream'),
        'statuses/firehose':                       ('GET',  'stream'),
        'statuses/sample':                         ('GET',  'stream'),
        'site':                                    ('GET',  'sitestream'),
        'user':                                    ('GET',  'userstream'),

        'account/remove_profile_banner':           ('POST', 'api'),
        'account/settings':                        ('GET',  'api'),
        'account/update_delivery_device':          ('POST', 'api'),
        'account/update_profile':                  ('POST', 'api'),
        'account/update_profile_background_image': ('POST', 'api'),
        'account/update_profile_banner':           ('POST', 'api'),
        'account/update_profile_colors':           ('POST', 'api'),
        'account/update_profile_image':            ('POST', 'api'),
        'account/verify_credentials':              ('GET',  'api'),

        'application/rate_limit_status':           ('GET',  'api'),

        'blocks/create':                           ('POST', 'api'),
        'blocks/destroy':                          ('POST', 'api'),
        'blocks/ids':                              ('GET',  'api'),
        'blocks/list':                             ('GET',  'api'),

        'direct_messages':                         ('GET',  'api'),
        'direct_messages/destroy':                 ('POST', 'api'),
        'direct_messages/new':                     ('POST', 'api'),
        'direct_messages/sent':                    ('GET',  'api'),
        'direct_messages/show':                    ('GET',  'api'),

        'favorites/create':                        ('POST', 'api'),
        'favorites/destroy':                       ('POST', 'api'),
        'favorites/list':                          ('GET',  'api'),

        'followers/ids':                           ('GET',  'api'),
        'followers/list':                          ('GET',  'api'),

        'friends/ids':                             ('GET',  'api'),
        'friends/list':                            ('GET',  'api'),

        'friendships/create':                      ('POST', 'api'),
        'friendships/destroy':                     ('POST', 'api'),
        'friendships/incoming':                    ('GET',  'api'),
        'friendships/lookup':                      ('GET',  'api'),
        'friendships/no_retweets/ids':             ('GET',  'api'),
        'friendships/outgoing':                    ('GET',  'api'),
        'friendships/show':                        ('GET',  'api'),
        'friendships/update':                      ('POST', 'api'),

        'lists/create':                            ('POST', 'api'),
        'lists/destroy':                           ('POST', 'api'),
        'lists/list':                              ('GET',  'api'),
        'lists/members':                           ('GET',  'api'),
        'lists/members/create':                    ('POST', 'api'),
        'lists/members/create_all':                ('POST', 'api'),
        'lists/members/destroy':                   ('POST', 'api'),
        'lists/members/destroy_all':               ('POST', 'api'),
        'lists/members/show':                      ('GET',  'api'),
        'lists/memberships':                       ('GET',  'api'),
        'lists/ownerships':                        ('GET',  'api'),
        'lists/show':                              ('GET',  'api'),
        'lists/statuses':                          ('GET',  'api'),
        'lists/subscribers':                       ('GET',  'api'),
        'lists/subscribers/create':                ('POST', 'api'),
        'lists/subscribers/destroy':               ('POST', 'api'),
        'lists/subscribers/show':                  ('GET',  'api'),
        'lists/subscriptions':                     ('GET',  'api'),
        'lists/update':                            ('POST', 'api'),

        'media/upload':                            ('POST', 'upload'),

        'mutes/users/create':                      ('POST', 'api'),
        'mutes/users/destroy':                     ('POST', 'api'),
        'mutes/users/ids':                         ('GET',  'api'),
        'mutes/users/list':                        ('GET',  'api'),

        'geo/id/:PARAM':                           ('GET',  'api'),  # PLACE_ID
        'geo/place':                               ('POST', 'api'),
        'geo/reverse_geocode':                     ('GET',  'api'),
        'geo/search':                              ('GET',  'api'),
        'geo/similar_places':                      ('GET',  'api'),

        'help/configuration':                      ('GET',  'api'),
        'help/languages':                          ('GET',  'api'),
        'help/privacy':                            ('GET',  'api'),
        'help/tos':                                ('GET',  'api'),

        'saved_searches/create':                   ('POST', 'api'),
        'saved_searches/destroy/:PARAM':           ('POST', 'api'),  # ID
        'saved_searches/list':                     ('GET',  'api'),
        'saved_searches/show/:PARAM':              ('GET',  'api'),  # ID

        'search/tweets':                           ('GET',  'api'),

        'statuses/destroy/:PARAM':                 ('POST', 'api'),  # ID
        'statuses/home_timeline':                  ('GET',  'api'),
        'statuses/lookup':                         ('GET',  'api'),
        'statuses/mentions_timeline':              ('GET',  'api'),
        'statuses/oembed':                         ('GET',  'api'),
        'statuses/retweet/:PARAM':                 ('POST', 'api'),  # ID
        'statuses/retweeters/ids':                 ('GET',  'api'),
        'statuses/retweets/:PARAM':                ('GET',  'api'),  # ID
        'statuses/retweets_of_me':                 ('GET',  'api'),
        'statuses/show/:PARAM':                    ('GET',  'api'),  # ID
        'statuses/user_timeline':                  ('GET',  'api'),
        'statuses/update':                         ('POST', 'api'),
        'statuses/update_with_media':              ('POST', 'api'),  # [deprecated]

        'trends/available':                        ('GET',  'api'),
        'trends/closest':                          ('GET',  'api'),
        'trends/place':                            ('GET',  'api'),

        'users/contributees':                      ('GET',  'api'),
        'users/contributors':                      ('GET',  'api'),
        'users/lookup':                            ('GET',  'api'),
        'users/profile_banner':                    ('get'   'api'),
        'users/report_spam':                       ('POST', 'api'),
        'users/search':                            ('GET',  'api'),
        'users/show':                              ('GET',  'api'),
        'users/suggestions':                       ('GET',  'api'),
        'users/suggestions/:PARAM':                ('GET',  'api'),  # SLUG
        'users/suggestions/:PARAM/members':        ('GET',  'api')   # SLUG
    }

    def __init__(self, session):
        self.session = session
    
    def _infer_method(self, resource):
        if ':' in resource:
            parts = resource.split('/')
            parts = [k if k[0] != ':' else ':PARAM' for k in parts]
            endpoint = '/'.join(parts)
        else:
            endpoint = resource

        (method, subdomain) = self.ENDPOINTS[endpoint]
        return method

    def request(self, resource, params=None):
        method = self._infer_method(resource)
        data = None

        if 'POST' is method:
            data = params
            params = None

        return self.session.request(method, 'https://api.twitter.com/1.1/%s.json' % (resource), data=data, params=params, timeout=self.TIMEOUT)

class OAuth2TokenInjector(requests.auth.AuthBase):
    def __init__(self, access_token):
        self.access_token = access_token
    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer %s' % (self.access_token,)
        return request

def twitter_from_credentials(key, secret):
    token_url = 'https://api.twitter.com/oauth2/token'
    auth_step_one = key + ':' + secret
    auth_step_two = base64.b64encode(auth_step_one.encode('utf8'))
    auth_step_three = auth_step_two.decode('utf8')
    params = dict()
    params['grant_type'] = 'client_credentials'

    headers = dict()
    headers['User-Agent'] = 'Jacob Greenleaf <greenleaf.jacob@gmail.com> TwitterAPI 1.0'
    headers['Authorization'] = 'Basic ' + auth_step_three
    headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'

    response = requests.post(token_url, params=params, headers=headers)
    response_json = json.loads(response.text)

    if 'access_token' in response_json:
        access_token = response_json['access_token']
        return twitter_from_token(access_token)
    else:
        logging.exception("Got HTTP %d when trying to grab access token but no access token found. Body: %s", response.status_code, response.text)
        raise Exception("Erorr getting access token. HTTP %d" % (response.status_code,))


def twitter_from_token(access_token):
    tokeninjector = OAuth2TokenInjector(access_token)
    session = requests.Session()
    session.auth = tokeninjector
    return Twitter(session)

