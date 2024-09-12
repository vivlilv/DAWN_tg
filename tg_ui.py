import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from create_db import process_file

# Initialize bot
API_TOKEN = os.environ.get("API_TOKEN", "7214897743:AAGn99a-MjdSCIyafOR1jihp7t4L4H0b-yE")
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['add_accounts'])
def start_command(message):
    example_file_path = 'accounts_example.txt'

    bot.reply_to(message, 'Привет, для начала нужно прислать аккаунты в данном формате')

    with open(example_file_path, 'rb') as file:
        bot.send_document(message.chat.id, file, caption='Пример файла')    


@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    save_path = f'accounts_data/{user_id}.json'
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    

    
    bot.reply_to(message, 'Данные отправлены для проверки...\nНе отправляйте файл снова пока не получите сообщение о регистрации предыдущих аккаунтов')
    invalid = process_file(file_path='accounts_data/6165872978.json',owner_id=user_id)
    bot.reply_to(message, invalid)


def main():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    main()