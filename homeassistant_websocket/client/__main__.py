from .client import Client
from .new_client import NewClient
import asyncio

def main() -> None:
    # it is hardcoded for now
    #client_id = 1
    uri = "ws://homeassistant.local:3030/"
    client = NewClient(uri)
    client.run()


if __name__ == "__main__":
    main()