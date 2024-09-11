import httpx
import asyncio
from datetime import datetime
from captcha import solve_captcha 



#Constants:
exp_token = '2056b72d0eb33beb2a6d2d39c67296afa677fc1f271efaf0d84b5d50cd08aee410c07f2f8a6510b58ab067551517964a9b712a207a15ea4f311b2b0364b0fd4be4b73a16b0be5708eaea1eeecc896238091f290f0f7a173e8a665a8cda3fe8625e6669adee14f08415335e123bac05218478fd5bfaf8810145bd97daf7c53b5039db2dd60cfd0de17ab9bd349623887c02a7789691d1c1fd02de15b2d9061b55c82233432f43b08ee746286fcc9515a18adfc9193e433d8c56c867a3e8a54ade18f11660f597e5fa46099ca5f2cc5f59356039379db30f6dc8af5c355ab82406c41fba212b6b3cc3eb36759c84491347'
active_token = '2056b72d0eb33beb2a6d2d39c67296afa677fc1f271efaf0d84b5d50cd08aee410c07f2f8a6510b58ab067551517964a9b712a207a15ea4f311b2b0364b0fd4bd653195afedd6e5a8efcceec848e8512ead4c3755e6f22d126ea8dcc52c97b39dce7d93ab26a35fa4a350642d5ac39472987dc0ea7aa0e673441517dede7dbddb91376e4e5a84222b90097066f274b0fa1748e07956a7ebbc2cf363c9d8561633043e968e48394238ce53b39e43c67db0256769eaf3a89b703b719672b5c98987ae93f8e69da8b425ffaa131fb890622d08eb77d54e7e6e9e33812671b32c067b03d5a62887f5a91ffaaf2b409eeed15'


# Create an async session
async def main():
        session = httpx.AsyncClient(http2=True, verify=False)
        session.headers.update({
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Linux\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        })


        # Function to get puzzle ID
        async def get_puzzle(session):
            url = "https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle"
            response = await session.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get('puzzle_id')


        # Function to get puzzle image in base64 format
        async def get_puzzle_base_64(session, puzzle_id):
            url = f"https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzle_id}"
            response = await session.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get('imgBase64')


        # Function to register user
        async def register_user(session,puzzle_id, puzzle_answer):
            url = "https://www.aeropres.in/chromeapi/dawn/v1/puzzle/validate-register"
            registration_data = {
                "ans": puzzle_answer,
                "country": "+91",
                "firstname": 'valaank',
                "lastname": 'valaank',
                "email": 'grottttp@gmail.com',
                "password": 'wakawaka',
                "puzzle_id": puzzle_id,
                "mobile": "",
                "referralCode": "i20g4c8r"
            }
            response = await session.post(url, json=registration_data)
            response.raise_for_status()
            print(f"Registration status: {response.status_code}")
            print(f"Response: {response.text}")
            print('******')


        # async def login(session,puzzle_id,solution):#v2 request in dev tools
            session.headers.update({
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/json",
                "origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
                "priority": "u=1, i",
                "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Linux\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
            })

            login_data = {
                "username": "genshzasho@gmail.com",
                "password": "Viva17k17",
                "logindata": {
                    "_v": "1.0.7",
                    "datetime": str(datetime.utcnow().isoformat(timespec='milliseconds') + 'Z')
                },
                "puzzle_id": puzzle_id,
                "ans": solution
            }

            response = await session.post(url="https://www.aeropres.in/chromeapi/dawn/v1/user/login/v2", json=login_data)
            print(response.json())
            response.raise_for_status()
        async def login(session, puzzle_id, solution):
            # Update headers (remove content-length, httpx manages this)
            session.headers.update({
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/json",
                "origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
                "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Linux\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
            })

            # Prepare the login data
            login_data = {
                "username": "genshzasho@gmail.com",
                "password": "Viva17k17",
                "logindata": {
                    "_v": "1.0.7",
                    "datetime": str(datetime.utcnow().isoformat(timespec='milliseconds') + 'Z')  # ISO timestamp
                },
                "puzzle_id": puzzle_id,  
                "ans": solution  
            }
            print(login_data)
            # Send POST request
            try:
                response = await session.post(
                    url="https://www.aeropres.in/chromeapi/dawn/v1/user/login/v2",
                    json=login_data
                )
                
                # Check the response
                print(response.json())  # Print the response for debugging
                response.raise_for_status()  # Raises exception for 4xx/5xx errors

            except httpx.HTTPStatusError as exc:
                print(f"Error response {exc.response.status_code} while requesting {exc.request.url}")
                print(exc.response.text)  # Print error message returned from the server

        async def get_user_referral_points(session,token):
            url = "https://www.aeropres.in/api/atom/v1/userreferral/getpoint"
            session.headers.update({
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "authorization": f"Berear {token}",
                "content-type": "application/json",
                "if-none-match": "W/\"336-jMb+AmW+rUVEfl0AseCEvUmbrVc\"",
                "origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
                "priority": "u=1, i",
                "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Linux\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
            })


            response = await session.get(url)
            print(response)
            print(response.json())
            return response.json()


        async def keep_alive(session,token,username='Vivlivko'):
            url = "https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive"
            session.headers.update({
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "authorization": f"Berear {token}",
                "content-type": "application/json",
                "origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
                "priority": "u=1, i",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
            })

            body = {
                "username": username,
                  "extensionid": "fpdkjdnhkakefebpekbdhillbhonfjjp",
                  "numberoftabs": 0,
                  "_v": "1.0.7",
            }

            response = await session.post(url,json=body)
            print(response)
            print(response.json())
            print(response.json()['data']['rewardPoint']['points'])


        async def logout():
            try:
                await get_user_referral_points(session,token=exp_token)
                await keep_alive(session,token=exp_token)
                print("logged out")
            except:
                print('error logging out (server error 502)...retrying after 15s')


        # Main flow
        print("alive")
        # await logout()
        # try:
        # puzzle_id = await get_puzzle(session=session)
        
        # img_base_64 = await get_puzzle_base_64(session=session,puzzle_id=puzzle_id)
        # solution = await solve_captcha(img_base64=img_base_64)
        # await register_user(session=session,puzzle_id=puzzle_id, puzzle_answer=solution)
    
        # except:
        #     print('err')
        while True:
            puzzle_id = await get_puzzle(session=session) 
            img_base_64 = await get_puzzle_base_64(session=session,puzzle_id=puzzle_id)
            solution = await solve_captcha(img_base64=img_base_64)
            await login(session=session,puzzle_id=puzzle_id,solution=solution) 






            # await get_user_referral_points(session,token=active_token)    
            # # await asyncio.sleep(120)
            # for i in range(5):
            #     try:
            #         response = await keep_alive(session,token=active_token)
            #         if response.status:
            #             print('keepalive done)')
            #             break
            #     except:
            #         print('request failed...')
            #         await asyncio.sleep(10)


        


if __name__=="__main__":
    asyncio.run(main())

