from pymongo import MongoClient
import json

client = MongoClient('mongodb://localhost:27017/')
db = client['dawn_profiles']
collection = db['user_entries']

# db.drop_collection('user_entries')
def validate_data(data):
    mail = data.get('mail', '')
    mail_pass = data.get('mail_pass', '')
    name = data.get('name', '')
    proxy = data.get('proxy', '')
    user_agent = data.get('user_agent', '')

    email_valid = '@' in mail
    password_valid = len(mail_pass) >= 8
    name_valid = name != ''
    proxy_valid = proxy.startswith('http:')
    user_agent_valid = len(user_agent) > 10

    return all([email_valid, password_valid, name_valid, proxy_valid, user_agent_valid])


def process_file(file_path,owner_id):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            data_list = json.loads(file_content)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print('error parsing json')
        return 1
    
    valid_data = []
    invalid_entries = []

    for data in data_list:
        if validate_data(data):
            data['owner']=owner_id
            data['account_state']='active'
            data['registered'] = True #by default all accounts are unregistered
            valid_data.append(data)
        else:
            invalid_entries.append(data)

    if valid_data:
        if len(valid_data)>1:
            collection.insert_many(valid_data)
        else:
            collection.insert_one(valid_data[0])


    if invalid_entries:
        # Save invalid entries to a new file in JSON format
        invalid_file_path = f'accounts_data/invalid_entries_{owner_id}.json'
        with open(invalid_file_path, 'w') as invalid_file:
            json.dump(invalid_entries, invalid_file, indent=4)

        print(f'Invalid entries saved to {invalid_file_path}')
        return invalid_file_path
    
    return 'Все аккаунты прошли проверку и начинают регистрацию!'


def toggle_account_state(owner_id):
    count = collection.count_documents({'owner': owner_id})
    if count == 0:
        print(f"No entries found for owner_id: {owner_id}")
        return [1, 'err']  # Return a list with an error indicator and message

    entries = collection.find({'owner': owner_id})

    counter = 0
    for entry in entries:
        current_state = entry.get('account_state')
        new_state = 'active' if current_state == 'sleep' else 'sleep'
        
        # Update the account_state in the database
        collection.update_one(
            {'_id': entry['_id']},
            {'$set': {'account_state': new_state}}
        )

        counter+=1
        print(f"Updated entry with ID {entry['_id']} to {new_state}")
    return [0,counter,new_state]