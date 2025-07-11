CREATE TABLE "players" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "uuid" varchar(32) NOT NULL,
  "username" varchar(32),
  "first_seen" timestamp,
  "last_seen" timestamp
);

CREATE TABLE "network_data" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "player_id" int,
  "ip_address" varchar(16),
  "user_agent" varchar,
  "via" varchar,
  "forwarded" varchar
);

CREATE TABLE "servers" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "name" varchar,
  "ip_address" varchar
);

CREATE TABLE "chunks" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "server_id" int,
  "dimension" int,
  "biome" int,
  "surface_y" int,
  "chunk_x" int,
  "chunk_z" int
);

CREATE TABLE "dimensions" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "value" varchar UNIQUE
);

CREATE TABLE "biomes" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "value" varchar UNIQUE
);

CREATE TABLE "surface_blocks" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "chunk_id" int,
  "block" int,
  "global_y" int,
  "offset_x" int,
  "offset_z" int
);

CREATE TABLE "blocks" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "value" varchar UNIQUE
);

CREATE TABLE "server_players" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "player_id" int,
  "server_id" int,
  "first_seen" timestamp,
  "last_seen" timestamp
);

CREATE TABLE "server_uptime" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "server_id" int UNIQUE,
  "total_uptime" int,
  "last_online" timestamp
);

CREATE TABLE "sessions" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "token" varchar NOT NULL,
  "player_id" int,
  "created" timestamp,
  "last_used" timestamp
);

CREATE TABLE "locations" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "server_player_id" int,
  "dimension" int,
  "global_x" int,
  "global_y" int,
  "global_z" int,
  "visited" timestamp
);

CREATE TABLE "messages" (
  "id" INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  "server_player_id" int,
  "message" varchar,
  "from_uuid" varchar,
  "to_uuid" varchar
);

COMMENT ON COLUMN "network_data"."forwarded" IS 'CSV, eg 1.2.3.4,8.7.6.5';

ALTER TABLE "server_players" ADD FOREIGN KEY ("player_id") REFERENCES "players" ("id");

ALTER TABLE "server_players" ADD FOREIGN KEY ("server_id") REFERENCES "servers" ("id");

ALTER TABLE "sessions" ADD FOREIGN KEY ("player_id") REFERENCES "players" ("id");

ALTER TABLE "network_data" ADD FOREIGN KEY ("player_id") REFERENCES "players" ("id");

ALTER TABLE "chunks" ADD FOREIGN KEY ("dimension") REFERENCES "dimensions" ("id");

ALTER TABLE "surface_blocks" ADD FOREIGN KEY ("block") REFERENCES "blocks" ("id");

ALTER TABLE "chunks" ADD FOREIGN KEY ("biome") REFERENCES "biomes" ("id");

ALTER TABLE "server_uptime" ADD FOREIGN KEY ("server_id") REFERENCES "servers" ("id");

ALTER TABLE "chunks" ADD FOREIGN KEY ("server_id") REFERENCES "servers" ("id");

ALTER TABLE "surface_blocks" ADD FOREIGN KEY ("chunk_id") REFERENCES "chunks" ("id");

ALTER TABLE "locations" ADD FOREIGN KEY ("dimension") REFERENCES "dimensions" ("id");

ALTER TABLE "locations" ADD FOREIGN KEY ("server_player_id") REFERENCES "server_players" ("id");

ALTER TABLE "messages" ADD FOREIGN KEY ("server_player_id") REFERENCES "server_players" ("id");
