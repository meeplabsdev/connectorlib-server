from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID

import psycopg2
from multipledispatch import dispatch as overload  # type: ignore
from psycopg2 import sql
from psycopg2.extensions import connection, cursor
from datetime import datetime


def is_docker():
    cgroup = Path("/proc/self/cgroup")
    return Path("/.dockerenv").is_file() or (cgroup.is_file() and "docker" in cgroup.read_text())


class DB:
    class Table:
        name: str

        def __init__(self, conn: connection, cur: cursor) -> None:
            self.conn = conn
            self.cur = cur

        def commit(self) -> None:
            try:
                self.conn.commit()
            except psycopg2.Error as e:
                self.conn.rollback()
                raise e

        def delete(self, id: int) -> None:
            self.cur.execute(f"select id from {self.name} where id = '{id}';")
            items = self.cur.fetchone()
            if items is None or len(items) == 0:
                return

            self.cur.execute(f"delete from {self.name} where id = '{id}';")
            self.commit()

        def find(self, **kwargs: Any) -> tuple[Any, ...] | None:
            self.cur.execute(f"select * from {self.name} where {self.where(**kwargs)};")
            items = self.cur.fetchall()
            if len(items) != 0:
                return items[0]

        def where(self, **kwargs: Any) -> str:
            fields = list(kwargs.keys())
            values = [f"'{v}'" if type(v) is str else str(v) for v in kwargs.values()]

            self.cur.execute(f"select column_name from information_schema.columns where table_name = '{self.name}' and data_type like 'timestamp%%';")
            timestamps = [str(i[0]) for i in self.cur.fetchall()]
            _where: list[str] = []
            for f, v in zip(fields, values):
                if f not in timestamps:
                    _where.append(f"{f} = {v}")
            return " and ".join(_where)

    class LookupTable(Table):
        def __init__(self, conn: connection, cur: cursor, name: str) -> None:
            super().__init__(conn, cur)
            self.name = name

        def add(self, value: str) -> tuple[int, str]:
            self.cur.execute(f"insert into {self.name} (value) values ('{value}');")
            self.commit()

            result: tuple[int, str] | None = self.find(value=value)
            if result is None:
                raise Exception("DB error when inserting value.")

            return result

        def remove(self, value: str) -> None:
            self.cur.execute(f"select id from {self.name} where value = '{value}';")
            items = self.cur.fetchone()
            if items is None or len(items) == 0:
                return

            self.cur.execute(f"delete from {self.name} where value = '{value}';")
            self.commit()

        def get(self, value: str) -> tuple[int, str] | None:
            return self.find(value=value)

    class Chunks(Table):
        def __init__(self, conn: connection, cur: cursor) -> None:
            super().__init__(conn, cur)
            self.name = "chunks"

        def add(self, server_id: int, dimension: int, biome: int, surface_y: int, chunk_x: int, chunk_z: int) -> tuple[int, int, int, int, int, int, int]:
            self.cur.execute(f"insert into {self.name} (server_id, dimension, biome, surface_y, chunk_x, chunk_z) values ({server_id}, {dimension}, {biome}, {surface_y}, {chunk_x}, {chunk_z});")
            self.commit()

            result: tuple[int, int, int, int, int, int, int] | None = self.find(server_id=server_id, dimension=dimension, chunk_x=chunk_x, chunk_z=chunk_z)
            if result is None:
                raise Exception("DB error when inserting value.")

            return result

        def get(self, server_id: int, dimension: int, chunk_x: int, chunk_z: int) -> tuple[int, int, int, int, int, int, int] | None:
            return self.find(server_id=server_id, dimension=dimension, chunk_x=chunk_x, chunk_z=chunk_z)

    class Locations(Table):
        def __init__(self, conn: connection, cur: cursor):
            super().__init__(conn, cur)
            self.name = "locations"

        def add(self, server_player_id: int, dimension: int, global_x: int, global_y: int, global_z: int) -> tuple[int, int, int, int, int, datetime]:
            self.cur.execute(f"insert into {self.name} (server_player_id, dimension, global_x, global_y, global_z, visited) values ({server_player_id}, {dimension}, {global_x}, {global_y}, {global_z}, CURRENT_TIMESTAMP);")
            self.commit()

            result: tuple[int, int, int, int, int, datetime] | None = self.find(server_player_id=server_player_id, dimension=dimension, global_x=global_x, global_y=global_y, global_z=global_z)
            if result is None:
                raise Exception("DB error when inserting value.")

            return result

        def get(self, server_player_id: int, dimension: int, global_x: int, global_y: int, global_z: int) -> tuple[int, int, int, int, int, int, datetime] | None:
            return self.find(server_player_id=server_player_id, dimension=dimension, global_x=global_x, global_y=global_y, global_z=global_z)

    class Messages(Table):
        def __init__(self, conn: connection, cur: cursor):
            super().__init__(conn, cur)
            self.name = "messages"

        def add(self, server_player_id: int, message: str, from_uuid: str, to_uuid: str) -> tuple[int, int, str, str, str]:
            self.cur.execute(f"insert into {self.name} (server_player_id, message, from_uuid, to_uuid) values ({server_player_id}, '{message}', '{from_uuid}', '{to_uuid}');")
            self.commit()

            result: tuple[int, int, str, str, str] | None = self.find(server_player_id=server_player_id, message=message, from_uuid=from_uuid, to_uuid=to_uuid)
            if result is None:
                raise Exception("DB error when inserting value.")

            return result

        def get(self, server_player_id: int, message: str, from_uuid: str, to_uuid: str) -> tuple[int, int, str, str, str] | None:
            return self.find(server_player_id=server_player_id, message=message, from_uuid=from_uuid, to_uuid=to_uuid)

    class NetworkData(Table):
        def __init__(self, conn: connection, cur: cursor) -> None:
            super().__init__(conn, cur)
            self.name = "network_data"

        def add(self, player_id: int, ip_address: str, user_agent: str, via: str, forwarded: str) -> tuple[int, int, str, str, str, str]:
            self.cur.execute(f"insert into {self.name} (player_id, ip_address, user_agent, via, forwarded) values ({player_id}, '{ip_address}', '{user_agent}', '{via}', '{forwarded}');")
            self.commit()

            result: tuple[int, int, str, str, str, str] | None = self.find(player_id=player_id, ip_address=ip_address, user_agent=user_agent, via=via, forwarded=forwarded)
            if result is None:
                raise Exception("DB error when inserting value.")

            return result

        def get(self, player_id: int, ip_address: str, user_agent: str) -> tuple[int, int, str, str, str, str] | None:
            return self.find(player_id=player_id, ip_address=ip_address, user_agent=user_agent)

    class Players(Table):
        def __init__(self, conn: connection, cur: cursor) -> None:
            super().__init__(conn, cur)
            self.name = "players"

        def add(self, uuid: str, username: str) -> tuple[int, str, str, datetime, datetime]:
            self.cur.execute(f"insert into {self.name} (uuid, username, first_seen, last_seen) values ('{uuid}', '{username}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);")
            self.commit()

            result: tuple[int, str, str, datetime, datetime] | None = self.find(uuid=uuid, username=username)
            if result is None:
                raise Exception("DB error when inserting value.")

            return result

        def get(self, uuid: str) -> tuple[int, str, str, datetime, datetime] | None:
            return self.find(uuid=uuid)

    class ServerPlayers(Table):
        def __init__(self, conn: connection, cur: cursor) -> None:
            super().__init__(conn, cur)
            self.name = "server_players"

        def add(self, player_id: int, server_id: int) -> tuple[int, int, int, datetime, datetime]:
            self.cur.execute(f"insert into {self.name} (player_id, server_id, first_seen, last_seen) values ({player_id}, {server_id}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);")
            self.commit()

            result: tuple[int, int, int, datetime, datetime] | None = self.find(player_id=player_id, server_id=server_id)
            if result is None:
                raise Exception("DB error when inserting value.")

            return result

        def get(self, player_id: int, server_id: int) -> tuple[int, int, int, datetime, datetime] | None:
            return self.find(player_id=player_id, server_id=server_id)

    class ServerUptime(Table):
        def __init__(self, conn: connection, cur: cursor) -> None:
            super().__init__(conn, cur)
            self.name = "server_uptime"

        def add(self, server_id: int) -> tuple[int, int, int, datetime]:
            self.cur.execute(f"insert into {self.name} (server_id, total_uptime, last_online) values ({server_id}, 0, CURRENT_TIMESTAMP);")
            self.commit()

            result: tuple[int, int, int, datetime] | None = self.find(server_id=server_id)
            if result is None:
                raise Exception("DB error when inserting value.")

            return result

        def get(self, server_id: int) -> tuple[int, int, int, datetime] | None:
            return self.find(server_id=server_id)

    class Servers(Table):
        def __init__(self, conn: connection, cur: cursor) -> None:
            super().__init__(conn, cur)
            self.name = "servers"

        def add(self, name: str, ip_address: str) -> tuple[int, str, str]:
            self.cur.execute(f"insert into {self.name} (name, ip_address) values ('{name}', '{ip_address}');")
            self.commit()

            result: tuple[int, str, str] | None = self.find(ip_address=ip_address)
            if result is None:
                raise Exception("DB error when inserting value.")

            return result

        def get(self, ip_address: str) -> tuple[int, str, str] | None:
            return self.find(ip_address=ip_address)

    class Sessions(Table):
        def __init__(self, conn: connection, cur: cursor) -> None:
            super().__init__(conn, cur)
            self.name = "sessions"

        def add(self, token: str, player_id: int) -> tuple[int, str, int, datetime, datetime]:
            self.cur.execute(f"insert into {self.name} (token, player_id, created, last_used) values ('{token}', {player_id}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);")
            self.commit()

            result: tuple[int, str, int, datetime, datetime] | None = self.find(token=token)
            if result is None:
                raise Exception("DB error when inserting value.")

            return result

        @overload(str)
        def get(self, token: str) -> tuple[int, str, int, datetime, datetime] | None:  # type: ignore
            return self.find(token=token)

        @overload(int)
        def get(self, player_id: int) -> tuple[int, str, int, datetime, datetime] | None:  # noqa: F811
            return self.find(player_id=player_id)

    class SurfaceBlocks(Table):
        def __init__(self, conn: connection, cur: cursor) -> None:
            super().__init__(conn, cur)
            self.name = "surface_blocks"

        def add(self, chunk_id: int, block: int, global_y: int, offset_x: int, offset_z: int) -> tuple[int, int, int, int, int, int]:
            self.cur.execute(f"insert into {self.name} (chunk_id, block, global_y, offset_x, offset_z) values ({chunk_id}, {block}, {global_y}, {offset_x}, {offset_z});")
            self.commit()

            result: tuple[int, int, int, int, int, int] | None = self.find(chunk_id=chunk_id, offset_x=offset_x, offset_z=offset_z)
            if result is None:
                raise Exception("DB error when inserting value.")

            return result

        def get(self, chunk_id: int, offset_x: int, offset_z: int) -> tuple[int, int, int, int, int, int] | None:
            return self.find(chunk_id=chunk_id, offset_x=offset_x, offset_z=offset_z)

    def __init__(self) -> None:
        self.conn: connection = psycopg2.connect(
            host="postgres" if is_docker() else "localhost",
            port="5432",
            database="connectorlib",
            user="connectorlib",
            password="connectorlib",
        )
        self.cur: cursor = self.conn.cursor()

        self.biomes = self.LookupTable(self.conn, self.cur, "biomes")
        self.blocks = self.LookupTable(self.conn, self.cur, "blocks")
        self.dimensions = self.LookupTable(self.conn, self.cur, "dimensions")

        self.chunks = self.Chunks(self.conn, self.cur)
        self.locations = self.Locations(self.conn, self.cur)
        self.messages = self.Messages(self.conn, self.cur)
        self.network_data = self.NetworkData(self.conn, self.cur)
        self.players = self.Players(self.conn, self.cur)
        self.server_players = self.ServerPlayers(self.conn, self.cur)
        self.server_uptime = self.ServerUptime(self.conn, self.cur)
        self.servers = self.Servers(self.conn, self.cur)
        self.sessions = self.Sessions(self.conn, self.cur)
        self.surface_blocks = self.SurfaceBlocks(self.conn, self.cur)

    def setup(self) -> None:
        self.cur.execute("""
            SELECT s.nspname as schema_name, t.relname as table_name
            FROM pg_class t 
            JOIN pg_namespace s ON s.oid = t.relnamespace
            WHERE t.relkind = 'r'
            AND s.nspname !~ '^pg_' 
            AND s.nspname != 'information_schema'
            ORDER BY 1, 2;
        """)

        for schema, table in self.cur.fetchall():
            print(f"Dropping {schema}.{table}")
            self.cur.execute(sql.SQL("DROP TABLE IF EXISTS {}.{} CASCADE").format(sql.Identifier(schema), sql.Identifier(table)))

        print("Creating new tables and relations")
        with open("config/setup.sql", "r") as f:
            self.cur.execute(f.read().strip())

        try:
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise e


