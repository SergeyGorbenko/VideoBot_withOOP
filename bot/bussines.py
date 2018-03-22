import requests
import telebot
import pytube
import lxml.html
import os
import threading

from bot import constants

Bot = None
Flag_Generate = False
Flag_Add = False
Flag_Next = True
Flag_Panel = False
Flag_Admin = False
Flag_Priority = False
Flag_Delete = False
Flag_Final_Removing = False
start_id = 0
html_code = ''
count_of_video = 0
deleted_video_id = ''
number = 0


def start(id):
    global Bot
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row('Add Video', 'Delete Video', 'stop')
    user_markup.row('Generate Video', 'Videos\' list')
    Bot.send_message(id, '>>>', reply_markup=user_markup)
    print('start')


def generate_video(id):
    global Bot
    global Flag_Generate
    Bot.send_message(id, "Enter your request:")
    Flag_Generate = True
    print('generated video')


def add_video(id):
    global Bot
    global Flag_Add
    global count_of_video

    if count_of_video >= 20:
        Bot.send_message(id,
                         "If you add new video this video will delete\n" + constants.youtube + overflow()[1])
    Bot.send_message(id, "Add link to your video:")
    Flag_Add = True
    print('add video')


def stop(id):
    hide_markup = telebot.types.ReplyKeyboardRemove(True)
    Bot.send_message(id, '...', reply_markup=hide_markup)
    print('stop')


def get_video(id, text):
    global Bot
    global Flag_Generate
    global Flag_Panel
    global html_code
    global start_id
    request = (str(text)).replace(' ', '+')
    url = 'https://www.youtube.com/results?search_query=' + request + '&sp=EgIYAQ%253D%253D'
    r = requests.get(url)

    html_code = str(r.text)
    start_id = get_id(html_code)
    video_id = html_code[start_id:start_id + 11]
    g_url = 'https://www.youtube.com/watch?v=' + video_id

    if video_id == 't-face{font':
        Bot.send_message(id, "Video not found")
    else:
        Bot.send_message(id, "Generated video ->")
        Bot.send_message(id, g_url)
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row('Next', 'Close')
    Bot.send_message(id, 'You may get next one', reply_markup=user_markup)
    Flag_Generate = False
    Flag_Panel = True
    print('get video')


def delete_overflow(del_video):
    id_video = str(del_video[1])
    numb_video = int(del_video[0])
    os.remove(constants.videos + id_video + '.mp4')
    f = open(constants.priority_list, encoding='utf8').readlines()
    f2 = open(constants.videos_list, encoding='utf8').readlines()
    f.pop(numb_video)
    f2.pop(numb_video * 2)
    f2.pop((numb_video * 2))
    with open(constants.priority_list, 'w', encoding='utf8') as F:
        F.writelines(f)
    with open(constants.videos_list, 'w', encoding='utf8') as F:
        F.writelines(f2)


def download_video(id, text):
    global Flag_Add
    global Flag_Priority
    global count_of_video

    if count_of_video >= 20:
        delete_overflow(overflow())

    flag = True
    with open(constants.videos_list, encoding='utf8') as fio:
        for i in fio:
            if i.strip().__contains__(text):
                flag = False
        if flag:
            pass
        else:
            Bot.send_message(id, "You have already had that video")

    if flag:
        Bot.send_message(id, "Your video has searched\nDownloading...")

        Flag_Add = False

        new_name = text[-11:]

        def download():
            print('downloading...')
            pytube.YouTube(text).streams \
                .filter(file_extension='mp4') \
                .first() \
                .download(constants.videos, new_name)
            print('...downloaded')

        threading.Thread(target=download).start()

        with open(constants.videos_list, 'a', encoding='utf8') as f:
            f.write(get_name_video(text) + '\n' + str(text) + '\n')

        Bot.send_message(id, "This video has already been added to the list")

        with open(constants.priority_list, 'a', encoding='utf8') as fio:
            fio.write(new_name + ' ')

        user_markup = telebot.types.ReplyKeyboardMarkup(True)
        user_markup.row('⭐⭐⭐⭐⭐', '⭐⭐⭐⭐')
        user_markup.row('⭐⭐⭐', '⭐⭐', '⭐')
        Bot.send_message(id, "Set the priority of the video", reply_markup=user_markup)
        Bot.send_message(id, "⭐⭐⭐⭐⭐ - very important video (display immediately)\n"
                             "⭐⭐⭐⭐ - important video (display next)\n"
                             "⭐⭐⭐ - medium importance video (display today)\n"
                             "⭐⭐ - usual video (display yesterday)\n"
                             "⭐ - low importance video (display in this week)\n")
        Flag_Priority = True
        count_of_video += 1


