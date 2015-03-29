import urllib2
import urllib
import verbix_parser

class VerbixScrapper:

	__languages = {
		'ro': 5,
		'es': 1,
		'pt': 2,
		'fr': 3,
		'ca': 4
	}

	def get_verb(self, language, verb):
		base_url = 'http://www.verbix.com/find-verb/'
		params = urllib.urlencode({
			'verb': verb,
			'Submit': 'Find'
		})

		request = urllib2.Request(base_url, params)
		response = urllib2.urlopen(request)

		parser = verbix_parser.VerbixParser()
		return parser.get_verb(VerbixScrapper.__languages[language], response.read())

	def get_conjugations(self, language, verb):
		base_url = 'http://www.verbix.com/webverbix/go.php'

		try:
			params = urllib.urlencode({
				'T1': verb,
				'D1': VerbixScrapper.__languages[language]
			})

			response = urllib2.urlopen('%s?%s' % (base_url, params))

			parser = verbix_parser.VerbixParser()
			return parser.parse(response.read())
		except UnicodeEncodeError:
			print 'Could not encode parameters'