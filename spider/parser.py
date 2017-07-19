import re
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import parse_qs, unquote


class TextParser(object):
	''' Parses the text in various html tags on a page '''

	# Strainer speeds up parsing because of selectivity
#	text_strainer = SoupStrainer(strain_through)
	tags_regex = re.compile(r'^p|h[1-6]')#|li|table$')# re.compile(r'^p|a|h\d|b|i|u|em|li|span$')
	
	def __init__(self, text_blob, *args, **kwargs):
		TextParser.text_strainer = SoupStrainer(TextParser.strain_through)
		self.soup = BeautifulSoup(text_blob, 'html.parser', parse_only=TextParser.text_strainer)
		self.text = self._extract_text()

	def _extract_text(self):
		texts = []
		for each in self.soup.find_all(True):
			text = each.get_text(separator=' ')
			if text:
				texts.append(text.strip())
		self.text = " ".join(texts)
		return self.text

	def get_text(self, encoding=None):
		text = self.text if self.text is not None else self._extract_text
		if encoding:
			try:
				return text.encode(encoding)
			except:
				pass
		return text

	@staticmethod
	def strain_through(tag, attrs):
		if TextParser.tags_regex.match(tag):
			if not TextParser.potential_advert(attrs):
				return True
		return False

	@staticmethod
	def potential_advert(attrs):
		# Returns whether the tag is a potential advertisement.
		if attrs:
			ad_class_regex = re.compile(r'adsbygoogle|ads?.*')
			if ad_class_regex.search(attrs.get('class', '')):
				return True
		return False


class SearchResultParser(object):
	''' Parser that parses for search result links '''
	
	def __init__(self, *args, **kwargs):
		self.links = list()

	def cook_soup(self, text_blob, strainer):
		''' Initializes BeautifulSoup object with a strainer '''

		# Using strainer makes parsing fast because of selective parse tree creation
		self.soup = BeautifulSoup(text_blob, 'html.parser', parse_only=strainer)

	def extract_links(self):
		''' Extracts links from the response page. Each subclass defines its own implementation '''
		raise NotImplementedError('Subclasses of SearchResultParser must implement extract_links() method')

	def get_links(self):
		return self.links

	@staticmethod
	def clean_link_from_query_string(link, key):
		''' Returns actual source link from qs of search result link '''
		link = link.split('?')[-1]
		link = parse_qs(link) # Parsing also unquotes the url
		link = link.get(key)
		return (link[0] if isinstance(link, list) and link[0].startswith('http') else None)

	@staticmethod
	def clean_link(link):
		return link.rstrip('/') # To maintain unique constraints in set


class GoogleParser(SearchResultParser):
	''' Google search result page parser '''
	
	strainer = SoupStrainer('h3', attrs={'class': 'r'})
	
	def __init__(self, text, *args, **kwargs):
		super(GoogleParser, self).__init__(*args, **kwargs)
		self.cook_soup(text, GoogleParser.strainer)
		self.extract_links()

	def extract_links(self):
		links = []
		for h3 in self.soup.find_all('h3'):
			href = self.clean_link_from_query_string(h3.a['href'], 'q')
			if href:
				links.append(href.rstrip('/'))
		self.links = links


class BingParser(SearchResultParser):
	''' Bing search result page parser '''
	
	strainer = SoupStrainer('h2')

	def __init__(self, text, *args, **kwargs):
		super(BingParser, self).__init__(*args, **kwargs)
		self.cook_soup(text, BingParser.strainer)
		self.extract_links()

	def extract_links(self):
		links = []
		for h2 in self.soup.find_all('h2'):
			# Every relevant h2 contains an anchor tag
			anchor = h2.a
			if anchor:
				href = anchor['href']
				if href.startswith('http'):
					links.append(href.rstrip('/'))
		self.links = links


class YahooParser(SearchResultParser):
	''' Yahoo search result page parser '''
	
	strainer = SoupStrainer('h3', attrs={'class': 'title'}) # div id=web
#	strainer = SoupStrainer('a', attrs={'class': 'td-u'})

	def __init__(self, text, *args, **kwargs):
		super(YahooParser, self).__init__(*args, **kwargs)
		self.cook_soup(text, YahooParser.strainer)
		self.extract_links()

	def extract_links(self):
		links = []
		for h3 in self.soup.find_all('h3'):
			anchor = h3.a
			if anchor and anchor.attrs.get('href'):
				links.append(anchor['href'].rstrip('/'))
		self.links = links


class DuckDuckGoParser(SearchResultParser):
	''' DuckDuckGo search result page parser '''

#	strainer = SoupStrainer('h2', attrs={'class': 'result__title'})
	strainer = SoupStrainer('a', attrs={'class': 'result__a'})

	def __init__(self, text, *args, **kwargs):
		super(DuckDuckGoParser, self).__init__(*args, **kwargs)
		self.cook_soup(text, DuckDuckGoParser.strainer)
		self.extract_links()

	def extract_links(self):
		links = []
		for anchor in self.soup.find_all('a'):
			href = self.clean_link_from_query_string(anchor['href'], 'uddg')
			if href:
				links.append(href.rstrip('/'))
		self.links = links


# A lookup dictionary
PARSER_LOOKUP = {
	'bing':       BingParser,
	'duckduckgo': DuckDuckGoParser,
	'google':     GoogleParser,
	'text':       TextParser,
	'yahoo':      YahooParser,
}
