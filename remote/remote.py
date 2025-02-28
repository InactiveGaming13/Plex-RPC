from json import loads
from typing import Any

from pypresence import Presence, ActivityType
from socketio import Client
from requests import get
from time import sleep
from threading import Thread

# Get the config params.
print("Reading config file")
with open("remoteConfig.json", "r") as file:
    config: dict[str, str] = loads(file.read())
    print("Config file read successfully")

# Create the Discord RPC instance.
RPC: Presence = Presence(config["discordClientId"])

# Create the SocketIO client.
socketio: Client = Client()

# Declare the currentlyPlaying and lastPlayed dictionaries.
currentlyPlaying: dict[str, dict[str, str | int]] = {}
lastPlayed: currentlyPlaying = {}

# Declare a LISTENING activity type to make code more readable.
listening: ActivityType.LISTENING = ActivityType.LISTENING


def filterRequestURL(url: str) -> str:
    """
    This function filters the URL to remove the API key.

    Args:
        url (str): The URL to filter.

    Returns:
        str: The filtered URL.
    """
    return url.replace(" ", "+").replace("’", "%27").replace("'", "%27")


def clearRPC(delay: float) -> None:
    """
    This function clears the Discord RPC status.
    """

    # Clear the Discord RPC status after the delay if nothing is being played on the PMS.
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
        def sendRequest(splitArtists: bool = False) -> list[bool | Any]:
            # Convert the metadataArtists string to a list and get the first artist.
            if splitArtists:
                artist: str = data["directoryArtists"] if data["directoryArtists"] is not None else data["metadataArtists"].split(";")[0]
            else:
                artist: str = data["directoryArtists"] if data["directoryArtists"] is not None else data["metadataArtists"]

            # Create the Last.fm request URL.
            lastFmRequest: str = filterRequestURL(
                f"https://ws.audioscrobbler.com/2.0/?method=album.getInfo&api_key={config["lastFmApiKey"]}&artist={artist}&album={data["albumName"]}&format=json"
            )

            # Get the Last.fm response.
            return [get(lastFmRequest).json(), splitArtists]

        lastFmResponse, split = sendRequest()

        if ("error" in lastFmResponse and lastFmResponse["error"] == 6) and not split:
            sendRequest(True)
        elif ("error" in lastFmResponse and lastFmResponse["error"] == 6) and split:
            pass

        # Get the album image from the Last.fm response.
        albumImage = lastFmResponse["album"]["image"][3]["#text"] if "album" in lastFmResponse and lastFmResponse["album"]["image"][3]["#text"] != "" else "plex-icon"

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
            activity_type=listening,
            details=data["metadataTitle"],
            state=data["metadataArtists"],
            large_image=albumImage,
            large_text=f"{data["albumName"]}",
            small_image="plex-icon" if albumImage != "plex-icon" else None,
            small_text=f"Listening on {data["serverName"]}"
        )
        return

    # This will only happen if the media is not playing.
    match data["eventType"]:
        # If the media is paused, clear the Discord RPC status.
        case "media.pause":
            RPC.clear()

        # If the media is stopped, clear the Discord RPC status if nothing is playing after 5 seconds.
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
    print("Disconnected from Socket server, Attempting to reconnect")
    RPC.clear()


@socketio.on("play")
def play(data: dict[str, str]) -> None:
    """
    This function is called when the server sends a "play" event to the client.

    Args:
        data (dict[str, str]): The data sent from the server.
    """
    data["eventType"] = "media.play"
    updatePresence(data)


@socketio.on("resume")
def resume(data: dict[str, str]) -> None:
    """
    This function is called when the server sends a "resume" event to the client.

    Args:
        data (dict[str, str]): The data sent from the server.
    """
    data["eventType"] = "media.resume"
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
    # Attempt to start the connection to the server and Discord RPC.
    try:
        print("Connecting to DiscordRPC")
        RPC.connect()
        print("Connected to DiscordRPC")
        print(f"Connecting to Socket server")
        socketio.connect(f"{config["serverProtocol"]}://{config["serverIp"]}:{config["serverPort"]}")
        socketio.wait()
    except KeyboardInterrupt:  # If the user presses Ctrl+C, the program will safely exit.
        print("Disconnecting from server")
        socketio.disconnect()
        print("Closing Discord RPC")
        RPC.close()
        print("Exiting")
        exit(0)
