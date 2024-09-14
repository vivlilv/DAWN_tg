from motor.motor_asyncio import AsyncIOMotorClient
import json
import logging
from typing import List, Dict, Tuple
import asyncio
from pprint import pprint
from bson import ObjectId

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ініціалізація асинхронного клієнта MongoDB
client = AsyncIOMotorClient('mongodb://localhost:27017/')
db = client['dawn_profiles']
collection = db['user_entries']

async def validate_data(data: Dict) -> bool:
    await client.drop_database('dawn_profiles')
    mail = data.get('mail', '')
    mail_pass = data.get('mail_pass', '')
    name = data.get('name', '')
    proxy = data.get('proxy', '')
    user_agent = data.get('user_agent', '')

    return all([
        '@' in mail,
        len(mail_pass) >= 8,
        name != '',
        proxy.startswith('http:'),
        len(user_agent) > 10
    ])

async def process_file(file_path: str, owner_id: str) -> str:
    try:
        with open(file_path, 'r') as file:
            data_list = json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logging.error(f'Помилка парсингу JSON: {e}')
        return 'Помилка парсингу JSON'
    
    valid_data = []
    invalid_entries = []

    for data in data_list:
        if await validate_data(data):
            data.update({
                'owner': owner_id,
                'account_state': 'active',
                'registered': False,
                'verified': False,
                'token': None,
                'points':0
            })
            logging.info(f"Валідний запис: {data}")
            valid_data.append(data)
        else:
            invalid_entries.append(data)

    if valid_data:
        if len(valid_data) > 1:
            await collection.insert_many(valid_data)
        else:
            await collection.insert_one(valid_data[0])

    if invalid_entries:
        invalid_file_path = f'accounts_data/invalid_entries_{owner_id}.json'
        with open(invalid_file_path, 'w') as invalid_file:
            json.dump(invalid_entries, invalid_file, indent=4)
        logging.info(f'Невалідні записи збережено у {invalid_file_path}')
        return invalid_file_path
    
    return 'Все аккаунты прошли проверку и начинают регистарцию!'

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

    return 0, str(counter), new_state

async def get_accounts_stats_by_owner_id(owner_id: str) -> dict:
    pipeline = [
        {"$match": {"owner": owner_id}},
        {"$group": {
            "_id": None,
            "total_points": {"$sum": "$points"},
            "account_count": {"$sum": 1}
        }}
    ]
    
    result = await collection.aggregate(pipeline).to_list(length=1)
    print(result)
    if result:
        return {
            "account_count": result[0]['account_count'],
            "total_points": result[0]['total_points']
        }
    else:
        return {
            "account_count": 0,
            "total_points": 0
        }

async def print_db_entries():
    # object_id = ObjectId('66e5a9af040dbb011ed8ea42')
    # result = await collection.delete_one({"_id": object_id})
    cursor = collection.find({})
    print("Записи в базі даних:")
    async for document in cursor:
        pprint(document)


# asyncio.run(print_db_entries())
# asyncio.run(validate_data(data={
#         "name": "Vivlivko",
#         "mail": "genshzasho@gmail.com",
#         "mail_pass": "viva17k17",
#         "referralCode": "",
#         "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
#         "proxy": "http://tbtvmzii:2qcqv4hp8yqm@23.129.254.246:6228"
#     }))