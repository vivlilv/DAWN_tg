import aiohttp
import asyncio

async def get_puzzle():
    url = "https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle?appid=undefined"
    
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
        "priority": "u=1, i",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, ssl=False) as response:
            print(f"Status Code: {response.status}")
            print(f"Response: {await response.json()}")

# Run the asyncio event loop
asyncio.run(get_puzzle())
