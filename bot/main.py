import re
import requests
import telebot
import time

from bot import bussines
from bot import constants

bot = bussines.Conversation.Bot = telebot.TeleBot(constants.token)

conversations = {}


@bot.message_handler(commands=['start'])
def handle_start(message):
    if bussines.Conversation.user_checker(message.from_user.id):
        new_con = bussines.Conversation(message.from_user.id)
        if not (message.from_user.id in conversations):
            conversations[message.from_user.id] = new_con

        user = str(message.from_user.first_name + ' ')
        if not (message.from_user.last_name is None):
            user += message.from_user.last_name
        conversations[message.from_user.id].start(user=user, id=message.from_user.id)
    else:
        bot.send_message(message.from_user.id, 'You do not have permissions')


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.from_user.id in conversations:

        user = str(message.from_user.first_name + ' ')
        if not (message.from_user.last_name is None):
            user += message.from_user.last_name

        if message.text == "stop":
            conversations[message.from_user.id].stop(user=user, id=message.from_user.id)

        elif message.text == "Add Video":
            conversations[message.from_user.id].add_video(user=user, id=message.from_user.id)

        elif message.text == "Generate Video":
            conversations[message.from_user.id].generate_video(user=user, id=message.from_user.id)

        elif message.text == "Videos\' list":
            conversations[message.from_user.id].list_video(user=user, id=message.from_user.id)

        elif message.text == "Delete Video":
            conversations[message.from_user.id].delete_video_choise(user=user, id=message.from_user.id)

        elif (str(message.text).__contains__('https://www.youtube.com')) and \
                conversations[message.from_user.id].Flag_Add:
            conversations[message.from_user.id].download_video(user=user, id=message.from_user.id, text=message.text)

        elif conversations[message.from_user.id].Flag_Generate:
            conversations[message.from_user.id].get_video(user=user, id=message.from_user.id, text=message.text)

        elif message.text == "/add_new_admin":
            bot.send_message(message.from_user.id, 'Send contact of new user')
            conversations[message.from_user.id].Flag_Admin = True
            print(user, "add new admin")

        elif conversations[message.from_user.id].Flag_Delete and (
                (re.match(r'^/([0-9]){0,2}', str(message.text)))):
            conversations[message.from_user.id].delete_video(user=user, id=message.from_user.id, text=message.text)

        elif conversations[message.from_user.id].Flag_Priority and re.match(r'⭐{0,5}', message.text):
            conversations[message.from_user.id].set_prioritys(user=user, id=message.from_user.id, text=message.text)

        elif conversations[message.from_user.id].Flag_Final_Removing:
            conversations[message.from_user.id].final_removing(user=user, id=message.from_user.id, text=message.text)

        else:
            conversations[message.from_user.id].other(user=user, id=message.from_user.id, text=message.text)


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if message.from_user.id in conversations:
        user = str(message.from_user.first_name + ' ')
        if conversations[message.from_user.id].Flag_Admin:
            conversations[message.from_user.id].add_new_admin(user=user,
                                                              id=message.from_user.id,
                                                              user_id=message.contact.user_id,
                                                              first_name=message.contact.first_name)


def polling():
    try:
        time.sleep(5)
        bot.polling(none_stop=True)
    except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
        polling()


if __name__ == "__main__":
    polling()
