import os
import time

import requests
from loguru import logger
from dotenv import load_dotenv

from pypresence import Presence


load_dotenv()  # for loading .env files

# find project dir
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)

# create log directory and file
os.makedirs("logs", exist_ok=True)
log_sink_name = os.path.join('logs', "{time}")  # just for win/linux path handling

# create log sink
logger.remove(0)
logger.add(sink=log_sink_name, rotation="24h", retention=3)  # log into file, rotate them daily, and keep last 3 files.


@logger.catch
def main():
    URL = "http://localhost:8080/jsonrpc"  # Your KODI HTTP access URL. This should be the default value
    payload = {
        "jsonrpc": "2.0",
        "method": "Player.GetItem",
        "params": {
            "properties": ["title", "thumbnail", "season", "episode", "showtitle"],
            "playerid": 1
        },
        "id": "VideoGetItem"
    }

    try:
        client_id = os.getenv('DISCORD_BOT_ID')
        RPC = Presence(client_id, pipe=0)
        RPC.connect()
    except Exception as e:
        logger.error(e)
        logger.error('Could not connect to discord')

    # Get details for now-playing. For now this is only for TV series.
    while True:
        try:
            response = requests.post(URL, json=payload)
            response_json = response.json()

            details = response_json.get('result', {}).get('item', {})
            logger.debug(details)

            state_str = details.get('title') or 'Not watching anything'
            details_str = details.get('showtitle') or 'Menu'
            ep_info = [details.get('episode', 1), details.get('season', 1)]

            logger.info(RPC.update(state=state_str, details=details_str, party_size=ep_info))
        except ConnectionRefusedError:
            logger.error("KODI is not running. No need to update status")
            time.sleep(300)
        except Exception as e:
            logger.error(e)

        time.sleep(15)


if __name__ == '__main__':
    main()