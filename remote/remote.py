from json import loads
from pypresence import Presence
from socketio import Client

print("Reading config file")
with open("remoteConfig.json", "r") as file:
    config: dict[str, str] = loads(file.read())

RPC: Presence = Presence(config["discordClientId"])

socketio: Client = Client()

currentlyPlaying: dict[str, str] = {}


def updatePresence(data: dict[str, str] | None, playing: bool = True) -> None:
    """
    This function updates the Discord RPC status with the provided parameters.

    Args:
        data (dict[str, str]): The data sent from the server.
        playing (bool, optional): Whether the media is playing or not. Defaults to True.
    """
    if playing and data:
        if len(currentlyPlaying) > 1:
            currentlyPlaying.clear()
        currentlyPlaying[data["metadataTitle"]] = data["metadataArtists"]
        if not RPC.pipe:
            RPC.connect()
        RPC.update(
            state=f"by {data["metadataArtists"]}",
            details=data["metadataTitle"],
            large_image="plex-icon",
            large_text=f"Listening on {data["serverName"]}",
            type=2
        )
    else:
        currentlyPlaying.clear()
        RPC.clear()


@socketio.on("connect")
def connect() -> None:
    """
    This function is called when the client connects to the server.
    """
    print("Connected to Socket server")


@socketio.on("disconnect")
def disconnect() -> None:
    """
    This function is called when the client disconnects from the server.
    """
    print("Disconnected from Socket server")
    RPC.clear()


@socketio.on("play")
def play(data: dict[str, str]) -> None:
    """
    This function is called when the server sends a "play" event to the client.

    Args:
        data (dict[str, str]): The data sent from the server.
    """
    print("Playing")
    updatePresence(data)


@socketio.on("resume")
def resume(data: dict[str, str]) -> None:
    """
    This function is called when the server sends a "resume" event to the client.

    Args:
        data (dict[str, str]): The data sent from the server.
    """
    print("Resuming")
    updatePresence(data)


@socketio.on("pause")
def pause() -> None:
    """
    This function is called when the server sends a "pause" event to the client.
    """
    print("Paused")
    updatePresence(None, False)


@socketio.on("stop")
def stop() -> None:
    """
    This function is called when the server sends a "stop" event to the client.
    """
    print("Stopped")
    updatePresence(None, False)


if __name__ == "__main__":
    """
    This is the main function that connects to the server and Discord RPC.
    """
    try:
        print("Connecting to DiscordRPC server")
        RPC.connect()
        ip: str = f"{config["serverProtocol"]}://{config["serverIp"]}:{config["serverPort"]}"
        print(f"Connecting to Socket server -> {ip}")
        socketio.connect(ip)
        socketio.wait()
    except KeyboardInterrupt:
        print("Disconnecting from server")
        socketio.disconnect()
        print("Closing Discord RPC")
        RPC.close()
        print("Exiting")
        exit(0)
