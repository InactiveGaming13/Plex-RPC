from flask import Flask, request
from flask_socketio import SocketIO, emit
from json import loads

app: Flask = Flask(__name__)
socketio: SocketIO = SocketIO(app)


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
    metadataArtists: str = data["Metadata"]["originalTitle"] if "originalTitle" in data["Metadata"] else data["Metadata"]["grandparentTitle"]
    # albumName: str = data["Metadata"]["parentTitle"]

    match eventType:
        case "media.play":
            print("Playing")
            emit("play", {"metadataTitle": metadataTitle, "metadataArtists": metadataArtists, "serverName": serverName}, broadcast=True)

        case "media.resume":
            print("Resuming")
            emit("resume", {"metadataTitle": metadataTitle, "metadataArtists": metadataArtists, "serverName": serverName}, broadcast=True)

        case "media.pause":
            print("Paused")
            emit("pause", {"metadataTitle": metadataTitle, "metadataArtists": metadataArtists, "serverName": serverName}, broadcast=True)

        case "media.stop":
            print("Stopped")
            emit("stop", {"metadataTitle": metadataTitle, "metadataArtists": metadataArtists, "serverName": serverName}, broadcast=True)

        case "media.scrobble":
            print("Scrobbled")

        case _:
            print("Unknown Event")
            pass

    return "OK"


@socketio.on("connect")
def connect() -> None:
    """
    This function is called when the client connects to the server.
    """
    print(f"Client connected! -> {request.remote_addr}")


@socketio.on("disconnect")
def disconnect() -> None:
    """
    This function is called when the client disconnects from the server.
    """
    print(f"Disconnected from server! -> {request.remote_addr}")


if __name__ == "__main__":
    """
    This is the main function that runs the Flask server and connects to Discord RPC.
    """
    try:
        socketio.run(app, host="127.0.0.1", port=8080)
    except KeyboardInterrupt:
        print("Exiting")
        emit("ServerShutdown", broadcast=True)
        exit(0)
