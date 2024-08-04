"""
This is the main file that runs the Flask server and connects to Discord RPC.
This file should be run on the client where the Plex Media Server and Discord are running.
"""

from flask import Flask, request
from json import loads
from pypresence import Presence

app: Flask = Flask(__name__)

discordClientId: str = "YOUR_DISCORD_CLIENT_ID"

RPC: Presence = Presence(discordClientId)

currentlyPlaying: dict[str, str] = {}


def updatePresence(metadataTitle: str, metadataArtists: str, serverName: str, playing: bool = True) -> None:
    """
    This function updates the Discord RPC status with the provided parameters.

    Args:
        metadataTitle (str): The title of the media being played.
        metadataArtists (str): The artist of the media being played.
        serverName (str): The name of the server on which the media is being played.
        playing (bool, optional): Whether the media is playing or not. Defaults to True.
    """
    if playing:
        RPC.update(
            state=f"by {metadataArtists}",
            details=metadataTitle,
            large_image="plex-icon",
            large_text=f"Listening on {serverName}",
            type=2
        )
    else:
        RPC.clear()


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
    # albumName: str = data["Metadata"]["parentTitle"]

    match eventType:
        case "media.play":
            print("Playing")
            currentlyPlaying[metadataTitle] = metadataArtists
            updatePresence(metadataTitle, metadataArtists, serverName)

        case "media.resume":

            print("Resuming")
            updatePresence(metadataTitle, metadataArtists, serverName)

        case "media.pause":
            print("Paused")
            updatePresence(metadataTitle, metadataArtists, serverName, False)

        case "media.stop":
            print("Stopped")
            updatePresence(metadataTitle, metadataArtists, serverName, False)

        case "media.scrobble":
            print("Scrobbled")
            updatePresence(metadataTitle, metadataArtists, serverName)

        case _:
            print("Unknown Event")
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
