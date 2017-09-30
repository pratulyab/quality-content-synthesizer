import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from datetime import timedelta
from rater.rating import rate
from spider.parser import PARSER_LOOKUP
from tornado import gen, httpclient, ioloop, queues, web
from urllib.parse import quote_plus, urlparse

# Search Engine's specific urls. Asking them to serve max #results per page. (query params)
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
		response = yield httpclient.AsyncHTTPClient().fetch(url, request_timeout=3) # Asynch network fetch call
		html = response.body #if isinstance(response.body, str) else response.body.decode()
		parser = PARSER_LOOKUP['text'](html) # Create specific parser object
		text = parser.get_text(encoding='utf-8') # Parse text
	except Exception as e:
#		print('Exception: %s %s' % (e, url))
		raise gen.Return('')
	# Tornado way of returning data from coroutines.
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
		response = yield httpclient.AsyncHTTPClient().fetch(url, request_timeout=4)
		try:
			html = response.body if isinstance(response.body, str) else response.body.decode()
		except:
			html = response.body
		parser = get_se_parser(url)(html)
		links = parser.get_links()
	except Exception as e:
#		print('Exception: %s %s' % (e, url))
		raise gen.Return([])
	
	raise gen.Return(links)


@gen.coroutine
def boot(query, n):
	''' Boot spider '''
#	if not query or not n:
#		raise gen.Return([])
	query = quote_plus(query) # Quote Query
	start = time.time()
	se_queue = queues.Queue() # Queue to store search engine urls with quoted query
	links_queue = queues.Queue() # Queue to store search result links
	fetching, fetched, processed = set(), set(), set() 
	result = list()
	TOTAL_PROCESSED = list() # Hack to limit slider range, because global int variable doesn't work with coroutine	
	n = n + int(n * 0.2) # extra 20% accounts for urls with no text or request exceptions. Tries best to provide a total of n with text
	# Limiting this because of Heroku drawbacks as mentioned in the documentation(under DISCLAIMER) and the demo url.
	# Link to heroku issue: https://devcenter.heroku.com/articles/request-timeout

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
			se_queue.task_done() # Decrement task counter

	@gen.coroutine
	def scrape_text(n):
		url = yield links_queue.get()
		try:
			if url in processed or len(TOTAL_PROCESSED) >= n:
				raise gen.Return('')
#			print('processing url', url)
			TOTAL_PROCESSED.append(url)
			processed.add(url)
			text = yield get_text_from_url(url)
			fetched.add(url)
			if text:
				result.append({'url': url, 'text': str(text)})
#			else:
#				print('no text for', url)
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
				yield scrape_text(n)

	# Enqueue search engine urls into se_queue
	for key,se in SEARCH_ENGINES.items():
		se_queue.put(str(se['url'] % query))

	for _ in range(2):
		# Create worker to send request to search engines and crawl links
		create_worker(who='link_scraper')
	
	yield se_queue.join(timeout=timedelta(seconds=120)) # Block until queue is empty or timeout is reached
	
	for _ in range(CONCURRENCY):
		# Create worker to send request to link and parse text
		create_worker(who='text_scraper')
	
	yield links_queue.join(timeout=timedelta(seconds=300))
	print('Scraped %d URLs in %d seconds.' % (len(fetched), time.time() - start))

	start = time.time()
	
	# Pass the result with urls and corpora to the rater
	result = rate(result)
	
	print('Rated in %f seconds' % (time.time() - start))
	raise gen.Return(result)