class Definitions:
    db: DB

    def __init__(self, db: DB):
        self.db = db

    class Biome:
        id: int
        val: str

        def __init__(self, biome: str):
            self.val = biome

            obj = db.biomes.get(biome)
            self.id = obj[0] if obj is not None else db.biomes.add(biome)[0]

    class Block:
        id: int
        val: str

        def __init__(self, block: str):
            self.val = block

            obj = db.blocks.get(block)
            self.id = obj[0] if obj is not None else db.blocks.add(block)[0]

    class Dimension:
        id: int
        val: str

        def __init__(self, dimension: str):
            self.val = dimension

            obj = db.dimensions.get(dimension)
            self.id = obj[0] if obj is not None else db.dimensions.add(dimension)[0]

    class Chunk:
        id: int
        server: Definitions.Server
        dimension: Definitions.Dimension
        biome: Definitions.Biome
        surface_y: int
        chunk_x: int
        chunk_z: int

        def __init__(
            self,
            server: Definitions.Server,
            dimension: Definitions.Dimension,
            biome: Definitions.Biome,
            surface_y: int,
            chunk_x: int,
            chunk_z: int,
        ):
            self.server = server
            self.dimension = dimension
            self.biome = biome
            self.surface_y = surface_y
            self.chunk_x = chunk_x
            self.chunk_z = chunk_z

            obj = db.chunks.get(server.id, dimension.id, chunk_x, chunk_z)
            self.id = obj[0] if obj is not None else db.chunks.add(server.id, dimension.id, biome.id, surface_y, chunk_x, chunk_z)[0]

    class Location:
        id: int
        server_player: Definitions.ServerPlayer
        dimension: Definitions.Dimension
        global_x: int
        global_y: int
        global_z: int
        visited: datetime

        def __init__(
            self,
            server_player: Definitions.ServerPlayer,
            dimension: Definitions.Dimension,
            global_x: int,
            global_y: int,
            global_z: int,
        ):
            self.server_player = server_player
            self.dimension = dimension
            self.global_x = global_x
            self.global_y = global_y
            self.global_z = global_z

            obj = db.locations.get(server_player.id, dimension.id, global_x, global_y, global_z)
            self.id = obj[0] if obj is not None else db.locations.add(server_player.id, dimension.id, global_x, global_y, global_z)[0]
            self.visited = obj[6] if obj is not None else datetime.now()

    class Message:
        id: int
        server_player: Definitions.ServerPlayer
        message: str
        from_uuid: UUID
        to_uuid: UUID

        def __init__(
            self,
            server_player: Definitions.ServerPlayer,
            message: str,
            from_uuid: UUID,
            to_uuid: UUID,
        ):
            self.server_player = server_player
            self.message = message
            self.from_uuid = from_uuid
            self.to_uuid = to_uuid

            obj = db.messages.get(server_player.id, message, from_uuid.hex, to_uuid.hex)
            self.id = obj[0] if obj is not None else db.messages.add(server_player.id, message, from_uuid.hex, to_uuid.hex)[0]

    class NetworkData:
        id: int
        player: Definitions.Player
        ip_address: str
        user_agent: str
        via: str
        forwarded: list[str]

        def __init__(
            self,
            player: Definitions.Player,
            ip_address: str,
            user_agent: str,
            via: str,
            forwarded: list[str],
        ):
            self.player = player
            self.ip_address = ip_address
            self.user_agent = user_agent
            self.via = via
            self.forwarded = forwarded

            obj = db.network_data.get(player.id, ip_address, user_agent)
            self.id = obj[0] if obj is not None else db.network_data.add(player.id, ip_address, user_agent, via, ",".join(forwarded))[0]

    class Player:
        id: int
        uuid: UUID
        username: str

        def __init__(
            self,
            uuid: UUID,
            username: str,
        ):
            self.uuid = uuid
            self.username = username

            obj = db.players.get(uuid.hex)
            self.id = obj[0] if obj is not None else db.players.add(uuid.hex, username)[0]

    class ServerPlayer:
        id: int
        player: Definitions.Player
        server: Definitions.Server

        def __init__(
            self,
            player: Definitions.Player,
            server: Definitions.Server,
        ):
            self.player = player
            self.server = server

            obj = db.server_players.get(player.id, server.id)
            self.id = obj[0] if obj is not None else db.server_players.add(player.id, server.id)[0]

    class ServerUptime:
        id: int
        server: Definitions.Server
        total_uptime: int

        def __init__(
            self,
            server: Definitions.Server,
        ):
            self.server = server

            obj = db.server_uptime.get(server.id)
            if obj is None:
                self.total_uptime = 0
                self.id = db.server_uptime.add(server.id)[0]
            else:
                self.total_uptime = obj[2]
                self.id = obj[0]

    class Server:
        id: int
        name: str
        ip_address: str

        def __init__(
            self,
            name: str,
            ip_address: str,
        ):
            self.name = name
            self.ip_address = ip_address

            obj = db.servers.get(ip_address)
            self.id = obj[0] if obj is not None else db.servers.add(name, ip_address)[0]

    class Session:
        id: int
        token: str
        player: Definitions.Player

        def __init__(
            self,
            token: str,
            player: Definitions.Player,
        ) -> None:
            self.token = token
            self.player = player

            obj = db.sessions.get(player.id)
            self.id = obj[0] if obj is not None else db.sessions.add(token, player.id)[0]

    class SurfaceBlock:
        id: int
        chunk: Definitions.Chunk
        block: Definitions.Block
        global_y: int
        offset_x: int
        offset_z: int

        def __init__(
            self,
            chunk: Definitions.Chunk,
            block: Definitions.Block,
            global_y: int,
            offset_x: int,
            offset_z: int,
        ) -> None:
            self.chunk = chunk
            self.block = block
            self.global_y = global_y
            self.offset_x = offset_x
            self.offset_z = offset_z

            obj = db.surface_blocks.get(chunk.id, offset_x, offset_z)
            self.id = obj[0] if obj is not None else db.surface_blocks.add(chunk.id, block.id, global_y, offset_x, offset_z)[0]


