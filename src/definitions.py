from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from uuid import UUID


class Coordinate:
    dimension: str
    x: int
    y: int
    z: int

    def __init__(self, dimension: str, x: int, y: int, z: int) -> None:
        self.dimension = dimension
        self.x = x
        self.y = y
        self.z = z

    def dump(self) -> str:
        return f"{self.dimension}@{self.x},{self.y},{self.z}"

    def load(self, data: str) -> Coordinate:
        data = data.split("@")
        dimension = data[0]
        data = data[1].strip().split(",")
        if len(data) != 3:
            raise ValueError("Coordinate does not have 3 items.")

        return Coordinate(dimension.strip(), int(data[0].strip()), int(data[1].strip()), int(data[2].strip()))


class DummyWebSocket:
    remote_address: tuple

    def __init__(self, remote_address: tuple):
        self.remote_address = remote_address


class Player:
    uuid: UUID
    name: str
    ip: str
    network_data: dict

    def __init__(self, websocket=DummyWebSocket(("", 0)), uuid: str = "00000000-0000-0000-0000-000000000000", name: str = "") -> None:
        self.name = str(name)
        self.uuid = UUID(hex=uuid.replace("-", ""))
        self.ip = websocket.remote_address[0]
        self.network_data = {
            "ip": [],
            "user_agent": [],
            "encoding": [],
            "mime": [],
            "via": [],
            "forwarded": [],
            "language": [],
        }

    def add_network_data(self, data: dict) -> None:
        for k in self.network_data.keys():
            if k in data.keys():
                if type(data[k]) is list:
                    for item in data[k]:
                        if item not in self.network_data[k] and item is not None:
                            self.network_data[k].append(item)
                else:
                    item = data[k]
                    if item not in self.network_data[k] and item is not None:
                        self.network_data[k].append(item)

    def dump(self) -> dict:
        return {
            "uuid": self.uuid.hex,
            "name": self.name,
            "ip": self.ip,
            "network_data": self.network_data,
        }

    def load(self, data: dict) -> Player:
        player = Player(
            DummyWebSocket((data["ip"], 0)),
            data["uuid"],
            data["name"],
        )

        player.add_network_data(data["network_data"])
        return player


class ServerPlayer:
    player: Player
    last_location: Coordinate
    prev_locations: list[Coordinate]
    last_seen: datetime
    chat_history: list[str]
    pm_history: list[str]
    advancements: list[str]

    def __init__(self, websocket=None, player: Player = None, location: Coordinate = None, prev_locations: list[Coordinate] = [], chat_history=[], pm_history=[], advancements=[]):
        self.player = player
        self.last_location = location
        self.prev_locations = prev_locations
        self.last_seen = datetime.now(timezone.utc)
        self.chat_history = chat_history
        self.pm_history = pm_history
        self.advancements = advancements

    def set_location(self, websocket, location: Coordinate):
        if self.last_location is not None:
            self.prev_locations.append(self.last_location)

        self.last_location = location

    def set_seen(self, websocket, seen=None):
        if seen is None:
            self.last_seen = datetime.now(timezone.utc)
        else:
            self.last_seen = seen

    def add_chat(self, message: str):
        self.chat_history.append(message)

    def add_pm(self, message: str):
        self.pm_history.append(message)

    def add_advancement(self, advancement: str):
        if advancement not in self.advancements:
            self.advancements.append(advancement)

    def dump(self) -> dict:
        prev_locations = []
        for pl in self.prev_locations:
            prev_locations.append(pl.dump())

        return {
            "uuid": self.player.uuid.hex,
            "last_location": self.last_location.dump(),
            "prev_locations": prev_locations,
            "last_seen": self.last_seen.timestamp(),
            "chat_history": self.chat_history,
            "pm_history": self.pm_history,
            "advancements": self.advancements,
        }

    def load(self, data: dict, players: list[Player]) -> ServerPlayer:
        player = None
        for p in players:
            if p.uuid.hex == data["uuid"].replace("-", ""):
                player = p
                break

        if player is None:
            raise ValueError("Could not find player in players.")

        prev_locations = []
        for pl in data["prev_locations"]:
            prev_locations.append(Coordinate("", 0, 0, 0).load(pl))

        serverPlayer = ServerPlayer(
            None,
            player,
            Coordinate("", 0, 0, 0).load(data["last_location"]),
            prev_locations,
            data["chat_history"],
            data["pm_history"],
            data["advancements"],
        )

        serverPlayer.set_seen(None, datetime.fromtimestamp(data["last_seen"]))
        return serverPlayer


class Chunk:
    blocks: list[str]
    biome: str

    def __init__(self, blocks: list[str], biome: str):
        self.blocks = blocks
        self.biome = biome

    def dump(self) -> dict:
        return {
            "blocks": self.blocks,
            "biome": self.biome,
        }

    def load(self, data: dict) -> Chunk:
        return Chunk(
            data["blocks"],
            data["biome"],
        )


class Server:
    ip: str
    players: list[ServerPlayer]
    chunks: dict[Coordinate, Chunk]

    def __init__(self, websocket=None, ip: str = "", chunks={}):
        self.ip = ip
        self.players = []
        self.chunks = chunks

    def add_player(self, player: ServerPlayer):
        for p in self.players:
            if player.player.uuid.hex == p.player.uuid.hex:
                return

        self.players.append(player)

    def set_chunk(self, c: Coordinate, chunk: Chunk):
        self.chunks[c] = chunk

    def dump(self) -> dict:
        players = []
        for p in self.players:
            players.append(p.dump())

        chunks = {}
        for k in self.chunks.keys():
            chunks[k.dump()] = self.chunks[k].dump()

        return {
            "ip": self.ip,
            "players": players,
            "chunks": chunks,
        }

    def load(self, data: dict, players: list[Player]) -> Server:
        server = Server(
            None,
            data["ip"],
        )

        for p in data["players"]:
            player = ServerPlayer().load(p, players)
            server.add_player(player)

        for c in data["chunks"].keys():
            coord = Coordinate("", 0, 0, 0).load(c)
            chunk = Chunk([], []).load(data["chunks"].get(c, {}))
            server.set_chunk(coord, chunk)

        return server


class DataStore:
    players: list[Player]
    servers: list[Server]
    sessions: list[str] = []

    def __init__(self, players: list[Player] = [], servers: list[Server] = []):
        self.players = players
        self.servers = servers

    def add_player(self, player: Player):
        for p in self.players:
            if player.uuid.hex == p.uuid.hex:
                return

        self.players.append(player)

    def add_server(self, server: Server):
        for s in self.servers:
            if server.ip == s.ip:
                return

        self.servers.append(server)

    def dump(self) -> dict:
        players = []
        for p in self.players:
            players.append(p.dump())

        servers = []
        for s in self.servers:
            # if s.ip is not None and s.ip != "unknown":
            servers.append(s.dump())

        return {
            "players": players,
            "servers": servers,
            "sessions": self.sessions,
        }

    def load(self, data: dict) -> DataStore:
        datastore = DataStore()

        for p in data["players"]:
            player = Player().load(p)
            datastore.add_player(player)

        for s in data["servers"]:
            server = Server().load(s, datastore.players)
            datastore.add_server(server)

        self.sessions = data["sessions"]

        return datastore

    def dumpfile(self, path: os.PathLike) -> None:
        with open(path, "w") as f:
            f.write(json.dumps(self.dump()))

    def loadfile(self, path: os.PathLike) -> DataStore:
        with open(path, "r") as f:
            return self.load(json.loads(f.read().strip()))
