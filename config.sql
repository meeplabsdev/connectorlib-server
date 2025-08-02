CREATE TABLE "gamemode" (
  "id" SERIAL PRIMARY KEY,
  "gamemode" varchar UNIQUE
);

CREATE TABLE "message_type" (
  "id" SERIAL PRIMARY KEY,
  "type" varchar UNIQUE
);

CREATE TABLE "dimension" (
  "id" SERIAL PRIMARY KEY,
  "dimension" varchar UNIQUE
);

CREATE TABLE "biome" (
  "id" SERIAL PRIMARY KEY,
  "biome" varchar UNIQUE
);

CREATE TABLE "item" (
  "id" SERIAL PRIMARY KEY,
  "item" varchar UNIQUE
);

CREATE TABLE "player" (
  "id" SERIAL PRIMARY KEY,
  "uuid" varchar(32) UNIQUE,
  "username" varchar(32),
  "reputation" smallint,
  "added" timestamp,
  "active" timestamp
);

CREATE TABLE "server" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar,
  "ip" varchar UNIQUE,
  "added" timestamp,
  "active" timestamp
);

CREATE TABLE "server_player" (
  "id" SERIAL PRIMARY KEY,
  "player" serial,
  "server" serial,
  "added" timestamp,
  "active" timestamp
);

CREATE TABLE "messages" (
  "id" SERIAL PRIMARY KEY,
  "server" serial,
  "type" serial,
  "message" varchar,
  "pfrom" serial,
  "pto" serial,
  "sent" timestamp
);

CREATE TABLE "chunk" (
  "id" SERIAL PRIMARY KEY,
  "server" serial,
  "dimension" serial,
  "biome" serial,
  "cx" int,
  "cz" int,
  "ch" int[4]
);

CREATE TABLE "network_data" (
  "id" SERIAL PRIMARY KEY,
  "player" serial,
  "ip" varchar UNIQUE,
  "user_agent" varchar,
  "via" varchar,
  "forwarded" varchar,
  "added" timestamp,
  "active" timestamp
);

CREATE TABLE "inventory" (
  "id" SERIAL PRIMARY KEY,
  "server_player" serial UNIQUE,
  "slot_selected" serial
);

CREATE TABLE "item_instance" (
  "id" SERIAL PRIMARY KEY,
  "inventory" serial,
  "item" serial,
  "slot" serial,
  "count" serial,
  "custom" varchar
);

CREATE TABLE "attributes" (
  "id" SERIAL PRIMARY KEY,
  "server_player" serial UNIQUE,
  "health" smallint,
  "hunger" smallint,
  "breath" smallint,
  "protection" smallint,
  "saturation" smallint,
  "exhaustion" smallint,
  "exp_level" int,
  "exp_prog" float4,
  "gamemode" serial,
  "ping" smallint,
  "fps" smallint
);

CREATE TABLE "effect" (
  "id" SERIAL PRIMARY KEY,
  "effect" varchar UNIQUE,
  "colour" smallint,
  "type" varchar
);

CREATE TABLE "effect_instance" (
  "id" SERIAL PRIMARY KEY,
  "attributes" serial,
  "effect" serial,
  "duration" smallint,
  "strength" serial
);

CREATE TABLE "position" (
  "id" SERIAL PRIMARY KEY,
  "server_player" serial,
  "position" float4[3],
  "velocity" float4[3],
  "dimension" serial,
  "sneaking" bool,
  "sprinting" bool,
  "swimming" bool,
  "crawling" bool,
  "grounded" bool,
  "fallflying" bool,
  "added" timestamp
);

CREATE TABLE "nearby" (
  "id" SERIAL PRIMARY KEY,
  "position" serial,
  "player" serial,
  "location" float4[3]
);

CREATE TABLE "deaths" (
  "id" SERIAL PRIMARY KEY,
  "server_player" serial,
  "position" float4[3],
  "added" timestamp
);

CREATE UNIQUE INDEX "unique_player_server" ON "server_player" ("player", "server");

CREATE UNIQUE INDEX "unique_cx_cz" ON "chunk" ("cx", "cz");

ALTER TABLE "server_player" ADD FOREIGN KEY ("player") REFERENCES "player" ("id");

ALTER TABLE "server_player" ADD FOREIGN KEY ("server") REFERENCES "server" ("id");

ALTER TABLE "messages" ADD FOREIGN KEY ("pfrom") REFERENCES "player" ("id");

ALTER TABLE "messages" ADD FOREIGN KEY ("pto") REFERENCES "player" ("id");

ALTER TABLE "chunk" ADD FOREIGN KEY ("server") REFERENCES "server" ("id");

ALTER TABLE "network_data" ADD FOREIGN KEY ("player") REFERENCES "player" ("id");

ALTER TABLE "item_instance" ADD FOREIGN KEY ("inventory") REFERENCES "inventory" ("id");

ALTER TABLE "item_instance" ADD FOREIGN KEY ("item") REFERENCES "item" ("id");

ALTER TABLE "inventory" ADD FOREIGN KEY ("server_player") REFERENCES "server_player" ("id");

ALTER TABLE "attributes" ADD FOREIGN KEY ("server_player") REFERENCES "server_player" ("id");

ALTER TABLE "effect_instance" ADD FOREIGN KEY ("effect") REFERENCES "effect" ("id");

ALTER TABLE "attributes" ADD FOREIGN KEY ("gamemode") REFERENCES "gamemode" ("id");

ALTER TABLE "position" ADD FOREIGN KEY ("server_player") REFERENCES "server_player" ("id");

ALTER TABLE "chunk" ADD FOREIGN KEY ("dimension") REFERENCES "dimension" ("id");

ALTER TABLE "chunk" ADD FOREIGN KEY ("biome") REFERENCES "biome" ("id");

ALTER TABLE "position" ADD FOREIGN KEY ("dimension") REFERENCES "dimension" ("id");

ALTER TABLE "messages" ADD FOREIGN KEY ("type") REFERENCES "message_type" ("id");

ALTER TABLE "nearby" ADD FOREIGN KEY ("position") REFERENCES "position" ("id");

ALTER TABLE "nearby" ADD FOREIGN KEY ("player") REFERENCES "player" ("id");

ALTER TABLE "messages" ADD FOREIGN KEY ("server") REFERENCES "server" ("id");

ALTER TABLE "effect_instance" ADD FOREIGN KEY ("attributes") REFERENCES "attributes" ("id");

ALTER TABLE "deaths" ADD FOREIGN KEY ("server_player") REFERENCES "server_player" ("id");
