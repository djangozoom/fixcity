
# XXX I feel kinda icky importing settings during test
from django.conf import settings

from django.contrib.gis.geos.point import Point
from django.core.cache import cache        

from django.utils import simplejson as json

from django.test import TestCase

from fixcity.bmabr.management.commands import tweeter
from fixcity.bmabr.views import SRID
from fixcity.bmabr.views import _preprocess_rack_form

import lxml.objectify

import datetime
import mock
import unittest

def clear_cache():
    for key in cache._expire_info.keys():
        cache.delete(key)

class TestSourceFactory(unittest.TestCase):

    def test_existing_source(self):
        from fixcity.bmabr.models import Source, TwitterSource
        from fixcity.bmabr.views import source_factory
        existing = Source()
        existing.name = 'misc source'
        existing.save()
        dupe = source_factory({'source': existing.id})
        self.assertEqual(dupe, existing)

        # It should work also with subclasses of Source...
        twit = TwitterSource(status_id=12345, name='twitter')
        twit.save()
        self.assertEqual(twit, source_factory({'source': twit.id}))
        

    def test_twitter_source(self):
        from fixcity.bmabr.views import source_factory
        twit = source_factory({'source_type': 'twitter',
                               'twitter_user': 'bob',
                               'twitter_id': 123})
        self.assertEqual(twit.user, 'bob')
        self.assertEqual(twit.status_id, 123)
        self.assertEqual(twit.get_absolute_url(), 'http://twitter.com/bob/123')

    def test_unknown_source(self):
        from fixcity.bmabr.views import source_factory
        source = source_factory({'source_type': 'anything else'})
        self.assertEqual(source, None)


        
class TestUtilFunctions(unittest.TestCase):

    def tearDown(self):
        clear_cache()
        super(TestUtilFunctions, self).tearDown()
        
    def test_preprocess_rack_form__noop(self):
        orig_data = {'geocoded': '1'}
        data = orig_data.copy()
        _preprocess_rack_form(data)
        self.assertEqual(data, orig_data)

    @mock.patch('geopy.geocoders.Google.geocode')
    def test_preprocess_rack_form__address_but_no_matching_user(self,
                                                                mock_geocode):
        address = '148 Lafayette St, New York, NY'
        mock_geocode.return_value = [(address, (20, 40))]
        data = {'geocoded': '0', 'email': 'foo@bar.com', 'address': address}
        _preprocess_rack_form(data)
        self.failIf(data.has_key('user'))
        self.assertEqual(data['location'],
                         'POINT (40.0000000000000000 20.0000000000000000)')

    @mock.patch('geopy.geocoders.Google.geocode')
    def test_preprocess_rack_form__no_location(self, mock_geocode):
        address = '148 Lafayette St, New York, NY'
        mock_geocode.return_value = []
        data = {'geocoded': '0', 'address': address}
        _preprocess_rack_form(data)
        self.assertEqual(data['location'], u'')

    def test_preprocess_rack_form__with_user(self):
        from fixcity.bmabr.views import _preprocess_rack_form
        data = {'geocoded': '1', 'email': 'foo@bar.com'}
        from django.contrib.auth.models import User
        bob = User(username='bob', email='foo@bar.com')
        bob.save()
        _preprocess_rack_form(data)
        self.assertEqual(data['user'], 'bob')

        
    def test_newrack_no_data(self):
        from fixcity.bmabr.views import _newrack
        from fixcity.bmabr.models import NEED_SOURCE_OR_EMAIL
        result = _newrack({}, {})
        self.failUnless(result.has_key('errors'))
        self.assertEqual(result['errors']['title'],
                         [u'This field is required.'])
        self.assertEqual(result['errors']['address'],
                         [u'This field is required.'])
        self.assertEqual(result['errors']['date'],
                         [u'This field is required.'])
        self.assertEqual(result['errors']['__all__'], [NEED_SOURCE_OR_EMAIL])
        self.assertEqual(result['rack'], None)

    def test_newrack_with_email_but_no_source(self):
        from fixcity.bmabr.views import _newrack
        result = _newrack({'email': 'joe@blow.com'}, {})
        self.assertEqual(result['errors'].get('email'), None)
        self.assertEqual(result['errors'].get('__all__'), None)
        self.assertEqual(result['errors'].get('source'), None)

    def test_newrack_with_bad_source_but_no_email(self):
        from fixcity.bmabr.views import _newrack
        from fixcity.bmabr.models import NEED_SOURCE_OR_EMAIL
        from fixcity.bmabr.models import NEED_LOGGEDIN_OR_EMAIL
        result = _newrack({'source': 999999999}, {})
        self.assertEqual(
            result['errors'].get('source'),
            [u'Select a valid choice. That choice is not one of the available choices.'])
        self.assertEqual(result['errors'].get('email'), [NEED_LOGGEDIN_OR_EMAIL])
        self.assertEqual(result['errors'].get('__all__'), [NEED_SOURCE_OR_EMAIL])

    def test_newrack_working(self):
        from fixcity.bmabr.views import _newrack
        from fixcity.bmabr.models import Source
        source = Source()
        source.name = 'unknown source type'
        source.save() # needed to get an ID
        result = _newrack({'title': 'footitle',
                           'address': '123 W 12th st, New York, NY',
                           'date': '2009-11-18 12:33',
                           'source': source.id,
                           'location': Point(20.0, 20.0, srid=SRID),
                           }, {})
        self.assertEqual(result['errors'], {})
        self.failUnless(result.get('message'))
        self.failUnless(result.get('rack'))



