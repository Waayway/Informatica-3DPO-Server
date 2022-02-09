import tornado.ioloop
import tornado.web
from lobby import WebSocket

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Game server that is using Websockets Please ignore")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/ws', WebSocket)
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
