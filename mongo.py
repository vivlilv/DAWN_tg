from motor.motor_asyncio import AsyncIOMotorClient
import json
import logging
from typing import List, Dict, Tuple
import asyncio
from pprint import pprint
from bson import ObjectId
from faker import Faker
import random
from fake_useragent import UserAgent
from datetime import datetime
from config import SETTINGS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


client = AsyncIOMotorClient('mongodb://localhost:27017/')
db = client['dawn_profiles']
collection = db['user_entries']
users_api_keys = db['users_api_keys']

fake = Faker()

#main workflow
async def validate_data(data: Dict) -> bool:
    mail = data.get('mail', '')
    mail_pass = data.get('mail_pass', '')
    name = data.get('name', '')
    proxy = data.get('proxy', '')

    return all([
        '@' in mail,
        len(mail_pass) >= 8,
        name != '',
        proxy.startswith('http:') or proxy.startswith('https:')
    ])

def generate_random_user_agent():
    ua = UserAgent()
    return ua.chrome

async def process_txt_file(file_path: str, owner_id: str) -> str:
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except UnicodeDecodeError as e:
        logging.error(f'Error reading file: {e}')
        return 'Error reading file'
    
    valid_data = []
    invalid_entries = []

    for line in lines:
        parts = line.strip().split(' ')
        ref_code = '' if len(parts)<6 else parts[5]
        if len(parts) >= 4:
            data = {
                'name': parts[0],
                'mail': parts[1],
                'mail_pass': parts[2],
                'proxy': parts[3],
                'registered': True if parts[4]=='True' else False,
                'referralCode': ref_code,
                'user_agent': generate_random_user_agent()
            }
            if await validate_data(data):
                existing_account = await collection.find_one({'mail': data['mail']})
                if existing_account:
                    if not existing_account.get('registered', False):
                        # Update the existing account
                        update_result = await collection.update_one(
                            {'_id': existing_account['_id']},
                            {'$set': {
                                'name': data['name'],
                                'mail_pass': data['mail_pass'],
                                'proxy': data['proxy'],
                                'referralCode': data['referralCode'],
                                'user_agent': data['user_agent'],
                                'registration_attempts': 0,
                                'verification_attempts': 0,
                                'owner': existing_account['owner'],
                                'account_state': 'active',
                                'registered': data['registered'],
                                'verified': data['registered'],
                                'token': None,
                                'points': 0
                            }}
                        )
                        if update_result.modified_count > 0:
                            logging.info(f"Updated existing account: {data['mail']}")
                        else:
                            logging.warning(f"Failed to update existing account: {data['mail']}")
                    else:
                        logging.warning(f"Account {data['mail']} is already registered. Skipping update.")
                        invalid_entries.append(data)
                else:
                    # Insert new account
                    data.update({
                        'owner': owner_id,
                        'account_state': 'active',
                        'registered': data['registered'],
                        'verified': data['registered'],
                        'token': None,
                        'registration_attempts': 0,
                        'verification_attempts': 0,
                        'points': 0
                    })
                    logging.info(f"Valid entry: {data}")
                    valid_data.append(data)
            else:
                invalid_entries.append(data)
        else:
            logging.warning(f"Invalid line format: {line}")
            invalid_entries.append(line)

    if valid_data:
        if len(valid_data) > 1:
            await collection.insert_many(valid_data)
        else:
            await collection.insert_one(valid_data[0])

    if invalid_entries:
        invalid_file_path = f'invalid_entries_{owner_id}.txt'
        with open(invalid_file_path, 'w') as invalid_file:
            for entry in invalid_entries:
                if isinstance(entry, dict):
                    invalid_file.write(f"{entry['name']}:{entry['mail']}:{entry['mail_pass']}:{entry['proxy']}:{entry['referralCode']}\n")
                else:
                    invalid_file.write(f"{entry}\n")
        logging.info(f'Invalid entries saved to {invalid_file_path}')
        return invalid_file_path
    
    return 'All accounts have been validated and are ready for registration!'

