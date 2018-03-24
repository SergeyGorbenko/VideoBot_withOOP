import requests
import telebot
import pytube
import lxml.html
import os
import threading

from bot import constants


class Conversation:
    Bot = None
    count_of_video = 0

    def __init__(self, id):
        self.ID = id
        self.Flag_Generate = False
        self.Flag_Add = False
        self.Flag_Next = True
        self.Flag_Panel = False
        self.Flag_Admin = False
        self.Flag_Priority = False
        self.Flag_Delete = False
        self.Flag_Final_Removing = False
        self.start_id = 0
        self.html_code = ''
        self.deleted_video_id = ''
        self.number = 0

    def start(self, user, id):
        user_markup = telebot.types.ReplyKeyboardMarkup(True)
        user_markup.row('Add Video', 'Delete Video', 'stop')
        user_markup.row('Generate Video', 'Videos\' list')
        self.Bot.send_message(id, '>>>', reply_markup=user_markup)
        print(user, ': start')

    def generate_video(self, user, id):
        self.Bot.send_message(id, "Enter your request:")
        self.Flag_Generate = True
        print(user, ': generated video')

    def add_video(self, user, id):
        if self.count_of_video >= 20:
            self.Bot.send_message(id,
                                  "If you add new video this video will delete\n" +
                                  constants.youtube + self.overflow()[1])
        self.Bot.send_message(id, "Add link to your video:")
        self.Flag_Add = True
        print(user, ': add video')

    def stop(self, user, id):
        hide_markup = telebot.types.ReplyKeyboardRemove(True)
        self.Bot.send_message(id, '...', reply_markup=hide_markup)
        print(user, ': stop')

    def get_video(self, user, id, text):
        request = (str(text)).replace(' ', '+')
        url = 'https://www.youtube.com/results?search_query=' + request + '&sp=EgIYAQ%253D%253D'
        r = requests.get(url)

        self.html_code = str(r.text)
        self.start_id = self.get_id(self.html_code)
        video_id = self.html_code[self.start_id:self.start_id + 11]
        g_url = 'https://www.youtube.com/watch?v=' + video_id

        if video_id == 't-face{font':
            self.Bot.send_message(id, "Video not found")
        else:
            self.Bot.send_message(id, "Generated video ->")
            self.Bot.send_message(id, g_url)
        user_markup = telebot.types.ReplyKeyboardMarkup(True)
        user_markup.row('Next', 'Close')
        self.Bot.send_message(id, 'You may get next one', reply_markup=user_markup)
        self.Flag_Generate = False
        self.Flag_Panel = True
        print(user, ': get video')

    def download_video(self, user, id, text):
        if self.count_of_video >= 20:
            self.delete_overflow(self.overflow())

        flag = True
        with open(constants.videos_list, encoding='utf8') as fio:
            for i in fio:
                if i.strip().__contains__(text):
                    flag = False
                    break
            if flag:
                pass
            else:
                self.Bot.send_message(id, "You have already had that video")

        if flag:
            self.Bot.send_message(id, "Your video has searched")

            self.Flag_Add = False

            new_name = text[-11:]

            def download():
                self.Bot.send_message(id, "Downloading...")
                print(user, ': downloading...')
                pytube.YouTube(text).streams \
                    .filter(file_extension='mp4') \
                    .first() \
                    .download(constants.videos, new_name)
                print(user, ': ...downloaded')

            threading.Thread(target=download).start()

            with open(constants.videos_list, 'a', encoding='utf8') as f:
                f.write(self.get_name_video(text) + '\n' + str(text) + '\n')

            self.Bot.send_message(id, "This video has already been added to the list")

            with open(constants.priority_list, 'a', encoding='utf8') as fio:
                fio.write(new_name + ' ')

            user_markup = telebot.types.ReplyKeyboardMarkup(True)
            user_markup.row('⭐⭐⭐⭐⭐', '⭐⭐⭐⭐')
            user_markup.row('⭐⭐⭐', '⭐⭐', '⭐')
            self.Bot.send_message(id, "Set the priority of the video", reply_markup=user_markup)
            self.Bot.send_message(id, "⭐⭐⭐⭐⭐ - very important video (display immediately)\n"
                                      "⭐⭐⭐⭐ - important video (display next)\n"
                                      "⭐⭐⭐ - medium importance video (display today)\n"
                                      "⭐⭐ - usual video (display yesterday)\n"
                                      "⭐ - low importance video (display in this week)\n")
            self.Flag_Priority = True
            self.count_of_video += 1

    def other(self, user, id, text):
        if self.Flag_Panel:
            if (text == 'Next') and self.Flag_Next:
                self.start_id += self.get_id(self.html_code[self.start_id:-1])
                video_id = self.html_code[self.start_id:self.start_id + 11]
                if video_id == 'div class=\"':
                    self.Flag_Next = False
                    self.Bot.send_message(id, 'You have reached the limit video ')
                else:
                    g_url = constants.youtube + video_id
                    self.Bot.send_message(id, g_url)
                    print(user, ': next')

            elif text == 'Close':
                self.Flag_Panel = False
                self.Flag_Next = True
                self.start(user, id)
                print(user, ': close')
        if self.Flag_Add:
            self.Bot.send_message(id, 'There is no such video')

    def add_new_admin(self, user, id, user_id, first_name):
        print(user_id, first_name)
        if self.user_checker(user_id):
            self.Bot.send_message(id, "This user is already an admin ")
            print(first_name, ': user is already an admin')
        else:
            if user_id is None:
                self.Bot.send_message(id, "This user is not registered in Telegram")
                print(first_name, ': user is not registered in Telegram')
                self.Flag_Admin = False
                return
            with open(constants.admins, 'a', encoding='utf8') as fos:
                fos.write(str(user_id) + "\n")
            self.Bot.send_message(id, "The contact has been added to the administrator list")
            print(user, ': add new admin')
        self.Flag_Admin = False

    def list_video(self, user, id):
        list_of_video = ''
        j = int(2)
        k = 1
        with open(constants.videos_list, encoding='utf8') as f:
            for i in f:
                if int(j) % 2 == 0:
                    list_of_video += '/' + str(k) + ' ' + i.strip() + '\n'
                    k += 1
                j += 1
        self.Bot.send_message(id, list_of_video)
        print(user, ': show list video')

    def delete_video_choise(self, user, id):
        self.Bot.send_message(id, 'Choise video for removing:')
        self.list_video(user, id)
        self.Flag_Delete = True

    def delete_video(self, user, id, text):
        self.number = int(text[1:])
        with open(constants.videos_list, encoding='utf8') as f:
            text = f.readlines()
            self.deleted_video_id = text[self.number * 2 - 1]
            self.Bot.send_message(id, self.deleted_video_id)

        self.Flag_Final_Removing = True
        self.Flag_Delete = False
        user_markup = telebot.types.ReplyKeyboardMarkup(True)
        user_markup.row('Delete', 'Back')
        self.Bot.send_message(id, "Make a choice", reply_markup=user_markup)
        print(user, ': delete video')

    def final_removing(self, user, id, text):
        if str(text) == 'Delete':
            self.Bot.send_message(id, 'Removing')
            os.remove(constants.videos + str(self.deleted_video_id[-12:]).strip() + '.mp4')

            f = open(constants.videos_list, encoding='utf8').readlines()
            f.pop(self.number * 2 - 2)
            f.pop(self.number * 2 - 2)

            with open(constants.videos_list, 'w', encoding='utf8') as F:
                F.writelines(f)

            f = open(constants.priority_list, encoding='utf8').readlines()
            f.pop(self.number - 1)

            with open(constants.priority_list, 'w', encoding='utf8') as F:
                F.writelines(f)

            self.Bot.send_message(id, 'Done')
            print(user, ': remove >>>  ' + self.deleted_video_id.strip())
            self.start(user, id)
        elif str(text) == 'Back':
            print(user, ': back')
            self.start(user, id)
        self.Flag_Final_Removing = False

        self.count_of_video -= 1

    def set_prioritys(self, user, id, text):
        text = str(text).__len__()

        with open(constants.priority_list, 'a', encoding='utf8') as fio:
            fio.write(str(text) + '\n')
        self.start(user, id)
        self.Flag_Priority = False
        print(user, ': set priority')

    @staticmethod
    def delete_overflow(user, del_video):
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
        print(user, ': delete overflow')

    @staticmethod
    def overflow(user):
        with open(constants.priority_list, encoding='utf8') as fis:
            list_of_v = fis.readlines()

        del_video = [len(list_of_v) - 1,
                     list_of_v[len(list_of_v) - 1].split()[0],  # [numb, video_id, priority]
                     list_of_v[len(list_of_v) - 1].split()[1]]

        for i in range(len(list_of_v))[::-1]:
            if i == 0:
                break
            if int(del_video[2]) <= int(list_of_v[i - 1].split()[1]):
                del_video = [i - 1, list_of_v[i - 1].split()[0], list_of_v[i - 1].split()[1]]
        print(user, ': overflow')
        return del_video

    @staticmethod
    def get_id(html):
        video_id = html.find(
            "<li><div class=\"yt-lockup yt-lockup-tile yt-lockup-video vve-check clearfix\" data-context-item-id=")
        video_id += 99
        return video_id

    @staticmethod
    def get_name_video(url):
        r = requests.get(url)
        html_tree = lxml.html.fromstring(r.text)
        path = ".//title"
        name_video = html_tree.xpath(path)[0]
        return str(name_video.text_content()).replace(' - YouTube', '')

    @staticmethod
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