def overflow():
    with open(constants.priority_list, encoding='utf8') as fis:
        list_of_v = fis.readlines()
    del_video = [len(list_of_v) - 1, list_of_v[len(list_of_v) - 1].split()[0],  # [numb, video_id, priority]
                 list_of_v[len(list_of_v) - 1].split()[1]]
    for i in range(len(list_of_v))[::-1]:
        if i == 0:
            break
        if int(del_video[2]) <= int(list_of_v[i - 1].split()[1]):
            del_video = [i - 1, list_of_v[i - 1].split()[0], list_of_v[i - 1].split()[1]]
    print(del_video)
    return del_video


def other(id, text):
    global Bot
    global Flag_Panel
    global Flag_Next
    global html_code
    global start_id
    if Flag_Panel:
        if (text == 'Next') and Flag_Next:
            start_id += get_id(html_code[start_id:-1])
            video_id = html_code[start_id:start_id + 11]
            if video_id == 'div class=\"':
                Flag_Next = False
                Bot.send_message(id, 'You have reached the limit video ')
            else:
                g_url = constants.youtube + video_id
                Bot.send_message(id, g_url)
            print('next')

        elif text == 'Close':
            Flag_Panel = False
            Flag_Next = True
            start(id)
            print('close')
    if Flag_Add:
        print("There is no such video")
        Bot.send_message(id, 'There is no such video')


def get_id(html):
    video_id = html.find(
        "<li><div class=\"yt-lockup yt-lockup-tile yt-lockup-video vve-check clearfix\" data-context-item-id=")
    video_id += 99
    return video_id


def get_name_video(url):
    r = requests.get(url)
    html_tree = lxml.html.fromstring(r.text)
    path = ".//title"
    name_video = html_tree.xpath(path)[0]
    return str(name_video.text_content()).replace(' - YouTube', '')


def user_checker(user_id):
    rez = False
    if user_id == constants.gorbenko or user_id == constants.rumsha:
        rez = True
    else:
        with open(constants.admins, encoding='utf8') as fio:
            for line in fio:
                user_id = str(user_id)
                if user_id == line.strip():
                    rez = True
    return rez


def add_new_admin(id, user_id, first_name):
    global Flag_Admin
    print(user_id, first_name)
    if user_checker(user_id):
        Bot.send_message(id, "This user is already an admin ")
    else:
        if user_id is None:
            Bot.send_message(id, "This user is not registered in Telegram")
            return
        with open(constants.admins, 'a', encoding='utf8') as fos:
            fos.write(str(user_id) + "\n")
        Bot.send_message(id, "The contact has been added to the administrator list")
    Flag_Admin = False


def list_video(id):
    list_of_video = ''
    j = int(2)
    k = 1
    with open(constants.videos_list, encoding='utf8') as f:
        for i in f:
            if int(j) % 2 == 0:
                list_of_video += '/' + str(k) + ' ' + i.strip() + '\n'
                k += 1
            j += 1
    Bot.send_message(id, list_of_video)


def delete_video_choise(id):
    Bot.send_message(id, 'Choise video for removing:')
    list_video(id)
    global Flag_Delete
    Flag_Delete = True


def delete_video(id, text):
    global deleted_video_id
    global number
    number = int(text[1:])
    with open(constants.videos_list, encoding='utf8') as f:
        text = f.readlines()
        deleted_video_id = text[number * 2 - 1]
        Bot.send_message(id, deleted_video_id)

    global Flag_Final_Removing
    Flag_Final_Removing = True
    global Flag_Delete
    Flag_Delete = False
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row('Delete', 'Leave')
    Bot.send_message(id, "Make a choice", reply_markup=user_markup)


def final_removing(id, text):
    global deleted_video_id
    global count_of_video
    global number
    if str(text) == 'Delete':
        Bot.send_message(id, 'Removing')
        os.remove(constants.videos + str(deleted_video_id[-12:]).strip() + '.mp4')

        f = open(constants.videos_list, encoding='utf8').readlines()
        f.pop(number * 2 - 2)
        f.pop(number * 2 - 2)

        with open(constants.videos_list, 'w', encoding='utf8') as F:
            F.writelines(f)

        f = open(constants.priority_list, encoding='utf8').readlines()
        f.pop(number - 1)

        with open(constants.priority_list, 'w', encoding='utf8') as F:
            F.writelines(f)

        Bot.send_message(id, 'Done')
        start(id)
    elif str(text) == 'Leave':
        start(id)
    global Flag_Final_Removing
    Flag_Final_Removing = False

    count_of_video -= 1


def set_prioritys(id, text):
    global Flag_Priority
    text = str(text).__len__()

    with open(constants.priority_list, 'a', encoding='utf8') as fio:
        fio.write(str(text) + '\n')
    start(id)
    Flag_Priority = False
