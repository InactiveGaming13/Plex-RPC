"""
This is the main file that runs the Flask server and connects to Discord RPC.
This file should be run on the client where the Plex Media Server and Discord are running.
"""

from flask import Flask, request
from json import loads
from pypresence import Presence
from requests import get
from threading import Thread
from time import sleep

# Get the config params.
print("Reading config file")
with open("remoteConfig.json", "r") as file:
    config: dict[str, str] = loads(file.read())
    print("Config file read successfully")

app: Flask = Flask(__name__)

RPC: Presence = Presence(config["discordClientId"])

# Declare the currentlyPlaying and lastPlayed dictionaries.
currentlyPlaying: dict[str, dict[str, str | int]] = {}
lastPlayed: currentlyPlaying = {}


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


@app.post("/")
def index() -> str:
    """
    This function is called when the Plex webhook sends a POST request to the server.

    It then parses the JSON data and updates the Discord RPC status accordingly.

    Returns:
        str: Returns "OK" to the Plex webhook to confirm that the server received
    """
    data = loads(request.form["payload"])
    eventType: str = data["event"]
    # accountName: str = data["Account"]["title"]
    # accountPhoto: str = data["Account"]["thumb"]
    serverName: str = data["Server"]["title"]
    metadataTitle: str = data["Metadata"]["title"]
    # Below is required as the "originalTitle" key is only present when the grandparentTitle is different to the artist's name.
    metadataArtists: str = data["Metadata"]["originalTitle"] if "originalTitle" in data["Metadata"] else data["Metadata"]["grandparentTitle"]
    albumName: str = data["Metadata"]["parentTitle"]

    data: dict[str, str] = {
        "metadataTitle": metadataTitle,
        "metadataArtists": metadataArtists,
        "albumName": albumName,
        "serverName": serverName
    }

    match eventType:
        case "media.play":
            updatePresence(data)

        case "media.resume":
            updatePresence(data)

        case "media.pause":
            updatePresence({"eventType": "media.pause"}, False)

        case "media.stop":
            updatePresence({"eventType": "media.stop"}, False)

        case "media.scrobble":
            pass

        case _:
            print(f"Unknown Event -> {eventType}")
            pass

    return "OK"


if __name__ == "__main__":
    """
    This is the main function that runs the Flask server and connects to Discord RPC.
    """
    try:
        print("Connecting to Discord RPC")
        RPC.connect()
        print("Connected to Discord RPC")
        print("Starting Flask Server")
        app.run(debug=False, host="0.0.0.0", port=8015)
    except KeyboardInterrupt:
        print("Closing Discord RPC Connection")
        RPC.close()
        print("Exiting")
        exit(0)
