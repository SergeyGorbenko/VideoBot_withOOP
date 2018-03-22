import re
import requests
import telebot
import time

from bot import bussines
from bot import constants

bussines.Bot = telebot.TeleBot(constants.token)


@bussines.Bot.message_handler(commands=['start'])
def handle_start(message):
    if bussines.user_checker(message.from_user.id):
        bussines.start(message.from_user.id)
    else:
        bussines.Bot.send_message(message.from_user.id, 'You do not have permissions')


@bussines.Bot.message_handler(content_types=['text'])
def handle_text(message):
    if bussines.user_checker(message.from_user.id):
        if message.text == "stop":
            bussines.stop(message.from_user.id)

        elif message.text == "Add Video":
            bussines.add_video(message.from_user.id)

        elif message.text == "Generate Video":
            bussines.generate_video(message.from_user.id)

        elif message.text == "Videos\' list":
            bussines.list_video(message.from_user.id)

        elif message.text == "Delete Video":
            bussines.delete_video_choise(message.from_user.id)

        elif (str(message.text).__contains__('https://www.youtube.com')) and bussines.Flag_Add:
            bussines.download_video(message.from_user.id, message.text)

        elif bussines.Flag_Generate:
            bussines.get_video(message.from_user.id, message.text)

        elif message.text == "/add_new_admin":
            bussines.Bot.send_message(message.from_user.id, 'Send contact of new user')
            bussines.Flag_Admin = True
            print("add new admin")

        elif bussines.Flag_Delete and (
                (re.match(r'^/([0-9]){0,2}', str(message.text)))):
            bussines.delete_video(message.from_user.id, message.text)

        elif bussines.Flag_Priority and re.match(r'⭐{0,5}', message.text):
            bussines.set_prioritys(message.from_user.id, message.text)

        elif bussines.Flag_Final_Removing:
            bussines.final_removing(message.from_user.id, message.text)

        else:
            bussines.other(message.from_user.id, message.text)
    else:
        bussines.Bot.send_message(message.from_user.id, 'You do not have permissions')


@bussines.Bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if bussines.Flag_Admin:
        bussines.add_new_admin(message.from_user.id, message.contact.user_id, message.contact.first_name)


def polling():
    try:
        time.sleep(5)
        bussines.Bot.polling(none_stop=True)
    except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
        polling()


if __name__ == "__main__":
    polling()

