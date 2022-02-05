import json
import tornado.ioloop
import tornado.web
import tornado.websocket
import uuid

data = {}
clients = []

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Game server that is using Websockets Please ignore")

class WebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        self.id = str(uuid.uuid4())
        clients.append(self.id)
        data[self.id] = {"pos": {"x":0,"y":0,"z":0}}
        print("WebSocket opened, id: "+ self.id)
        
    def on_message(self, message):
        data[self.id] = json.loads(message)
        dataToSend = without_keys(data, [self.id])
        self.write_message(json.dumps(dataToSend))
        

    def on_close(self):
        print("WebSocket closed")
        del data[self.id]
        clients.remove(self.id)

def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/ws', WebSocket)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