if __name__ == "__main__":
    db = DB()
    db.setup()

    definitions = Definitions(db)
    biome = definitions.Biome("plains")
    block = definitions.Block("gravel")
    dimension = definitions.Dimension("overworld")

    server = definitions.Server("Arlie Server", "mc.axo.llc")
    player = definitions.Player(UUID(int=1), "floridarosie")

    server_uptime = definitions.ServerUptime(server)
    chunk = definitions.Chunk(server, dimension, biome, 64, 3, 4)

    network_data = definitions.NetworkData(player, "5.4.3.2", "Java 21.6", "google v1.1", ["5.4.3.2", "8.8.8.8"])
    session = definitions.Session("thisismytoken", player)

    server_player = definitions.ServerPlayer(player, server)
    location = definitions.Location(server_player, dimension, 12, 65, 186)
    message = definitions.Message(server_player, "Hello, World!", UUID(int=1), UUID(int=0))
    surface_block = definitions.SurfaceBlock(chunk, block, 63, 0, 0)

    print(f"{biome.id=}, {block.id=}, {dimension.id=}, {server.id=}, {player.id=}, {server_uptime.id=}, {chunk.id=}, {network_data.id=}, {session.id=}, {server_player.id=}, {location.id=}, {message.id=}, {surface_block.id=}")
