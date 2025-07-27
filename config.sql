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
  "ch" int
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
  "server_player" serial,
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
  "server_player" serial,
  "health" serial,
  "hunger" smallint,
  "breath" smallint,
  "protection" smallint,
  "saturation" smallint,
  "exhaustion" smallint,
  "exp_level" int,
  "exp_prog" float,
  "gamemode" serial,
  "ping" smallint,
  "fps" smallint
);

CREATE TABLE "effects" (
  "id" SERIAL PRIMARY KEY,
  "server_player" serial UNIQUE
);

CREATE TABLE "effect" (
  "id" SERIAL PRIMARY KEY,
  "effect" varchar,
  "type" varchar
);

CREATE TABLE "effect_instance" (
  "id" SERIAL PRIMARY KEY,
  "effects" serial,
  "effect" serial,
  "duration" smallint,
  "strength" serial
);

CREATE TABLE "position" (
  "id" SERIAL PRIMARY KEY,
  "server_player" serial,
  "position" float[3],
  "velocity" float[3],
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
  "player" serial
);

CREATE UNIQUE INDEX "unique_player_server" ON "server_player" ("player", "server");

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

ALTER TABLE "effect_instance" ADD FOREIGN KEY ("effects") REFERENCES "effects" ("id");

ALTER TABLE "effects" ADD FOREIGN KEY ("server_player") REFERENCES "server_player" ("id");

ALTER TABLE "attributes" ADD FOREIGN KEY ("gamemode") REFERENCES "gamemode" ("id");

ALTER TABLE "position" ADD FOREIGN KEY ("server_player") REFERENCES "server_player" ("id");

ALTER TABLE "chunk" ADD FOREIGN KEY ("dimension") REFERENCES "dimension" ("id");

ALTER TABLE "chunk" ADD FOREIGN KEY ("biome") REFERENCES "biome" ("id");

ALTER TABLE "position" ADD FOREIGN KEY ("dimension") REFERENCES "dimension" ("id");

ALTER TABLE "messages" ADD FOREIGN KEY ("type") REFERENCES "message_type" ("id");

ALTER TABLE "nearby" ADD FOREIGN KEY ("position") REFERENCES "position" ("id");

ALTER TABLE "nearby" ADD FOREIGN KEY ("player") REFERENCES "player" ("id");

ALTER TABLE "messages" ADD FOREIGN KEY ("server") REFERENCES "server" ("id");
