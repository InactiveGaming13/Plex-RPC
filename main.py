from flask import Flask, request
from json import loads
from pypresence import Presence

app: Flask = Flask(__name__)

discordClientId: str = "YOUR_DISCORD_CLIENT_ID"

RPC: Presence = Presence(discordClientId)


def updatePresence(metadataTitle: str, metadataArtists: str, serverName: str, playing: bool = True) -> None:
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


@app.route("/", methods=["POST"])
def index() -> str:
    data = loads(request.form["payload"])
    eventType: str = data["event"]
    accountName: str = data["Account"]["title"]
    accountPhoto: str = data["Account"]["thumb"]
    serverName: str = data["Server"]["title"]
    metadataTitle: str = data["Metadata"]["title"]
    metadataArtists: str = data["Metadata"]["originalTitle"] if "originalTitle" in data["Metadata"] else data["Metadata"]["grandparentTitle"]
    albumName: str = data["Metadata"]["parentTitle"]

    match eventType:
        case "media.play":
            print("Playing")
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
    try:
        RPC.connect()
        app.run(debug=False, host="0.0.0.0", port=8015)
    except KeyboardInterrupt:
        updatePresence("", "", "", False)
        RPC.close()
        exit(0)
