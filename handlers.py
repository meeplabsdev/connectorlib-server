from messages import auth, data, player

HANDLERS = {
    "IdentityRequest": auth.IdentityRequest,
    "IdentityChallenge": auth.IdentityChallenge,
    "DataRequest": data.DataRequest,
    "NetworkData": data.NetworkData,
    "PositionData": data.PositionData,
    "ChatData": data.ChatData,
    "SystemChatData": data.SystemChatData,
    "PlayerJoin": player.PlayerJoin,
    "PlayerQuit": player.PlayerQuit,
    "PlayerRespawn": player.PlayerRespawn,
    "PlayerAdvancement": player.PlayerAdvancement,
}
