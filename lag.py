import asyncio
import json
import websockets
import time

# colours for terminal output
RED = "\033[91m"
LIME = "\033[92m"
RESET = "\033[0m"

def colored(text, color):
    return f"{color}{text}{RESET}"

# Websockets URLs, change your URL to match your setup
url1 = "ws://127.0.0.1:6006"
url2 = "wss://xrplcluster.com"

subscription_message = json.dumps({
    "command": "subscribe",
    "streams": ["ledger"]
})

# Store the ledger info with timestamps
ledger_info = {}

async def connect_to_websocket(url, identifier):
    async with websockets.connect(url) as websocket:
        await websocket.send(subscription_message)
        while True:
            response = await websocket.recv()
            data = json.loads(response)

            if data.get("type") == "ledgerClosed":
                ledger_index = data.get("ledger_index")
                current_time = time.time()

                if ledger_index in ledger_info:
                    other_time, other_identifier = ledger_info[ledger_index]
                    time_diff = current_time - other_time
                    first_responder = identifier if time_diff > 0 else other_identifier
                    time_diff = abs(time_diff)

                    color = LIME if first_responder == "Local Node" else RED
                    ledger_info_str = colored(f"Ledger {ledger_index}", color)
                    time_diff_str = colored(f"{time_diff:.2f} seconds", color)
                    first_responder_str = colored(first_responder, color)

                    print(f"{ledger_info_str} matched. Time difference: {time_diff_str}. First response from: {first_responder_str}")

                    del ledger_info[ledger_index]
                else:
                    ledger_info[ledger_index] = (current_time, identifier)

async def main():
    await asyncio.gather(
        connect_to_websocket(url1, "Local Node"),
        connect_to_websocket(url2, "XRPL Cluster")
    )

asyncio.run(main())
