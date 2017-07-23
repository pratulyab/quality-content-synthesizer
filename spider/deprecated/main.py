''' DEPRECATED. This script boots the blocking spider and returns results.
	However, this is no longer user.
	Please refer to spider/scraper.py where all this logic has been adapted to work in an asynchronous fashion using Tornado Web Framework
'''

# # #
# Haven't added multi-threading to this because the architecture has been shifted to asynchronous.
# concurrency has been achieved there. Please refer spider/scraper.py
# # #

from urllib.parse import quote_plus
try:
	from spider.deprecated.scraper import LinkScraper, TextScraper # Deprecated Scraper (BLOCKING + SYNCHRONOUS)
except ImportError:
	import os, sys
	sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
	from deprecated.scraper import LinkScraper, TextScraper

SE = {
	'bing'       : {'url': 'https://www.bing.com/search?q=%s&count=100'},
	'duckduckgo' : {'url': 'https://duckduckgo.com/html?q=%s'},
	'google'     : {'url': 'https://google.com/search?q=%s&num=100'},
	'yahoo'      : {'url': 'https://search.yahoo.com/search?p=%s&n=100'},
}

scraped_links = list()
result = []

def get_results(key):
	global scraped_links, result

	url = SE[key]['url']
	l = LinkScraper(url)
	links = l.get_links()
	required = SE[key]['n']
	for link in links:
		if link in scraped_links:
			continue
		text = TextScraper(link).get_corpus()
		if text and len(text.split()) > 1000:
			result.append({'url':link, 'text': text})
			required -= 1
			if not required:
				break
	return required

def get_corpora(query, n=50): # G: 40% B: 20% D: 20% Y: 20%
	query = quote_plus(query)
	remaining = 0
	
	for key in SE:
		SE[key]['url'] = SE[key]['url'] % query
		if key == 'google':
			num = round(n * 0.4)
		else:
			num = round(n * 0.2)
		SE[key]['n'] = num
	
	
	for key in ['bing', 'duckduckgo', 'yahoo', 'google']:
		print('scraping %d %s result links' % (SE[key]['n'],key))
		if key != 'google':
			rem = get_results(key)
			remaining += rem
		else:
			SE[key]['n'] += remaining
			print('Result short of', get_results(key), 'corpora')

	return result # {'url': <URL>, 'text': <TextBlob>}

if __name__ == '__main__':
	print(len(get_corpora(input("Enter search query: "))), 'links with text over 1000 words')