async def toggle_account_state(owner_id: str) -> Tuple[int, str, str]:
    count = await collection.count_documents({'owner': owner_id})
    if count == 0:
        logging.warning(f"Не знайдено записів для owner_id: {owner_id}")
        return 1, 'err', ''

    cursor = collection.find({'owner': owner_id})
    counter = 0
    new_state = ''

    async for entry in cursor:
        current_state = entry.get('account_state')
        new_state = 'active' if current_state == 'sleep' else 'sleep'
        
        await collection.update_one(
            {'_id': entry['_id']},
            {'$set': {'account_state': new_state}}
        )

        counter += 1
        logging.info(f"Оновлено запис з ID {entry['_id']} до стану {new_state}")

    return 0, "active" if new_state == 'sleep' else "sleep", new_state

async def get_accounts_stats_by_owner_id(owner_id: str) -> Dict[str, int]:
    pipeline = [
        {"$match": {"owner": owner_id}},
        {"$group": {
            "_id": None,
            "accounts": {"$sum": 1},
            "fully_registered_and_verified": {
                "$sum": {
                    "$cond": [
                        {"$and": [
                            {"$eq": ["$registered", True]},
                            {"$eq": ["$verified", True]}
                        ]},
                        1,
                        0
                    ]
                }
            },
            "registration_failed": {
                "$sum": {
                    "$cond": [{"$eq": ["$registration_failed", True]}, 1, 0]
                }
            },
            "total_points": {"$sum": "$points"}
        }}
    ]

    result = await collection.aggregate(pipeline).to_list(length=1)
    print(result)
    if result:
        stats = result[0]
        stats.pop('_id', None)
        
        return stats
    else:
        return {
            "accounts": 0,
            "fully_registered_and_verified": 0,
            "registration_failed": 0,
            "total_points": 0
        }

async def print_db_entries():
    cursor = collection.find({})
    print("Записи в базі даних:")
    async for document in cursor:
        pprint(document)

