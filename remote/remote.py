from json import loads
from pypresence import Presence
from socketio import Client
from requests import get
from time import sleep
from threading import Thread

print("Reading config file")
with open("remoteConfig.json", "r") as file:
    config: dict[str, str] = loads(file.read())
    print("Config file read successfully")

RPC: Presence = Presence(config["discordClientId"])

socketio: Client = Client()

currentlyPlaying: dict[str, dict[str, str | int]] = {}
lastPlayed: currentlyPlaying = {}


def clearRPC(delay: float) -> None:
    """
    This function clears the Discord RPC status.
    """

    #
    lastPlayed.clear()
    lastPlayed.update(currentlyPlaying)
    currentlyPlaying.clear()
    sleep(delay)
    if len(currentlyPlaying) == 0:
        RPC.clear()
        print("Cleared Discord RPC status due to the queue being empty.")
        print("If the queue is not empty (This is a bug and should be reported at https://github.com/InactiveGaming13/Plex-RPC/issues), the status will be updated shortly.")


def updatePresence(data: dict[str, str] | None, playing: bool = True) -> None:
    """
    This function updates the Discord RPC status with the provided parameters.

    Args:
        data (dict[str, str]): The data sent from the server.
        playing (bool, optional): Whether the media is playing or not. Defaults to True.
    """
    # Declare albumImage as None so that it always exists.
    albumImage: str | None = None

    # Check if Last.fm is enabled and if the media is playing and if the data is not None.
    if config["lastFmEnabled"] and playing and data:
        # Convert the metadataArtists string to a list and get the first artist.
        artist: str = data["metadataArtists"].split(";")[0]
        # Create the Last.fm request URL.
        lastFmRequest: str = f"https://ws.audioscrobbler.com/2.0/?method=album.getInfo&api_key={config["lastFmApiKey"]}&artist={artist}&album={data["albumName"]}&format=json"
        # Get the Last.fm response.
        lastFmResponse: dict[str, str] = get(lastFmRequest).json()
        # Get the album image from the Last.fm response.
        albumImage = lastFmResponse["album"]["image"][3]["#text"] if "album" in lastFmResponse else "plex-icon"

    # Check if the media is playing and if the data is not None.
    if playing and data:
        # Replace the semicolon with a comma and space in the metadataArtists string.
        data["metadataArtists"] = data["metadataArtists"].replace(";", ", ")

        # Check if the currentlyPlaying dictionary is not empty and clear it.
        if len(currentlyPlaying) > 0:
            currentlyPlaying.clear()

        # Get the last used PID.
        lastUsed: int = 0 if len(lastPlayed) == 0 else 1 if next(iter(lastPlayed.values()))["pid"] == 0 else 0

        # Update the currentlyPlaying dictionary with the data and last used PID.
        currentlyPlaying[data["metadataTitle"]] = {"artist": data["metadataArtists"], "pid": lastUsed}

        # Clear the Discord RPC status so that the new status can be set and there is only one status.
        RPC.clear(next(iter(lastPlayed.values()))["pid"]) if len(lastPlayed) > 0 else None

        # Update the Discord RPC status with the data.
        RPC.update(
            details=data["metadataTitle"],
            state=f"by {data["metadataArtists"]}",
            large_image=albumImage,
            large_text=f"{data["albumName"]}",
            small_image="plex-icon" if albumImage != "plex-icon" else None,
            small_text=f"Listening on {data["serverName"]}",
            type=2
        )
        return

    # This will only happen if the media is not playing.
    match data["eventType"]:
        # If the media is paused, clear the Discord RPC status.
        case "media.pause":
            RPC.clear()

        # If the media is stopped, clear the Discord RPC status if nothing is playing after 5 seconds..
        case "media.stop":
            Thread(target=clearRPC, args=(5,)).start()


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
    updatePresence(data)


@socketio.on("resume")
def resume(data: dict[str, str]) -> None:
    """
    This function is called when the server sends a "resume" event to the client.

    Args:
        data (dict[str, str]): The data sent from the server.
    """
    updatePresence(data)


@socketio.on("pause")
def pause() -> None:
    """
    This function is called when the server sends a "pause" event to the client.
    """
    updatePresence({"eventType": "media.pause"}, False)


@socketio.on("stop")
def stop() -> None:
    """
    This function is called when the server sends a "stop" event to the client.
    """
    updatePresence({"eventType": "media.stop"}, False)


if __name__ == "__main__":
    """
    This is the main function that connects to the server and Discord RPC.
    """
    try:
        print("Connecting to DiscordRPC")
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
