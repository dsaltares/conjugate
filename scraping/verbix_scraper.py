# -*- coding: utf-8 -*-

import urllib2
import urllib
import httplib
import socket
import time
import logging
import verbix_parser

class VerbixScraper:

    __languages = {
        'ro': 5,
        'es': 1,
        'pt': 2,
        'fr': 3,
        'ca': 4
    }

    __retries = 5

    def get_infinitive(self, language, verb):
        base_url = 'http://www.verbix.com/find-verb/'
        params = {
            'verb': verb,
            'Submit': 'Find'
        }

        response = self.__request(self.__post, base_url, params)

        if response is None:
            return

        content = self.__get_response_content(response)

        parser = verbix_parser.VerbixParser()
        return parser.get_infinitive(VerbixScraper.__languages[language], content)

    def get_verb_info(self, language, verb):
        base_url = 'http://www.verbix.com/webverbix/go.php'
        params = {
            'T1': verb,
            'D1': VerbixScraper.__languages[language]
        }

        response = self.__request(self.__get, base_url, params)

        if response is None:
            return

        content = self.__get_response_content(response)

        parser = verbix_parser.VerbixParser()
        return parser.parse(content)

    def __get_response_content(self, response):
        try:
            return response.read()
        except httplib.IncompleteRead as e:
            return e.partial

    def __request(self, make_request, url, params):
        num_attempts = 0

        while num_attempts < VerbixScraper.__retries:
            try:
                (success, response) = self.__try_request(make_request, url, params)

                if success:
                    return response
                else:
                    logging.warning('Request %d/%d failed' % (num_attempts + 1, VerbixScraper.__retries))
                    num_attempts += 1
                    time.sleep(2)

            except UnicodeEncodeError:
                logging.error('Could not encode parameters')
                return None

        logging.error('Too many attempts, giving up')

    def __try_request(self, make_request, url, params):
        try:
            return make_request(url, params)
        except (socket.error,httplib.BadStatusLine, urllib2.HTTPError, urllib2.URLError):
            return (False, None)

    def __get(self, url, params):
        final_url = '%s?%s' % (url, urllib.urlencode(params))
        logging.info('get: %s' % final_url)
        response = urllib2.urlopen(final_url)
        return (True, response)

    def __post(self, url, params):
        logging.info('post: %s' % url)
        request = urllib2.Request(url, urllib.urlencode(params))
        response = urllib2.urlopen(request)
        return (True, response)