async def retrieve_and_categorize_accounts(owner_id: str) -> str:
    cursor = collection.find({'owner': owner_id})
    
    registered_accounts = []
    not_registered_accounts = []
    failed_accounts = []

    accounts = []
    async for account in cursor:
        accounts.append(account)

    # Calculate the maximum width for each column
    max_name_len = max(len(account.get('name', '')) for account in accounts)
    max_mail_len = max(len(account.get('mail', '')) for account in accounts)
    max_mail_pass_len = max(len(account.get('mail_pass', '')) for account in accounts)
    max_proxy_len = max(len(account.get('proxy', '')) for account in accounts)
    max_referral_code_len = max(len(account.get('referralCode', '')) for account in accounts)
    max_points_len = max(len(str(account.get('points', ''))) for account in accounts)

    # Define the header
    header = (
        f"{'Name':<{max_name_len}} "
        f"{'Email':<{max_mail_len}} "
        f"{'Password':<{max_mail_pass_len}} "
        f"{'Proxy':<{max_proxy_len}} "
        f"{'Ref Code':<15}"
        f"{'Points':<{max_points_len+2}} "
        f"{'Reg attempts':<30} "
        f"{'Ver attempts':<15}"
    )

    for account in accounts:
        account_str = (
            f"{account.get('name', ''):<{max_name_len}} "
            f"{account.get('mail', ''):<{max_mail_len}} "
            f"{account.get('mail_pass', ''):<{max_mail_pass_len}} "
            f"{account.get('proxy', ''):<{max_proxy_len}} "
            f"{account.get('referralCode', ''):<15}"
            f"{account.get('points', ''):<{max_points_len}}"
        )
        
        registered = account.get('registered') in [True, 'True']
        verified = account.get('verified') in [True, 'True']
        registration_attempts = account.get('registration_attempts')
        verification_attempts = account.get('verification_attempts')
        
        logging.info(f"Processing account: {account.get('mail', '')} - Registered: {registered}, Verified: {verified}, Reg attempts: {registration_attempts}, Ver attempts: {verification_attempts}")

        account_info = f"{account_str} - Reg attempts: {registration_attempts:<15}  Ver attempts: {verification_attempts:<15}"
        print('REG ', registered, 'VER ', verified)
        if registered and verified:
            registered_accounts.append(account_info)
            logging.info(f"Account categorized as valid: {account.get('mail', '')}")
        elif not registered or not verified:
            if registration_attempts < SETTINGS['max_registration_attempts'] or verification_attempts < SETTINGS['max_verification_attempts']:
                not_registered_accounts.append(account_info)
                logging.info(f"Account categorized as not registered: {account.get('mail', '')}")
            else:
                error_msg = "Ошибка верификации почты" if registered else "Ошибка прохождения капчи"
                failed_accounts.append(f"{account_info} - {error_msg}")
                logging.info(f"Account categorized as failed: {account.get('mail', '')}")
        else:
            logging.warning(f"Account in unexpected state: {account.get('mail', '')}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"accounts_status_{owner_id}_{timestamp}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("REGISTERED:\n")
        f.write(header + "\n")
        f.write("\n".join(registered_accounts))
        f.write(f"\n\nNOT YET REGISTERED ({len(not_registered_accounts)}):\n")
        f.write(header + "\n")
        f.write("\n".join(not_registered_accounts))
        f.write(f"\n\nFAILED REGISTRATION ({len(failed_accounts)}):\n")
        f.write(header + "\n")
        f.write("\n".join(failed_accounts))

    logging.info(f"Generated file {filename} with {len(registered_accounts)} valid, {len(not_registered_accounts)} not registered, and {len(failed_accounts)} failed accounts")
    return filename

async def save_api_key(user_id: str, api_key: str) -> Dict:
    """
    Save or update the API key for a user in the users_keys collection.
    :param user_id: The ID of the user
    :param api_key: The API key to save
    :return: A dictionary containing the result of the operation
    """
    try:
        result = await users_api_keys.update_one(
            {'user_id': user_id},
            {'$set': {'api_key': api_key}},
            upsert=True
        )
        
        if result.matched_count > 0:
            return {"status": "updated", "message": "API ключ успешно обновлён"}
        else:
            return {"status": "inserted", "message": "API ключ успешно добавлен"}
    except Exception as e:
        logging.error(f"Error saving API key for user {user_id}: {str(e)}")
        return {"status": "error", "message": f"Ошибка при попытке добавить АРІ ключ, повторите позже"}







#used in tests/debugging
async def update_user_agents(owner_id: str = None) -> Tuple[int, int]:
    query = {'owner': owner_id} if owner_id else {}
    
    cursor = collection.find(query)
    updated_count = 0
    total_count = 0

    async for document in cursor:
        total_count += 1
        chrome_version = random.randint(90, 127)
        webkit_version = random.randint(537, 600)
        safari_version = random.randint(537, 600)

        new_user_agent = f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{webkit_version}.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/{safari_version}.36"
        
        result = await collection.update_one(
            {'_id': document['_id']},
            {'$set': {'user_agent': new_user_agent}}
        )
        
        if result.modified_count > 0:
            updated_count += 1
            logging.info(f"Updated user agent for document {document['_id']}: {new_user_agent}")
        else:
            logging.warning(f"Failed to update user agent for document {document['_id']}")

    logging.info(f"Updated {updated_count} out of {total_count} documents")
    return updated_count, total_count

async def delete_entries_with_null_token():
    try:
        result = await collection.delete_many({"token": None})
        deleted_count = result.deleted_count
        logging.info(f"Deleted {deleted_count} entries with null token")
        return deleted_count
    except Exception as e:
        logging.error(f"Error deleting entries with null token: {str(e)}")
        raise

async def update_registration_fields():
    # Update all documents
    result = await collection.update_many(
        {},  # This empty filter matches all documents
        {
            '$set': {
                'registration_attempts': 0,
                'verification_attempts': 0,
            },
            '$unset': {
                'registration_attempt': ""
            }
        }
    )
    logging.info(f"Updated registration fields for {result.modified_count} documents")
    return result.modified_count

async def mark_account_as_failed(account_id):
    await collection.update_one(
        {'_id': account_id},
        {'$set': {'registration_failed': True}}
    )


if __name__ == "__main__":
    # asyncio.run(update_registration_fields())
    asyncio.run(print_db_entries())
