from pymongo import MongoClient
import json

client = MongoClient('mongodb://localhost:27017/')
db = client['dawn_profiles']

collection = db['user_entries']

# collection.insert_one({
#         'name':'lrwvk',
#         'mail': 'vitafimcd@outlook.com',
#         'mail_pass':'dXcr1akln',
#         'referralCode':'',
#         'user_agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
#         'proxy':'https://tbtvmzii:tbtvmzii@23.129.254.246:6228',
#         'proxy_example':"http://username:password@proxy-server:port",

#     })





def validate_data(data):
    return all([data.get('mail')=="1", data.get('mail_pass')])



def process_file(file_path,owner_id):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            data_list = json.loads(file_content)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print('error parsing json')
        return 'Ошибка в файле, проверьте на тип .json и правильность полей'
    
    valid_data = []
    invalid_entries = []

    for data in data_list:
        if validate_data(data):
            data['owner']=owner_id
            data['account_state']='sleep'
            valid_data.append(data)
        else:
            invalid_entries.append(data)

    if valid_data:
        print(valid_data)
        collection.insert_many(valid_data)

    if invalid_entries:
        print('invalid entries')
        print(invalid_entries)
        return str(invalid_entries)


# invalid = process_file('accounts_data/6165872978.json',owner_id='6165872978')
# print(invalid)