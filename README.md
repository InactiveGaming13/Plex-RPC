# Plex-RPC
A simple app for Tracking listening status on Plex, and displaying it on DiscordRPC.

This app was created to display the current status of the Plex server on Discord. This app uses the Plex Webhooks to track the current status of the Plex server
and displays it on Discord using the DiscordRPC.

Included in this repository are three files: `main.py`, `server.py`, and `remote.py`.

- `main.py` is the main file that should be run on the same machine as the Discord client.
- `server.py` is the main file that should be run on a different machine than the Discord client.
- `remote.py` is a file that should be run on the same machine as the Discord client to receive the status updates from the server.

Please follow the [Installation](#installation) instructions below to get started.

---

## Installation

### Running on the same machine as Discord
1. Clone the repository.
2. (Optional but recommended) Create a virtual environment with `python -m venv venv`.
3. Install the requirements with `pip install -r requirements.txt`.
4. Run the app with `python main.py`.
5. Open Discord and start watching something on Plex.

---

### Running on a different machine (e.g. a Raspberry Pi for server hosting)
1. Clone the repository to the server machine.
2. (Optional but recommended) Create a virtual environment with `python -m venv venv`.
3. Install the requirements with `pip install -r requirements.txt`.
4. Configure the `config.json` file with the IP address of the Plex server Webhook.
5. Run the app with `python server.py`.
6. On the machine running Discord, configure the `config.json` file with the IP address of the server machine.
7. Start `remote.py` on the Discord machine.
8. Open Discord and start watching something on Plex.
