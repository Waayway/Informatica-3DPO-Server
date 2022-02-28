from datetime import datetime, timedelta
from tornado import httputil
from loguru import logger
from typing import Any
from dataObjects.LobbyToGameData import LobbyReadyToGameData
from dataObjects.velocityData import VelocityData
from dataObjects.LobbyReady import LobbyReady
from functions import without_keys
import tornado.websocket
import json
import uuid


class GlobalData:
    # GlobalData for this file. just simple things that are handier to store here
    data = {}
    lobby_to_game_data = LobbyReadyToGameData()
    ws_connections = []
    lobbyReadyList: list = []
    isLobbyStarted: bool = False
    isLobbyReady: bool = False
    wasLobbyReady: bool = False
    numConnected: int = 0
    startedTimerMoment: datetime = datetime.now()
    LobbyLoadedList: list = []


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

        self.done_loading = False
        
    
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
        data = {"players": {}}
        timeDelta = datetime.now() - GlobalData.startedTimerMoment
        if timeDelta < timedelta(seconds=5):
            data["timer"] = timeDelta.total_seconds()
        for i in GlobalData.ws_connections:
            logger.debug(f"Name of {i.id} is: {i.name}")
            data["players"][i.id] = {"lobbydata": i.LobbyReady.getData(), "name": i.name}
        logger.debug("Data To send to the clients: 0" + str(data))
        for i in GlobalData.ws_connections:
            i.write_message("0"+json.dumps(data))

    def send_player_data(self, data):
        newData = without_keys(data, [self.id])
        self.write_message("1"+json.dumps(newData))
    
    def send_lobbyloaded_data(self):
        data = {}
        data["playersdoneloading"] = len(GlobalData.LobbyLoadedList)
        logger.debug("Data to send to the clients: 3"+str(data))
        for i in GlobalData.ws_connections:
            i.write_message("3"+json.dumps(data))

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
            check_if_lobby_all_ready()
            self.send_lobby_message()

        elif str(message).startswith("1"):
            # Decifer data and import the data
            message = str(message).removeprefix("1")
            if message == "timer":
                check_if_lobby_all_ready()
        elif str(message).startswith("2"):
            message = str(message).removeprefix("2")
            if message == "true":
                self.done_loading = True
                GlobalData.LobbyLoadedList.append(self.id)
            else:
                self.done_loading = False
                GlobalData.LobbyLoadedList.remove(self.id)
            self.send_lobbyloaded_data()
        elif str(message).startswith("4"):
            self.velData.importData(message.removeprefix("4"))
            dataToSend = {}
            for i in GlobalData.ws_connections:
                if i.id == self.id: continue
                dataToSend[i.id] = i.velData.exportData()
            self.write_message("4"+json.dumps(dataToSend))
            


    def on_close(self):
        logger.info("WebSocket closed, id: " + self.id)
        GlobalData.ws_connections.remove(self)
        if self.id in GlobalData.LobbyLoadedList:
            GlobalData.LobbyLoadedList.remove(self.id)
    
    def send_lobby_to_game_data():
        data = LobbyReadyToGameData()
        for i in GlobalData.ws_connections:
            data.players.append(i.id)
            data.playersDoneLoading += int(i.done_loading)
        logger.debug(f"Data to send to the clients: 2{data}")
        for i in GlobalData.ws_connections:
            i.write_message("2"+json.dumps(data.exportData()))


def check_if_lobby_all_ready():
    isLobbyReady = True
    for i in GlobalData.lobbyReadyList:
        print(i)
        if not i: 
            isLobbyReady = False
            break
    print(isLobbyReady)
    if isLobbyReady == True and not GlobalData.wasLobbyReady:
        GlobalData.startedTimerMoment = datetime.now()
        GlobalData.wasLobbyReady = isLobbyReady
    elif isLobbyReady and GlobalData.wasLobbyReady:
        if datetime.now() - GlobalData.startedTimerMoment > timedelta(seconds=5) and GlobalData.wasLobbyReady:
            GlobalData.isLobbyStarted = True
            GlobalData.startedTimerMoment = datetime.now() - timedelta(hours=5)
            WebSocket.send_lobby_to_game_data()
    elif not isLobbyReady:
        GlobalData.wasLobbyReady = False

    GlobalData.isLobbyReady = isLobbyReady

# 