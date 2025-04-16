import requests as req
import schedule
from time import sleep
from datetime import datetime


def slash_send(self, token, guild_id, application_id, version_id, command_id, command, delay, channels, image):
    def sendMessage(token, channel_id, application_id, guild_id, version_id, command_id, command):
        try:
            headers = {'authorization': token, 'Content-Type': 'application/json'}
            payload = {
                "type": 2,
                "application_id": str(application_id),
                "guild_id": str(guild_id),
                "channel_id": str(channel_id),
                "session_id": '1',
                "data": {
                    "version": str(version_id),
                    "id": str(command_id),
                    "name": str(command),
                    "type": 1
                }
            }
            response = req.post("https://discord.com/api/v9/interactions", headers=headers, json=payload)

            if response.status_code == 400:
                payload["data"]["guild_id"] = str(guild_id)
                response = req.post("https://discord.com/api/v9/interactions", headers=headers, json=payload)

            current_datetime = datetime.now()
            self.logsbeep.emit(f"{current_datetime} | SLASH COMMAND sent to {channel_id}")

        except Exception as e:
            self.logsbeep.emit(f"Error: {str(e)}")

    if not self.running:
        return

    sendMessage(token, channel_id, application_id, guild_id, version_id, command_id, command)