from flask import Flask, request
from flask_socketio import SocketIO
from json import loads

# Create the Flask app and the SocketIO instance.
app: Flask = Flask(__name__)
socketio: SocketIO = SocketIO(app)

currentlyPlaying: dict[str, str] | None = {}


@app.route("/", methods=["POST"])
def index() -> str:
    """
    This function is called when the Plex webhook sends a POST request to the server.

    It then parses the JSON data and updates the Discord RPC status accordingly.

    Returns:
        str: Returns "OK" to the Plex webhook to confirm that the server received
    """
    # Parse the JSON data from the POST request.
    data = loads(request.form["payload"])
    # Extract the required data from the JSON data.
    eventType: str = data["event"]
    # accountName: str = data["Account"]["title"]
    # accountPhoto: str = data["Account"]["thumb"]
    serverName: str = data["Server"]["title"]
    metadataTitle: str = data["Metadata"]["title"] if data["Metadata"]["title"] != "" else "Unknown Title"
    metadataArtists: str = data["Metadata"]["originalTitle"] if "originalTitle" in data["Metadata"] else data["Metadata"]["grandparentTitle"]
    directoryArtists: str = data["Metadata"]["grandparentTitle"] if data["Metadata"]["grandparentTitle"] != metadataArtists else None
    albumName: str = data["Metadata"]["parentTitle"]

    # Match the event types and send the corresponding event to the client.
    match eventType:
        case "media.play":
            currentlyPlaying.update({
                "metadataTitle": metadataTitle,
                "metadataArtists": metadataArtists,
                "directoryArtists": directoryArtists,
                "albumName": albumName,
                "serverName": serverName
            })
            socketio.emit("play", {
                "metadataTitle": metadataTitle,
                "metadataArtists": metadataArtists,
                "directoryArtists": directoryArtists,
                "albumName": albumName,
                "serverName": serverName
            })

        case "media.resume":
            currentlyPlaying.update({
                "metadataTitle": metadataTitle,
                "metadataArtists": metadataArtists,
                "directoryArtists": directoryArtists,
                "albumName": albumName,
                "serverName": serverName
            })
            socketio.emit("resume", {
                "metadataTitle": metadataTitle,
                "metadataArtists": metadataArtists,
                "directoryArtists": directoryArtists,
                "albumName": albumName,
                "serverName": serverName
            })

        case "media.pause":
            currentlyPlaying.clear()
            socketio.emit("pause")

        case "media.stop":
            currentlyPlaying.clear()
            socketio.emit("stop")

        case "media.scrobble":
            currentlyPlaying.update({
                "metadataTitle": metadataTitle,
                "metadataArtists": metadataArtists,
                "directoryArtists": directoryArtists,
                "albumName": albumName,
                "serverName": serverName
            })
            socketio.emit("scrobble", {
                "metadataTitle": metadataTitle,
                "metadataArtists": metadataArtists,
                "directoryArtists": directoryArtists,
                "albumName": albumName,
                "serverName": serverName
            })

        case _:
            print(f"Unknown Event -> {eventType}")
            pass

    return "OK"


@socketio.on("connect")
def connect() -> None:
    """
    This function is called when the client connects to the server.
    """
    # Print the client's IP address when they connect to the server (If running through NGINX, this will always read as 127.0.0.1).
    print(f"Client connected! -> {request.remote_addr}")

    # If there is a currently playing song, send the data to the client.
    if currentlyPlaying:
        socketio.emit("play", currentlyPlaying)


@socketio.on("disconnect")
def disconnect() -> None:
    """
    This function is called when the client disconnects from the server.
    """
    # Print the client's IP address when they disconnect from the server (If running through NGINX, this will always read as 127.0.0.1).
    print(f"Disconnected from server! -> {request.remote_addr}")


if __name__ == "__main__":
    """
    This is the main function that runs the Flask server and connects to Discord RPC.
    """
    # Run the Flask server on port 8080.
    socketio.run(app)
