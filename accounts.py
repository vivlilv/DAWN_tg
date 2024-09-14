import random
import asyncio
import httpx
import logging
from datetime import datetime
from typing import List, Dict, Optional
from captcha import solve_captcha 
from mail import get_verification_link
from mongo import client
from config import SETTINGS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AccountsManager:
    def __init__(self):
        self.client = client
        self.db = self.client[SETTINGS['DB_NAME']]
        self.collection = self.db[SETTINGS['COLLECTION_NAME']]
        self.active_accounts: Dict[str, Account] = {}
        self.add_new_accounts: Dict[str, Account] = {}

    async def fetch_accounts(self, query: Dict) -> List[Dict]:
        return await self.collection.find(query).to_list(length=None)

    async def fetch_active_registered_verified_accounts(self) -> List[Dict]:
        return await self.fetch_accounts({'account_state': 'active', 'registered': True, 'verified': True})

    async def fetch_unregistered_or_unverified_accounts(self) -> List[Dict]:
        return await self.fetch_accounts({'$or': [{'registered': False}, {'verified': False}]})

    async def run_active_registered_accounts(self):
        print(self.add_new_accounts)
        for account_id, account_instance in self.add_new_accounts.items():
            if account_id not in self.active_accounts:
                self.active_accounts[account_id] = account_instance
                logging.info(f"Starting task for account {account_id}")
                asyncio.create_task(self.active_accounts[account_id].start_task())
        self.add_new_accounts.clear()

    async def check_db_for_changes(self):
        current_active_accounts = await self.fetch_active_registered_verified_accounts()
        unregistered_or_unverified = await self.fetch_unregistered_or_unverified_accounts()
        
        current_ids = {acc['_id'] for acc in current_active_accounts}
        current_ids.update({acc['_id'] for acc in unregistered_or_unverified})

        new_accounts = [acc for acc in current_active_accounts if acc['_id'] not in self.active_accounts]
        new_accounts.extend([acc for acc in unregistered_or_unverified if acc['_id'] not in self.active_accounts])
        
        for acc in new_accounts:
            self.add_new_accounts[acc['_id']] = Account(account_details=acc, collection=self.collection)

        for account_id in list(self.active_accounts):
            if account_id not in current_ids:
                await self.active_accounts[account_id].stop_task()
                del self.active_accounts[account_id]
            else:
                updated_acc = next(acc for acc in current_active_accounts if acc['_id'] == account_id)
                self.active_accounts[account_id].points = updated_acc.get('points', 0)

    async def run(self):
        logging.info("Starting AccountsManager.run()")
        while True:
            try:
                logging.info("Checking DB for changes")
                await self.check_db_for_changes()
                logging.info("Running active registered accounts")
                await self.run_active_registered_accounts()
            except Exception as e:
                logging.error(f"Error in main loop: {e}", exc_info=True)
            logging.info(f"Sleeping for {SETTINGS['CHECK_INTERVAL']} seconds")
            await asyncio.sleep(SETTINGS['CHECK_INTERVAL'])

