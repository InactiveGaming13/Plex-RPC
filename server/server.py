from flask import Flask, request
from flask_socketio import SocketIO
from json import loads

# Read the config file.
print("Reading config file")
with open("serverConfig.json", "r") as file:
    config: dict[str, str] = loads(file.read())
    print("Config file read successfully")

# Create the Flask app and the SocketIO instance.
app: Flask = Flask(__name__)
socketio: SocketIO = SocketIO(app)


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
    print(data)
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
            socketio.emit("play", {
                "metadataTitle": metadataTitle,
                "metadataArtists": metadataArtists,
                "directoryArtists": directoryArtists,
                "albumName": albumName,
                "serverName": serverName
            })

        case "media.resume":
            socketio.emit("resume", {
                "metadataTitle": metadataTitle,
                "metadataArtists": metadataArtists,
                "directoryArtists": directoryArtists,
                "albumName": albumName,
                "serverName": serverName
            })

        case "media.pause":
            socketio.emit("pause")

        case "media.stop":
            socketio.emit("stop")

        case "media.scrobble":
            pass

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
    socketio.run(app, host=config["ip"], port=config["port"])