class TestActivation(TestCase):

    def test_activate__malformed_key(self):
        response = self.client.get('/accounts/activate/XYZPDQ/')
        self.assertEqual(response.status_code, 200)
        self.failUnless(response.context['key_status'].count('Malformed'))

    # lots more to test in this view!


class TestTweeter(unittest.TestCase):

    def test_parse(self):
        username = 'fixcity_testing'
        class StubTweet:
            # for something this trivial, the Mock API is more trouble.
            text = '@%s an address #bikerack a title' % username
            created_at = datetime.datetime.utcfromtimestamp(0)
            id = 123
            class user:
                screen_name = 'bob'
        fetcher = tweeter.TwitterFetcher(None, username)
        self.assertEqual(fetcher.parse(StubTweet),
                         {'date': datetime.datetime(1970, 1, 1, 0, 0),
                          'address': 'an address',
                          'tweetid': 123,
                          'user': 'bob',
                          'title': 'a title'})

    def test_newrack_json_twitter(self):
        from fixcity.bmabr.views import newrack_json

        class MockRequest:

            method = 'POST'
            POST = {}
            raw_post_data = json.dumps(dict(
                title='foo title',
                description='foo description',
                date='2009-11-18 15:14',
                address='148 Lafayette St, New York, NY',
                geocoded=1,  # Skip server-side geocoding.
                location=str(Point(-73.999548, 40.719545, srid=SRID)),
                source_type='twitter',
                twitter_user='TwitterJoe',
                twitter_id=456,
                ))

        response = newrack_json(MockRequest)
        data = json.loads(response._get_content())
        self.failUnless(data.has_key('photo_post_url'))
        self.failUnless(type(data.get('rack')) == int)
        self.failUnless(data.has_key('user'))
        self.failUnless(data.has_key('message'))
        
    
    @mock.patch('fixcity.bmabr.management.commands.tweeter.RackBuilder.new_rack')
    @mock.patch('tweepy.API')
    def test_main(self, MockTweepyAPI, mock_new_rack):
        tweepy_mock = MockTweepyAPI()
        user = settings.TWITTER_USER
        builder = tweeter.RackBuilder(settings, tweepy_mock)
        # The Mock API works OK but setting attrs is a bit tedious...
        # i wish you could pass a dict as the spec argument.
        status = mock.Mock(['id', 'text', 'user', 'created_at'])
        status.id = 1
        status.text = '@%s 13 thames st, brooklyn, ny #bikerack mention ' % user
        status.user = mock.Mock(['screen_name'])
        status.user.screen_name = 'some twitter user'
        status.created_at = datetime.datetime.utcfromtimestamp(0)
        tweepy_mock.mentions.return_value = [status]
        tweepy_mock.direct_messages.return_value = []
        tweepy_mock.rate_limit_status.return_value = {'remaining_hits': 999}

        builder.main(False)
        self.assertEqual(mock_new_rack.call_count, 1)
        self.assertEqual(mock_new_rack.call_args,
                         ((),
                          {'address': '13 thames st, brooklyn, ny',
                           'date': datetime.datetime(1970, 1, 1, 0, 0),
                           'title': 'mention',
                           'tweetid': 1,
                           'user': 'some twitter user',
                           }))


class TestKMLViews(TestCase):

        
    def tearDown(self):
        super(TestKMLViews, self).tearDown()
        clear_cache()
                
    def test_rack_requested_kml__empty(self):
        kml = self.client.get('/rack/requested.kml').content
        # This is maybe a bit goofy; we parse the output to test it
        tree = lxml.objectify.fromstring(kml)
        placemarks = tree.Document.getchildren()
        self.assertEqual(len(placemarks), 0)

        
    def test_rack_requested_kml__one(self):
        from fixcity.bmabr.models import Rack
        rack = Rack(address='148 Lafayette St, New York NY',
                    title='TOPP', date=datetime.datetime.utcfromtimestamp(0),
                    email='john@doe.net', location=Point(20.0, 20.0, srid=SRID),
                    )
        rack.save()
        kml = self.client.get('/rack/requested.kml').content
        tree = lxml.objectify.fromstring(kml)
        placemarks = tree.Document.getchildren()
        self.assertEqual(len(placemarks), 1)
        placemark = tree.Document.Placemark
        self.assertEqual(placemark.name, rack.title)
        self.assertEqual(placemark.address, rack.address)
        self.assertEqual(placemark.description, '')
        
        self.assertEqual(placemark.Point.coordinates, '20.0,20.0,0')

        # Argh. Searching child elements for specific attribute values
        # is making my head hurt. xpath should help, but I couldn't
        # find the right expression. Easier to extract them into a
        # dict.
        data = {}
        for d in placemark.ExtendedData.Data:
            data[d.attrib['name']] = d.value

        self.assertEqual(data['page_number'], 1)
        self.assertEqual(data['num_pages'], 1)
        self.assertEqual(data['source'], 'web')
        self.assertEqual(data['date'], 'Jan. 1, 1970')
        self.assertEqual(data['votes'], 0)