class Account:
    def __init__(self, account_details: Dict, collection):
        self.account_details = account_details
        self.session = httpx.AsyncClient(http2=True, verify=False)
        self.task: Optional[asyncio.Task] = None
        self.collection = collection
        self.should_stop = False
        self.points = self.account_details.get('points', 0)

    async def set_session(self):
        self.session.headers.update(SETTINGS['DEFAULT_HEADERS'])
        self.session.headers.update({"user-agent": self.account_details['user_agent']})

    async def get_puzzle(self) -> str:
        url = f"{SETTINGS['BASE_URL']}/puzzle/get-puzzle"
        response = await self.session.get(url)
        response.raise_for_status()
        return response.json()['puzzle_id']

    async def get_puzzle_base_64(self, puzzle_id: str) -> str:
        url = f"{SETTINGS['BASE_URL']}/puzzle/get-puzzle-image?puzzle_id={puzzle_id}"
        response = await self.session.get(url)
        response.raise_for_status()
        return response.json()['imgBase64']

    async def register_user(self, puzzle_id: str, solution: str) -> int:
        url = f"{SETTINGS['BASE_URL']}/puzzle/validate-register"
        registration_data = {
            "ans": solution,
            "country": "+91",
            "firstname": self.account_details['name'],
            "lastname": self.account_details['name'],
            "email": self.account_details['mail'],
            "password": self.account_details['mail_pass'],
            "puzzle_id": puzzle_id,
            "mobile": "",
            "referralCode": ""
        }
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
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
        response = await self.session.post(url, json=registration_data, headers=headers)
        print(response.json())
        return response.status_code

    async def verify_mail(self) -> Optional[str]:
        for _ in range(5):
            try:
                link = get_verification_link(username=self.account_details['mail'], password=self.account_details['mail_pass'])
                if link.startswith('https'):
                    self.session.headers.update(SETTINGS['VERIFICATION_HEADERS'])
                    await self.session.get(link)
                    return link
            except Exception as e:
                logging.error(f"Error while getting email: {e}")
            await asyncio.sleep(10)
        return None

    async def login(self, puzzle_id: str, solution: str) -> Optional[str]:
        url = f"{SETTINGS['BASE_URL']}/user/login/v2"
        login_data = {
            "username": self.account_details['mail'],
            "password": self.account_details['mail_pass'],
            "logindata": {
                "_v": SETTINGS['VERSION'],
                "datetime": datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
            },
            "puzzle_id": puzzle_id,
            "ans": solution
        }
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
        }
        response = await self.session.post(url, json=login_data, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['message'] == 'Successfully logged in!':
            return data['data']['token']
        return None

    async def get_user_referral_points(self, token: str) -> Dict:
        url = SETTINGS['GET_POINT_URL']
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
            "if-none-match": 'W/"337-NtHbWrVXbnADn2xC9gA7fTkFhMo"',
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
        response = await self.session.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        new_points = data['data']['rewardPoint']['points']
        
        if new_points != self.points:
            self.points = new_points
            await self.update_points_in_db(new_points)
        
        logging.info(f"Current points: {self.points}")
        return data

    async def update_points_in_db(self, new_points: int):
        await self.collection.update_one(
            {'_id': self.account_details['_id']},
            {'$set': {'points': new_points}}
        )
        logging.info(f"Updated points in database for {self.account_details['name']}: {new_points}")

    async def keep_alive(self, token: str) -> int:
        url = f"{SETTINGS['BASE_URL']}/userreward/keepalive"
        headers = {
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
            "origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
            "priority": "u=1, i",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        }
        body = {
            "username": self.account_details['name'],
            "extensionid": SETTINGS['EXTENSION_ID'],
            "numberoftabs": 0,
            "_v": SETTINGS['VERSION'],
        }
        response = await self.session.post(url, json=body, headers=headers)
        return response.status_code

    async def full_registration(self) -> int:
        logging.info(f"Starting registration for {self.account_details['name']}")

        sl=random.randint(1,60)
        print(f'sleeping for {sl}')
        await asyncio.sleep(sl)
        await self.set_session()
        try:
            for _ in range(10):
                if not self.account_details.get('registered'):
                    puzzle_id = await self.get_puzzle()
                    img_base_64 = await self.get_puzzle_base_64(puzzle_id)
                    solution = await solve_captcha(img_base_64)
                    await asyncio.sleep(25)
                    response = await self.register_user(puzzle_id, solution)
                    if response == 200:
                        await self.update_registration_status(True)
                        logging.info(f"Account {self.account_details['name']} successfully registered")
                        break
            for _ in range(10):
                if not self.account_details.get('verified'):
                    if await self.verify_mail():
                        await self.update_verification_status(True)
                        logging.info(f"Account {self.account_details['name']} successfully verified")
                        return 200
        except Exception as e:
            logging.error(f"Error during registration: {e}")
            await asyncio.sleep(10)
        return 400

    async def update_registration_status(self, status: bool):
        await self.collection.update_one(
            {'_id': self.account_details['_id']},
            {'$set': {'registered': status}}
        )
        self.account_details['registered'] = status

    async def update_verification_status(self, status: bool):
        await self.collection.update_one(
            {'_id': self.account_details['_id']},
            {'$set': {'verified': status}}
        )
        self.account_details['verified'] = status

    async def farm(self):
        logging.info(f"Starting farming for {self.account_details['name']}")
        await self.set_session()
        print('token---\n',self.account_details.get('token'),'\n---token')
        if not self.account_details.get('registered') or not self.account_details.get('verified'):
            await self.full_registration()
        if not self.account_details.get('token'):
            await self.login_with_retry()
        
        while not self.should_stop and self.account_details['account_state'] == 'active':
            try:
                await asyncio.gather(
                    self.get_user_referral_points(self.account_details['token']),
                    self.keep_alive_with_retry(self.account_details['token'])
                )
            except Exception as e:
                logging.error(f"Error during farming: {e}")
            await asyncio.sleep(110)

    async def login_with_retry(self, max_retries: int = 10):
        for attempt in range(max_retries):
            try:
                puzzle_id = await self.get_puzzle()
                img_base_64 = await self.get_puzzle_base_64(puzzle_id)
                solution = await solve_captcha(img_base_64)
                await asyncio.sleep(25)
                token = await self.login(puzzle_id=puzzle_id, solution=solution)
                if token:
                    await self.update_token_in_db(token)
                    return
            except Exception as e:
                logging.error(f"Login error (attempt {attempt + 1}): {e}")
            await asyncio.sleep(10)
        logging.error(f"Failed to login after {max_retries} attempts")

    async def keep_alive_with_retry(self, token: str, max_retries: int = 5):
        for attempt in range(max_retries):
            try:
                status = await self.keep_alive(token)
                if status == 200:
                    return
            except Exception as e:
                logging.error(f"Keep_alive error (attempt {attempt + 1}): {e}")
            await asyncio.sleep(10)
        logging.error("Failed to perform keep_alive after all attempts")

    async def update_token_in_db(self, token: str):
        await self.collection.update_one(
            {'_id': self.account_details['_id']},
            {'$set': {'token': token}}
        )

    async def start_task(self):
        if self.task is None:
            self.should_stop = False
            if not self.account_details.get('registered') or not self.account_details.get('verified'):
                logging.info(f"Starting registration/verification for account {self.account_details['name']}")
                await self.full_registration()
            self.task = asyncio.create_task(self.farm())

    async def stop_task(self):
        if self.task is not None:
            self.should_stop = True
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None


manager = AccountsManager()
asyncio.run(manager.run())