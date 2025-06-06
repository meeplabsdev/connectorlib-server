from typing import Type
from messages import auth, data, player, chunk, base

HANDLERS: dict[str, Type[base.BaseHandler]] = {
    "IdentityRequest": auth.IdentityRequest,
    "IdentityChallenge": auth.IdentityChallenge,
    # "NetworkData": data.NetworkData,
    # "PositionData": data.PositionData,
    # "ChatData": data.ChatData,
    # "SystemChatData": data.SystemChatData,
    # "PlayerJoin": player.PlayerJoin,
    # "PlayerQuit": player.PlayerQuit,
    # "PlayerRespawn": player.PlayerRespawn,
    # "PlayerAdvancement": player.PlayerAdvancement,
    # "ChunkRequest": chunk.ChunkRequest,
    # "ChunkData": chunk.ChunkData,
}
