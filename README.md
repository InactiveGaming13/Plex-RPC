# Plex-RPC
A simple app for Tracking listening status on Plex, and displaying it on DiscordRPC.

---

### This application requires Plex Pass to function as it uses the Webhooks feature.

### This will also not work with downloads as the Webhooks are not triggered for downloads.

---

Please note the following abbreviations used in the documentation:
- PMS: Plex Media Server
- RPC: Rich Presence
- venv: Virtual Environment

This app was created to display the current status of the Plex server on Discord. This app uses the Plex Webhooks to track the current status of the Plex server
and displays it on Discord using the DiscordRPC.

Included in this repository are three files: `main.py`, `server.py`, and `remote.py`.

- `main.py` is the main file that should be run on the same machine as the Discord client and PMS.
- `server.py` is the main file that should be run on a different machine than the Discord client but the same machine as PMS.
- `remote.py` is a file that should be run on the same machine as the Discord client to receive the status updates from PMS.

Please follow the [Installation](#installation) instructions below to get started.

---

## Installation

## Linux

---

### Running on the same machine as Discord and PMS (e.g. a personal computer running PMS)
1. Clone the repository.
2. (Optional but recommended) Create a venv with `python -m venv venv` and activate it with `source venv/bin/activate`.
3. Install the requirements with `pip install -r requirements.txt` in the `Plex-RPC/main` directory.
4. Configure PMS to send Webhooks to `http://127.0.0.1:8080` as this is the default address the app listens on (or change it to your preference).
5. Configure the `config.json` file with your Discord Application ID and last.fm API key (if using the last.fm album covers).
6. Run the app with `python main.py`, ENSURE THAT DISCORD IS RUNNING FIRST.
7. Start listening to something on Plex and the status should be displayed on Discord.

### Running on a different machine as Discord (e.g. a server running PMS)
1. Clone the repository to the server machine.
2. (Optional but recommended) Create a venv with `python -m venv venv` and activate it with `source venv/bin/activate`.
3. Install the requirements with `pip install -r requirements.txt` in the `Plex-RPC/server` directory.
4. Configure PMS to send Webhooks to `http://127.0.0.1:8080` as this is the default address the app listens on (or change it to your preference).
5. Install nginx with `sudo apt install nginx`.
6. Configure the nginx configuration file to proxy the server to the internet (see the example in `Plex-RPC/server/linExample.conf`).
7. Start nginx with `sudo systemctl start nginx` or `sudo service nginx start`.
8. Run the app with `python server.py`.
9. On the machine running Discord, configure the `remoteConfig.json` file with the IP address of the server machine (STRONGLY RECOMMENDED: Use NGINX even on a local connection).
10. (Optional but recommended) Create a venv with `python -m venv venv` and activate it with `source venv/bin/activate`.
11. Install the requirements with `pip install -r requirements.txt` in the `Plex-RPC/remote` directory.
12. Run the app with `python remote.py`, ENSURE THAT DISCORD IS RUNNING FIRST.
13. Start listening to something on Plex and the status should be displayed on Discord.

---

## Windows

---

### Running on the same machine as Discord and PMS (e.g. a personal computer running PMS)

1. Clone the repository.
2. (Optional but recommended) Create a venv with `python -m venv venv` and activate it with `.\venv\Scripts\Activate`.
3. Install the requirements with `pip install -r requirements.txt` in the `Plex-RPC/main` directory.
4. Configure PMS to send Webhooks to `http://127.0.0.1:8080` as this is the default address the app listens on (or change it to your preference).
5. Configure the `config.json` file with your Discord Application ID and last.fm API key (if using the last.fm album covers).
6. Run the app with `python main.py`, ENSURE THAT DISCORD IS RUNNING FIRST.
7. Start listening to something on Plex and the status should be displayed on Discord.

---

### Running on a different machine (e.g. a Raspberry Pi for server hosting)
1. Clone the repository to the server machine.
2. (Optional but recommended) Create a venv with `python -m venv venv` and activate it with `.\venv\Scripts\Activate`.
3. Install the requirements with `pip install -r requirements.txt` in the `Plex-RPC/server` directory.
4. Configure PMS to send Webhooks to `http://127.0.0.1:8080` as this is the default address the app listens on (or change it to your preference).
5. Install nginx using the [Official NGINX install guide](http://nginx.org/en/docs/windows.html).
6. Configure the nginx configuration file to proxy the server to the internet (see the example in `Plex-RPC/server/winExample.conf`).
7. Start nginx with `start nginx` (Ensure that you are in the same directory as NGINX).
8. Run the app with `python server.py`.
9. On the machine running Discord, configure the `remoteConfig.json` file with the IP address of the server machine (STRONGLY RECOMMENDED: Use NGINX even on a local connection).
10. (Optional but recommended) Create a venv with `python -m venv venv` and activate it with `.\venv\Scripts\Activate`.
11. Install the requirements with `pip install -r requirements.txt` in the `Plex-RPC/remote` directory.
12. Run the app with `python remote.py`, ENSURE THAT DISCORD IS RUNNING FIRST.
13. Start listening to something on Plex and the status should be displayed on Discord.

---

## Mac

---

### Running on the same machine as Discord and PMS (e.g. a personal computer running PMS)

I don't have a Mac, but the Linux instructions should work for Mac as well.

If you have a Mac and would like to contribute to this section, please open a pull request.

### Running on a different machine as Discord (e.g. a server running PMS)

I don't have a Mac, but the Linux instructions should work for Mac as well.

If you have a Mac and would like to contribute to this section, please open a pull request.

---

## Configuration

The `config.json` file is used to configure the main app. The following are the keys in the file:
```json
{
  "serverIp": "127.0.0.1",
  "serverPort": 8080,
  "serverProtocol": "http",
  "discordClientId": "YOUR_DISCORD_CLIENT_ID",
  "lastFmEnabled": true,
  "lastFmApiKey": "YOUR_LASTFM_API_KEY (IF USING LAST.FM)"
}
```

The `remoteConfig.json` file is used to configure the remote app. The following are the keys in the file:
```json
{
    "serverIp": "YOUR_SERVER_IP_RUNNING_SERVER.PY",
    "serverPort": 443,
    "serverProtocol": "https",
    "discordClientId": "YOUR_DISCORD_CLIENT_ID",
    "lastFmEnabled": true,
    "lastFmApiKey": "YOUR_LASTFM_API_KEY (IF USING LAST.FM)"
}
```

The `serverConfig.json` file is used to configure the server app. The following are the keys in the file:
```json
{
    "serverIp": "12.0.0.1",
    "serverPort": 8080
}
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to test your changes before submitting a pull request.
