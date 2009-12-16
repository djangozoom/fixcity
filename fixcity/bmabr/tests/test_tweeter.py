# XXX I feel kinda icky importing settings during test
from django.conf import settings

from django.contrib.gis.geos.point import Point
from django.core.cache import cache        

from django.utils import simplejson as json

from fixcity.bmabr.management.commands import tweeter
from fixcity.bmabr.views import SRID

import datetime
import mock
import unittest


def clear_cache():
    for key in cache._expire_info.keys():
        cache.delete(key)


class TestTweeter(unittest.TestCase):

    username = 'fixcity_testing'

    class StubTweet:
        # for something this trivial, the Mock API is more trouble.
        text = '@fixcity_testing an address #bikerack a title'
        created_at = datetime.datetime.utcfromtimestamp(0)
        id = 123
        class user:
            screen_name = 'bob'

    def test_parse(self):
        fetcher = tweeter.TwitterFetcher(None, self.username)
        self.assertEqual(fetcher.parse(self.StubTweet),
                         {'date': datetime.datetime(1970, 1, 1, 0, 0),
                          'address': 'an address',
                          'tweetid': 123,
                          'user': 'bob',
                          'title': 'a title'})

    @mock.patch('logging.Logger.warn')
    def test_parse_invalid(self, mock_logger_warn):
        fetcher = tweeter.TwitterFetcher(None, self.username)
        self.StubTweet.text = 'invalid format'
        self.assertEqual(fetcher.parse(self.StubTweet), None)
        
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
        
    @mock.patch('tweepy.API.mentions')
    def test_get_tweets__server_error(self, mock_mentions):
        import tweepy
        mock_mentions.side_effect = tweepy.error.TweepError('500 or something')
        fetcher = tweeter.TwitterFetcher(tweepy.API(), self.username)
        self.assertEqual(fetcher.get_tweets(), [])


    @mock.patch('tweepy.API.mentions')
    def test_get_tweets__empty(self, mock_mentions):
        import tweepy
        mock_mentions.return_value = []
        fetcher = tweeter.TwitterFetcher(tweepy.API(), self.username)
        self.assertEqual(fetcher.get_tweets(), [])

    @mock.patch('tweepy.API.mentions')
    def test_get_tweets__pages(self, mock_mentions):
        import tweepy

        class StubTweet:
            def __init__(self, id):
                self.id = id

        def get_mock_tweet_results(count=1, page=1, *args, **kw):
            # A little helper to simulate the twitter mentions()
            # API.  We'll arbitrarily say that there are 207 total
            # results; 200 in the first page, 7 in the second.
            start = count * (page - 1)
            if page == 2:
                count = 7
            elif page > 2:
                return []
            results = [StubTweet(i) for i in range(start, start + count)]
            return results
                
        mock_mentions.side_effect = get_mock_tweet_results
        fetcher = tweeter.TwitterFetcher(tweepy.API(), self.username)
        results = fetcher.get_tweets()
        self.assertEqual(len(results), 207)
        self.assertEqual(mock_mentions.call_count, 2)

    @mock.patch('tweepy.API')
    @mock.patch('__builtin__.open')
    def test_load_last_status(self, mock_open, MockTweepyAPI):
        import StringIO, pickle
        mock_open.return_value = StringIO.StringIO(
            pickle.dumps({'last_processed_id': 99}))
        builder = tweeter.RackBuilder(settings, MockTweepyAPI())
        self.assertEqual(builder.load_last_status(True), 99)
        self.assertEqual(builder.load_last_status(False), None)

        mock_open.side_effect = IOError("no such file")
        self.assertEqual(builder.load_last_status(True), None)
        
    @mock.patch('tweepy.API')
    def test_main__twitter_down(self, MockTweepyAPI):
        import tweepy
        tweepy_mock = MockTweepyAPI()
        tweepy_mock.rate_limit_status.side_effect = tweepy.error.TweepError(
            "server down?")
        builder = tweeter.RackBuilder(settings, tweepy_mock)
        builder.main()
        self.assertEqual(tweepy_mock.get_tweets.call_count, 0)

    @mock.patch('tweepy.API')
    def test_main__over_limit(self, MockTweepyAPI):
        tweepy_mock = MockTweepyAPI()
        tweepy_mock.rate_limit_status.return_value = {
            'remaining_hits': 0, 'reset_time': 'tomorrow'}
        builder = tweeter.RackBuilder(settings, tweepy_mock)
        self.assertRaises(Exception, builder.main)

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

    @mock.patch('tweepy.API')
    def test_bounce(self, MockTweepyAPI):
        tweepy_mock = MockTweepyAPI()
        builder = tweeter.RackBuilder(settings, tweepy_mock)
        builder.bounce('somebody', 'an interesting message')
        self.assertEqual(tweepy_mock.update_status.call_args,
                         (('@somebody an interesting message',), {})) 

    @mock.patch('tweepy.API')
    def test_bounce__twitter_down(self, MockTweepyAPI):
        tweepy_mock = MockTweepyAPI()
        builder = tweeter.RackBuilder(settings, tweepy_mock)
        import tweepy
        tweepy_mock.update_status.side_effect = tweepy.error.TweepError(
            "server down?")
        builder.bounce('somebody else', 'twitter down?')
        # ... umm... nothing interesting to test here?

    @mock.patch('logging.Logger.info')
    @mock.patch('fixcity.bmabr.management.commands.tweeter.send_mail')
    @mock.patch('tweepy.API')
    def test_bounce__notify_admin(self, MockTweepyAPI, mock_send_mail,
                                  mock_info):
        tweepy_mock = MockTweepyAPI()
        builder = tweeter.RackBuilder(settings, tweepy_mock)
        message = 'a message!'
        subject = 'this is not my day.'
        builder.bounce('somebody', message, notify_admin=subject)
        args = mock_send_mail.call_args
        self.assertEqual(args[0][0], 'FixCity tweeter bounce! %s' % subject)
        self.failUnless(args[0][1].count('Bouncing to: somebody'))

        builder.bounce('somebody', message, notify_admin=subject,
                       notify_admin_body='more body')
        args = mock_send_mail.call_args
        self.failUnless(args[0][1].count('more body'))



    @mock.patch('fixcity.bmabr.management.commands.tweeter.shorten_url')
    @mock.patch('logging.Logger.info')
    @mock.patch('fixcity.bmabr.management.commands.tweeter.http')
    @mock.patch('tweepy.API')
    def test_new_rack(self, MockTweepyAPI, mock_http, mock_info, mock_shorten):
        tweepy_mock = MockTweepyAPI()
        builder = tweeter.RackBuilder(settings, tweepy_mock)
        class StubResponse:
            status = 200
        mock_http.request.return_value = (StubResponse(), '{"rack": 99}')
        mock_shorten.return_value = 'http://short_url/'
        builder.new_rack('TITLE', 'ADDRESS', 'USER', 'DATE', 123)

        self.assertEqual(mock_http.request.call_count, 1)
        args = mock_http.request.call_args
        self.assert_(args[0][0].startswith('http'))
        self.assertEqual(args[0][1], 'POST')
        self.assertEqual(args[1]['headers'],
                         {'Content-type': 'application/json'})
        from django.utils import simplejson as json
        decoded = json.loads(args[1]['body'])
        self.assertEqual(decoded['address'], 'ADDRESS')
        self.assertEqual(decoded['date'], 'DATE')
        self.assertEqual(decoded['description'], '')
        self.assertEqual(decoded['geocoded'], 0)
        self.assertEqual(decoded['source_type'], 'twitter')
        self.assertEqual(decoded['title'], 'TITLE')
        self.assertEqual(decoded['twitter_id'], 123)
        self.assertEqual(decoded['twitter_user'], 'USER')

        # We notified the user too.
        self.assertEqual(tweepy_mock.update_status.call_count, 1)


    @mock.patch('fixcity.bmabr.management.commands.tweeter.shorten_url')
    @mock.patch('logging.Logger.info')
    @mock.patch('fixcity.bmabr.management.commands.tweeter.http')
    @mock.patch('tweepy.API')
    def test_new_rack__errors(self, MockTweepyAPI, mock_http, mock_info,
                              mock_shorten):
        tweepy_mock = MockTweepyAPI()
        builder = tweeter.RackBuilder(settings, tweepy_mock)
        class StubResponse:
            status = 200
        mock_http.request.return_value = (StubResponse(), '{"errors": "any"}')
        mock_shorten.return_value = 'http://short_url/'
        builder.new_rack('TITLE', 'ADDRESS', 'USER', 'DATE', 123)

        self.assertEqual(mock_http.request.call_count, 1)

        # We notified the user too.
        self.assertEqual(tweepy_mock.update_status.call_count, 1)
        notify_args = tweepy_mock.update_status.call_args
        self.assert_(notify_args[0][0].count('something went wrong'))

    @mock.patch('logging.Logger.info')
    @mock.patch('fixcity.bmabr.management.commands.tweeter.RackBuilder.bounce')
    @mock.patch('fixcity.bmabr.management.commands.tweeter.http')
    @mock.patch('tweepy.API')
    def test_new_rack__server_error(self, MockTweepyAPI, mock_http,
                                    mock_bounce, mock_info):
        tweepy_mock = MockTweepyAPI()
        builder = tweeter.RackBuilder(settings, tweepy_mock)
        class StubResponse:
            status = 500
        mock_http.request.return_value = (StubResponse(), 'content')
        builder.new_rack('TITLE', 'ADDRESS', 'USER', 'DATE', 123)
        self.assertEqual(mock_bounce.call_count, 1)

    @mock.patch('logging.Logger.info')
    @mock.patch('fixcity.bmabr.management.commands.tweeter._notify_admin')
    @mock.patch('fixcity.bmabr.management.commands.tweeter.http')
    @mock.patch('tweepy.API')
    def test_new_rack__network_error(self, MockTweepyAPI, mock_http,
                                     mock_notify_admin, mock_info):
        tweepy_mock = MockTweepyAPI()
        builder = tweeter.RackBuilder(settings, tweepy_mock)
        import socket
        mock_http.request.side_effect = socket.error('oops')
        self.assertRaises(socket.error, builder.new_rack,
                          'TITLE', 'ADDRESS', 'USER', 'DATE', 123)
        self.assertEqual(mock_notify_admin.call_count, 1)

    @mock.patch('fixcity.bmabr.management.commands.tweeter.api_factory')
    @mock.patch('fixcity.bmabr.management.commands.tweeter.RackBuilder.main')
    def test_command(self, mock_main, mock_api_factory):
        from fixcity.bmabr.management.commands.tweeter import Command
        c = Command()
        c.handle()
        self.assertEqual(mock_main.call_count, 1)