from datetime import timedelta
from rater.rating import rate
from spider.parser import PARSER_LOOKUP
from tornado import gen, httpclient, ioloop, queues, web
from urllib.parse import quote_plus, urlparse
import sys, time

SEARCH_ENGINES = {
	'bing'       : {'url': 'https://www.bing.com/search?q=%s&count=100'},
	'duckduckgo' : {'url': 'https://duckduckgo.com/html?q=%s'},
	'google'     : {'url': 'https://google.com/search?q=%s&num=100'},
	'yahoo'      : {'url': 'https://search.yahoo.com/search?p=%s&n=100'},
}

CONCURRENCY = 10 # Num. Of Concurrent Workers

@gen.coroutine
def get_text_from_url(url):
	''' Crawls url, scrapes the page and parses the text '''
	
	try:
		response = yield httpclient.AsyncHTTPClient().fetch(url, request_timeout=5)
		html = response.body #if isinstance(response.body, str) else response.body.decode()
		parser = PARSER_LOOKUP['text'](html)
		text = parser.get_text(encoding='utf-8')
	except Exception as e:
		print('Exception: %s %s' % (e, url))
		raise gen.Return('')
	
	raise gen.Return(text)

def get_se_parser(url):
	''' Returns particular Search Engine parser class based on domain of url if found in PARSER_LOOKUP; otherwise None '''
	subdomain = urlparse(url).netloc
	domain = subdomain.split('.')[-2].lower()
	return PARSER_LOOKUP.get(domain)

@gen.coroutine
def get_links_from_url(url):
	''' Crawls url, scrapes search result page and parses for results' links '''
	
	try:
		response = yield httpclient.AsyncHTTPClient().fetch(url, request_timeout=10)
		try:
			html = response.body if isinstance(response.body, str) else response.body.decode()
		except:
			html = response.body
		parser = get_se_parser(url)(html)
		links = parser.get_links()
	except Exception as e:
		print('Exception: %s %s' % (e, url))
		raise gen.Return([])
	
	raise gen.Return(links)


@gen.coroutine
def boot(query):
	query = quote_plus(query)
	start = time.time()
	se_queue = queues.Queue() # Search Engine Links Queue
	links_queue = queues.Queue()
	processed = set()
	fetching, fetched = set(), set()
	result = list()

	@gen.coroutine
	def scrape_link():
		url = yield se_queue.get()
		try:
			if url in fetching:
				return
#			print('fetching url', url)
			fetching.add(url)
			links = yield get_links_from_url(url)
			fetched.add(url)
#			print(len(links), 'links fetched from', url)
			for each in links:
				if each.startswith('http'):
					yield links_queue.put(each) # Adding to links_queue
		finally:
			se_queue.task_done()

	@gen.coroutine
	def scrape_text():
		url = yield links_queue.get()
		try:
			if url in processed:
				return
#			print('processing url', url)
			processed.add(url)
			text = yield get_text_from_url(url)
			fetched.add(url)
			if text:
				result.append({'url': url, 'text': str(text)})
			else:
				print('no text for', url)
		finally:
			links_queue.task_done()

	@gen.coroutine
	def create_worker(who):
		if who == 'link_scraper':
			while True:
				yield scrape_link()
		else:
			# text_scraper
			while True:
				yield scrape_text()

	for key,se in SEARCH_ENGINES.items():
		se_queue.put(str(se['url'] % query))

	for _ in range(2):
		create_worker(who='link_scraper')
	
	yield se_queue.join(timeout=timedelta(seconds=120)) # Block until queue is empty or timeout is achieved
	
	for _ in range(CONCURRENCY):
		create_worker(who='text_scraper')
	
	yield links_queue.join(timeout=timedelta(seconds=300))
	print('Scraped %d URLs in %d seconds.' % (len(fetched), time.time() - start))
	start = time.time()
	result = rate(result)
	print('Rated in %f seconds' % (time.time() - start))
	raise gen.Return(result)
