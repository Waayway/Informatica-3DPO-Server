from typing import Any
import tornado.websocket
from loguru import logger
import json
import uuid
from dataObjects.velocityData import VelocityData
from dataObjects.LobbyReady import LobbyReady
from functions import without_keys
from tornado import httputil


class GlobalData:
    # GlobalData for this file. just simple things that are handier to store here
    data = {}
    ws_connections = []
    lobbyReadyList: list = []
    isLobbyStarted: bool = False
    numConnected: int = 0


def send_message_to_clients():
    # send the player data every x seconds.
    if GlobalData.isLobbyStarted:
        data = {}
        for i in GlobalData.ws_connections:
            data[i.id] = i.velData.exportData()

        logger.debug("Sending Player Data: "+data)

        for i in GlobalData.ws_connections:
            i.send_player_data(data)


class WebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application: tornado.web.Application, request: httputil.HTTPServerRequest, **kwargs: Any) -> None:
        super().__init__(application, request, **kwargs)
        # Data used in this Class
        self.velData = VelocityData()
        self.numid = 0
        self.first_message = True
        self.name = ""
        
    
    def open(self):
        # Generate an Id and log it to console
        self.id = str(uuid.uuid4())
        GlobalData.ws_connections.append(self)
        logger.info("WebSocket opened, id: " + self.id)
        # Write the id back to the client for saving on the client
        self.write_message(self.id)
        # setNumid
        self.numid = len(GlobalData.lobbyReadyList)
        self.LobbyReady = LobbyReady(self.id)
        GlobalData.lobbyReadyList.append(self.LobbyReady)
        #send Lobby Data so the client can place current players in the lobby
        self.send_lobby_message()

    def send_lobby_message(self):
        data = {}
        for i in GlobalData.ws_connections:
            logger.debug(f"Name of {i.id} is: {i.name}")
            data[i.id] = {"lobbydata": i.LobbyReady.getData(), "name": i.name}
        logger.debug("Data To send to the clients: 0" + str(data))
        for i in GlobalData.ws_connections:
            i.write_message("0"+json.dumps(data))

    def send_player_data(self, data):
        newData = without_keys(data, [self.id])
        self.write_message("1"+json.dumps(newData))

    def on_message(self, message):
        message = message.decode('UTF-8')
        logger.debug("Got Data from client: "+self.id+", "+str(message))
        if self.first_message:
            data = json.loads(message)
            self.name = data["name"]
            self.first_message = not self.first_message
        # checks the data the server got from client for data type, types are descriped in README.md
        if str(message).startswith("0"):
            # Get message and load into the LobbyReady Object
            message = str(message).removeprefix("0")
            data = json.loads(message)
            self.LobbyReady.setData(data[self.id])
            GlobalData.lobbyReadyList[self.numid] = data[self.id]
            self.send_lobby_message()

        elif str(message).startswith("1"):
            # Decifer data and import the data
            message = str(message).removeprefix("1")
            data = json.loads(message)
            self.velData.importData(data)

    def on_close(self):
        logger.info("WebSocket closed, id: " + self.id)
        GlobalData.ws_connections.remove(self)
