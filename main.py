from tornado import httpserver, ioloop, web
from spider.scraper import boot
import json, os, sys

class LandingHandler(web.RequestHandler):

	def get(self):
		self.render('index.html')

class SearchHandler(web.RequestHandler):
	@web.asynchronous # Async connection
	def get(self):
		query = str(self.get_query_argument('q'))
		boot(query, callback=self.send_response)

	def send_response(self, *args):
		self.result = args[0]
		self.write(json.dumps(self.result, indent=4))
		self.finish()

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
