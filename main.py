from tornado import httpserver, ioloop, web
from spider.scraper import boot
import json, os, sys

class LandingHandler(web.RequestHandler):

	def get(self):
		self.render('index.html')

class SearchHandler(web.RequestHandler):
	@web.asynchronous # Async connection
	def get(self):
		try:
			query = str(self.get_query_argument('q'))
			if not query:
				self.send_response([]) # writing back none
				return
			n = int(self.get_query_argument('n'))
			if n == 0:
				self.send_response([])
				return
		except ValueError:
			# Error converting to int
			n = 30 # Default in HTML
		except Exception as e:
			self.send_response([])
			return
		boot(query, n, callback=self.send_response) # Boot spider

	def send_response(self, *args):
		self.result = args[0]
		self.write(json.dumps(self.result))
		self.finish()

# Url - Controller mapping
urls = [
	(r'/', LandingHandler),
	(r'/search/?$', SearchHandler),
]


if __name__ == '__main__':
	app = web.Application(urls) # Create Tornado web application instance
#	port = sys.argv[1] if len(sys.argv) > 1 else 8888
#	app.listen(port) # Define port 8888 to listen at
	http_server = httpserver.HTTPServer(app)
	port = int(os.environ.get("PORT", 5000))
	http_server.listen(port)
	ioloop.IOLoop.current().start()  # Create IOLoop instance and start it
