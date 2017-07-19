import requests
from urllib.parse import urlparse
from .parser import *

class Crawler(object):
	''' Crawler crawls the url '''

	REQUEST_TIMEOUT = 5 # seconds

	def __init__(self, url, *args, **kwargs):
		self.url = url
		self.response = self._send_request()

	def _send_request(self):
		try:
			r = requests.get(self.url, timeout=Crawler.REQUEST_TIMEOUT)
			r.raise_for_status()
			return r
		except Exception as e:
			print(e)
			return None


class TextScraper(Crawler):
	''' TextScraper scrapes the crawled page for text '''

	def __init__(self, url, *args, **kwargs):
		super(TextScraper, self).__init__(url, *args, **kwargs)
		self.scraped_result = ''
		if self.response:
			parser = TextParser(self.response.text)
			self.scraped_result = parser.get_text()
	
	def get_corpus(self):
		return self.scraped_result


class LinkScraper(Crawler):
	''' LinkScraper scrapes the crawled page for links (Used for search results) '''

	def __init__(self, url, *args, **kwargs):
		super(LinkScraper, self).__init__(url, *args, **kwargs)
		self.scraped_links = None
		if self.response:
			parser = self.get_parser(url)(self.response.text)
			self.scraped_links = parser.get_links()

	def get_links(self):
		return self.scraped_links

#	def get_links(self, n):
#		return self.scraped_links[:n]

	@staticmethod
	def get_parser(url):
		''' Returns parser class based on domain of url if found in PARSER_LOOKUP; otherwise None '''
		subdomain = urlparse(url).netloc
		domain = subdomain.split('.')[-2].lower()
		return PARSER_LOOKUP.get(domain)
