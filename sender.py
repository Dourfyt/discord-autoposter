import requests as req
import schedule
from time import sleep
from datetime import datetime
from websocket import create_connection
import json
import random


def send(self, token, channel_id, message, delay, image):
    def sendMessage(token, channel_id, message, image):
        try:
            ws = create_connection("wss://gateway.discord.gg/")
            data = '''
            {
                "op": 2,
                "d":{
                    "token": "%s",
                    "properties": {
                        "$os": "linux",
                        "$browser": "ubuntu",
                        "$device": "ubuntu"
                    }
                }
            }
            ''' % token
            ws.send(data)

            headers = {'authorization': token}
            if image != '':
                try:
                    files = {'file': open(image, 'rb')}
                    data = {'content': message}
                    req.post(f"https://discord.com/api/v9/channels/{channel_id}/messages",
                             headers=headers, files=files, data=data)
                except Exception as e:
                    self.logsbeep.emit(f"Error sending image: {str(e)}")
            else:
                payload = {"content": message, "tts": False}
                req.post(f"https://discord.com/api/v9/channels/{channel_id}/messages",
                         headers=headers, json=payload)

            current_datetime = datetime.now()
            self.logsbeep.emit(f"{current_datetime} | MSG sent to {channel_id}")

        except Exception as e:
            self.logsbeep.emit(f"Error: {str(e)}")
        finally:
            try:
                ws.close()
            except:
                pass

    # Remove the schedule usage and just send directly
    if not self.running:
        return

    sendMessage(token, channel_id, message, image)