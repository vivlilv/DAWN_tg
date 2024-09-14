import os
import asyncio
from telebot.async_telebot import AsyncTeleBot
from mongo import process_file, toggle_account_state, get_accounts_stats_by_owner_id

API_TOKEN = os.environ.get("API_TOKEN", "7214897743:AAGn99a-MjdSCIyafOR1jihp7t4L4H0b-yE")
bot = AsyncTeleBot(API_TOKEN)

@bot.message_handler(commands=['add_accounts'])
async def start_command(message):
    example_file_path = 'accounts_example.txt'

    await bot.reply_to(message, 'Привет, для начала нужно отправить файл с аккаунтами(тип .json).\nИспользуйте ", а не \'')

    with open(example_file_path, 'rb') as file:
        await bot.send_document(message.chat.id, file, caption='Пример файла')    

@bot.message_handler(content_types=['document'])
async def handle_document(message):
    user_id = message.from_user.id
    file_info = await bot.get_file(message.document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    
    save_path = f'accounts_data/{user_id}.json'
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    await bot.reply_to(message, 'Данные отправлены для проверки...\nНе отправляйте файл снова, пока не получите уведомление про регистрацию ваших аккаунтов')
    result = await process_file(file_path=save_path, owner_id=str(user_id))

    if result == 'Помилка парсингу JSON':
        await bot.reply_to(message, 'Ошибка, проверьте файл на тип .json и правильность полей')

    elif result == 'Все аккаунты прошли проверку и начинают регистарцию!':
        await bot.reply_to(message, result)

    else:
        if os.path.exists(result):
            with open(result, 'rb') as invalid_file:
                await bot.reply_to(message, 'Файл c аккаунтами, не прошедшими проверку (проверьте файл)')
                await bot.send_document(message.chat.id, invalid_file)
            os.remove(result)  # Очистка файлу після відправки
        else:
            await bot.reply_to(message, 'Ошибка, повторите команду немного позже...')

    os.remove(save_path)

@bot.message_handler(commands=['start_stop_farming'])
async def farm_command(message):
    user_id = message.from_user.id

    await bot.reply_to(message, 'Меняю состояние аккаунтов (работа/сон)')
    result = await toggle_account_state(owner_id=str(user_id))
    if result[0] == 1:
        await bot.reply_to(message, 'Не найдено аккаунтов, добавьте их с помощью /add_accounts.')
    else:
        await bot.reply_to(message, f'Успешно изменено состояние аккаунтов с {result[1]} на {result[2]}')


@bot.message_handler(commands=['stats'])
async def stats_command(message):
    user_id = message.from_user.id
    result = await get_accounts_stats_by_owner_id(owner_id=str(user_id))
    if result['account_count'] == 0:
        await bot.reply_to(message, 'Не найдено аккаунтов, добавьте их с помощью /add_accounts.')
    else:
        await bot.reply_to(message, f'У вас:\n{result["account_count"]} аккаунтов\n{result["total_points"]} поинтов в сумме')





async def main():
    await bot.polling(non_stop=True)

if __name__ == '__main__':
    asyncio.run(main())