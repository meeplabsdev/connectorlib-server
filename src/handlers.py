from typing import Type
from messages import BaseHandler, ChatData, ChunkEvent, IdentityEvent, NetworkData, PlayerJoin, PlayerQuit, PlayerRespawn, PositionData, SystemChatData

HANDLERS: dict[str, Type[BaseHandler.BaseHandler]] = {
    "IdentityRequest": IdentityEvent.IdentityRequest,
    "IdentityChallenge": IdentityEvent.IdentityChallenge,
    "NetworkData": NetworkData.NetworkData,
    "PositionData": PositionData.PositionData,
    "ChatData": ChatData.ChatData,
    "SystemChatData": SystemChatData.SystemChatData,
    "PlayerJoin": PlayerJoin.PlayerJoin,
    "PlayerQuit": PlayerQuit.PlayerQuit,
    "PlayerRespawn": PlayerRespawn.PlayerRespawn,
    "ChunkRequest": ChunkEvent.ChunkRequest,
    "ChunkData": ChunkEvent.ChunkData,
}
