import psycopg2


class CURRENT_TIMESTAMP:
    def __str__(self):
        return "CURRENT_TIMESTAMP"


class DB:
    class Table:
        def __init__(self, conn, cur) -> None:
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

        def _add(self, **kwargs) -> int:
            _fields = list(kwargs.keys())
            fields = ", ".join(_fields)
            _values = [f"'{v}'" if type(v) is str else str(v) for v in kwargs.values()]
            values = ", ".join(_values)

            self.cur.execute(f"select column_name from information_schema.columns where table_name = '{self.name}' and data_type like 'timestamp%%';")
            timestamps = [str(i[0]) for i in self.cur.fetchall()]
            _where = []
            for f, v in zip(_fields, _values):
                if f not in timestamps:
                    _where.append(f"{f} = {v}")
            where = " and ".join(_where)

            self.cur.execute(f"select id from {self.name} where {where};")
            items = self.cur.fetchall()
            if items is not None and len(items) != 0:
                return items[0][0]

            self.cur.execute(f"insert into {self.name} ({fields}) values ({values});")
            self.commit()

            self.cur.execute(f"select id from {self.name} where {where} limit 1;")
            return self.cur.fetchone()[0]

        def _get(self, **kwargs) -> tuple:
            pass

    class LookupTable(Table):
        def __init__(self, conn, cur, name: str) -> None:
            super().__init__(conn, cur)
            self.name = name

        def add(self, value: str) -> int:
            return self._add(
                value=value,
            )

        def remove(self, value: str) -> None:
            self.cur.execute(f"select id from {self.name} where value = '{value}';")
            items = self.cur.fetchone()
            if items is None or len(items) == 0:
                return

            self.cur.execute(f"delete from {self.name} where value = '{value}';")
            self.commit()

    class Chunks(Table):
        def __init__(self, conn, cur) -> None:
            super().__init__(conn, cur)
            self.name = "chunks"

        def add(self, server_id: int, dimension: int, biome: int, surface_y: int, chunk_x: int, chunk_z: int) -> int:
            return self._add(
                server_id=server_id,
                dimension=dimension,
                biome=biome,
                surface_y=surface_y,
                chunk_x=chunk_x,
                chunk_z=chunk_z,
            )

    class Locations(Table):
        def __init__(self, conn, cur):
            super().__init__(conn, cur)
            self.name = "locations"

        def add(self, server_player_id: int, dimension: int, global_x: int, global_y: int, global_z: int):
            return self._add(
                server_player_id=server_player_id,
                dimension=dimension,
                global_x=global_x,
                global_y=global_y,
                global_z=global_z,
                visited=CURRENT_TIMESTAMP(),
            )

    class Messages(Table):
        def __init__(self, conn, cur):
            super().__init__(conn, cur)
            self.name = "messages"

        def add(self, server_player_id: int, message: str):
            return self._add(
                server_player_id=server_player_id,
                message=message,
            )

    class NetworkData(Table):
        def __init__(self, conn, cur) -> None:
            super().__init__(conn, cur)
            self.name = "network_data"

        def add(self, player_id: int, ip_address: str, user_agent: str, via: str, forwarded: str) -> int:
            return self._add(
                player_id=player_id,
                ip_address=ip_address,
                user_agent=user_agent,
                via=via,
                forwarded=forwarded,
            )

    class Players(Table):
        def __init__(self, conn, cur) -> None:
            super().__init__(conn, cur)
            self.name = "players"

        def add(self, uuid: str, username: str) -> int:
            return self._add(
                uuid=uuid,
                username=username,
                first_seen=CURRENT_TIMESTAMP(),
                last_seen=CURRENT_TIMESTAMP(),
            )

    class ServerPlayers(Table):
        def __init__(self, conn, cur) -> None:
            super().__init__(conn, cur)
            self.name = "server_players"

        def add(self, player_id: int, server_id: int) -> int:
            return self._add(
                player_id=player_id,
                server_id=server_id,
                first_seen=CURRENT_TIMESTAMP(),
                last_seen=CURRENT_TIMESTAMP(),
            )

    class ServerUptime(Table):
        def __init__(self, conn, cur) -> None:
            super().__init__(conn, cur)
            self.name = "server_uptime"

        def add(self, server_id: int) -> int:
            return self._add(
                server_id=server_id,
                total_uptime=0,
                last_online=CURRENT_TIMESTAMP(),
            )

    class Servers(Table):
        def __init__(self, conn, cur) -> None:
            super().__init__(conn, cur)
            self.name = "servers"

        def add(self, name: str, ip_address: str) -> int:
            return self._add(
                name=name,
                ip_address=ip_address,
            )

    class Sessions(Table):
        def __init__(self, conn, cur) -> None:
            super().__init__(conn, cur)
            self.name = "sessions"

        def add(self, token: str, player_id: int) -> int:
            return self._add(
                token=token,
                player_id=player_id,
                created=CURRENT_TIMESTAMP(),
                last_used=CURRENT_TIMESTAMP(),
            )

    class SurfaceBlocks(Table):
        def __init__(self, conn, cur) -> None:
            super().__init__(conn, cur)
            self.name = "surface_blocks"

        def add(self, chunk_id: int, block: int, global_y: int, offset_x: int, offset_z: int) -> int:
            return self._add(
                chunk_id=chunk_id,
                block=block,
                global_y=global_y,
                offset_x=offset_x,
                offset_z=offset_z,
            )

    def __init__(self) -> None:
        # conn = psycopg2.connect(host="postgres", port="5432", database="connectorlib", user="connectorlib", password="connectorlib")
        self.conn = psycopg2.connect(host="localhost", port="5432", database="connectorlib", user="connectorlib", password="connectorlib")
        self.cur = self.conn.cursor()

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


