import tornado.websocket
from loguru import logger
import json
import uuid

class GlobalData:
    data = {}
    ws_connections = []

class WebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        self.id = str(uuid.uuid4())
        logger.info("WebSocket opened, id: " + self.id)
        self.write_message(self.id)

    def on_message(self, message):
        logger.debug("Got Data from client: "+self.id+", "+str(message))

    def on_close(self):
        logger.info("WebSocket closed, id: " + self.id)
        