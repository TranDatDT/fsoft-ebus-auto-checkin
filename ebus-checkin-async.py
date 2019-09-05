"""FPT Software eBus AutoCheckin By TranDatDT"""

import asyncio
import datetime
from copy import deepcopy
from base64 import b64encode
import requests_async as requests

# CONFIG
SERVER_LINK = ''        # Server
AUTH_LINK = ''          # Login url
CHECKIN_LINK = ''       # Checkin url
TRANSFER_LINK = ''      # Transfer Utop url

BUS_ID = 101    # Bus ID
BEACON_ID = 47  # BLE ID of the bus

LIST_USERS = [
    b'USERNAME:PASSWORD',
]

HEADERS = {
    'User-Agent': 'Swagger-Codegen/1.0.0/java',
    'Content-Type': 'application/json; charset=utf-8',
    'Accept-Encoding': 'gzip'
}

today_date = datetime.datetime.today().strftime("%Y-%m-%d")

date_check = f'{today_date}T00:00:00.000'
COIN = 5


async def ebus_checkin(user: bytes):
    auth_headers = deepcopy(HEADERS)
    transfer_headers = deepcopy(HEADERS)

    base64_auth = b64encode(user).decode("ascii")  # Basic token
    auth_headers['Authorization'] = 'Basic {}'.format(base64_auth)

    user_decode = user.decode()
    user_decode = user_decode[:user_decode.index(':')]

    print(f"{user_decode}: Logging in...")

    # Get token from server
    get_token = await requests.post(url="{}{}".format(SERVER_LINK, AUTH_LINK),
                                    headers=auth_headers)

    if get_token.status_code == 200:
        print(f"{user_decode}: Logged in!")

        # Extract token
        x_access_token = get_token.json()['token']

        # Headers for check in
        checkin_headers = deepcopy(HEADERS)
        checkin_headers['x-access-token'] = x_access_token

        # Data
        request_data = {
            "data": [
                {
                    "beacon_id": BEACON_ID,
                    "date_check": date_check,
                    "id_bus": BUS_ID
                }
            ]
        }

        print(f"{user_decode}: Checking...")
        # Check in
        checkin = await requests.post(url="{}{}".format(SERVER_LINK, CHECKIN_LINK),
                                      headers=checkin_headers,
                                      json=request_data)

        print(f"{user_decode}: {checkin.json()}")
        print(f"{user_decode}: Transferring...")
        transfer_payload = {
            'spending': COIN
        }

        transfer_headers['x-access-token'] = x_access_token

        transfer = await requests.get(url='{}{}'.format(SERVER_LINK, TRANSFER_LINK),
                                      headers=transfer_headers,
                                      params=transfer_payload)

        print(f"{user_decode}: {transfer.text}")
    else:
        print(f"{user_decode}: {get_token.text}")


async def main():
    tasks = []

    for user in LIST_USERS:
        tasks.append(ebus_checkin(user))

    await asyncio.gather(*tasks)


print(f"Date: {today_date}")
asyncio.run(main())