if __name__ == "__main__":
    db = DB()
    print("DB Ready!")

    biome = db.biomes.add("taiga")
    block = db.blocks.add("stone")
    dimension = db.dimensions.add("overworld")

    server = db.servers.add("Arlie Server", "mc.axo.llc")
    server2 = db.servers.add("James Server", "lag.aternos.me")
    uptime = db.server_uptime.add(server)
    uptime2 = db.server_uptime.add(server2)
    chunk = db.chunks.add(server, dimension, biome, 64, 3, 2)
    chunk2 = db.chunks.add(server, dimension, biome, 64, 4, 2)
    chunk3 = db.chunks.add(server2, dimension, biome, 64, 3, 2)
    chunk4 = db.chunks.add(server2, dimension, biome, 64, 4, 2)
    surface = db.surface_blocks.add(chunk, block, 65, 0, 0)
    surface2 = db.surface_blocks.add(chunk2, block, 63, 0, 0)
    surface3 = db.surface_blocks.add(chunk3, block, 64, 7, 0)
    surface4 = db.surface_blocks.add(chunk4, block, 61, 0, 1)

    player = db.players.add("e39ee8310599438fb107cf97e246fc92", "Biffot")
    player2 = db.players.add("62eaea5762cb458c8007d6c5e652c2a7", "floridarosie")
    network = db.network_data.add(player, "1.2.3.4", "My/Agent 1.2", "1.1 google", "1.2.3.4,8.7.6.5")
    network2 = db.network_data.add(player2, "1.2.3.4", "My/Agent 1.2", "1.1 google", "1.2.3.4,8.7.6.5")
    session = db.sessions.add("mytokenhere", player)
    session2 = db.sessions.add("anothertoken", player)
    splayer = db.server_players.add(player, server)
    splayer2 = db.server_players.add(player, server2)
    splayer3 = db.server_players.add(player2, server)
    splayer4 = db.server_players.add(player2, server2)

    location = db.locations.add(splayer, dimension, 1, 2, 3)
    message = db.messages.add(splayer2, "this is a test message")
