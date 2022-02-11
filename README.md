# Informatica-3DPO-Server

- Max Players in config
- Map size in config 
- Players when connected get into the lobby.


## Protocol
Client connects and get send `id` this id then gets stored at both the server and client level
```json
"id"
```
After this the client will send the username
```json
{"name": "username"}
```

Every message has a int at the front to say what kind of message it is,

0. LobbyReady
1. VelocityData
2. TimerData
3. MapData

Most of the data will thus be like
```json
1{data}
```
### Lobby
Client gets a list of players on connecting, on disconnect of a client the client will get a update of the current players waiting in the lobby, on ready the server will receive a message which will say
```json 
{"id": "ready"}
```
Or when not ready
```json
{"id": "not ready"}
```
both have their id's in place of the "id"
the ready data will then get sent to all the clients.

### Ingame
Client sends every 30 seconds their Velocity instead of their position.
The server processes the velocity to then get the position. then sends both to the client to make a smoother motion for the player