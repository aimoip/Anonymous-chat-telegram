import telebot
from telebot import types

from Messages import *
from dataEgine import *


access_token = 'TOKEN HERE'
bot = telebot.TeleBot(access_token)


def inline_menu():
    """
    Create inline menu for new chat
    :return: InlineKeyboardMarkup
    """
    callback = types.InlineKeyboardButton(text='\U00002709 New chat', callback_data='NewChat')
    menu = types.InlineKeyboardMarkup()
    menu.add(callback)

    return menu
    
    
def inline_menu_for_start():
    """
    Create inline menu for new chat
    :return: InlineKeyboardMarkup
    """
    callback_boy_button = types.InlineKeyboardButton(text='من پسرم', callback_data='1')
    callback_girl_button = types.InlineKeyboardButton(text='من دخترم', callback_data='0')
    menu = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    menu.add(callback_boy_button,callback_girl_button)

    return menu


def generate_markup():
    """
    Create menu with two buttons: 'Like' and 'Dislike'
    :return: ReplyKeyboardMarkup
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    markup.add(like_str)
    markup.add(dislike_str)
    return markup


def generate_markup_home():
    """
    Create menu with two buttons: 'Like' and 'Dislike'
    :return: ReplyKeyboardMarkup
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    markup.add('جستجوی جدید')
    return markup


def generate_markup_for_gender_finder():
    """
    Create menu with two buttons: 'Like' and 'Dislike'
    :return: ReplyKeyboardMarkup
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    markup.add("pesar mikham")
    markup.add("dokhtar mikham")
    markup.add("farghi nadare")
    return markup



def connect_user(user_id):
    """
    :param user_id: Chat id with user
    :return: boolean
    """
    if user_id in communications:
        return True
    else:
        bot.send_message(user_id, m_has_not_dialog)
        return False


@bot.message_handler(commands=['start'])
def echo(message):
    """
    Make the user in Data Base.
    :param message:
    :return:
    """
    message.chat.type = 'private'
    user_id = message.chat.id

    if message.chat.username is None:
        bot.send_message(user_id, m_is_not_user_name)
        return

    menu = inline_menu_for_start()

    bot.send_message(user_id, m_start, reply_markup=menu,)


@bot.message_handler(commands=['stop'])
def echo(message):
    """
    This function remove user from Data Base and sends a farewell message.
    :param message:
    :return:
    """
    menu = types.ReplyKeyboardRemove()
    user_id = message.chat.id

    if message.chat.id in communications:

        bot.send_message(communications[user_id]['UserTo'], m_disconnect_user, reply_markup=menu)

        tmp_id = communications[user_id]['UserTo']
        delete_info(tmp_id)

    delete_user_from_db(user_id)

    bot.send_message(user_id, m_good_bye)


@bot.message_handler(func=lambda call: call.text == like_str or call.text == dislike_str)
def echo(message):
    """
    This function reacts to pressing buttons: 'Like' and 'Dislike'
    If both users press 'Like', then bot sends them username from telegram.
    If somebody press 'Dislike', then chat finish.
    :param message:
    :return:
    """
    user_id = message.chat.id

    if user_id not in communications:
        bot.send_message(user_id, m_failed, reply_markup=types.ReplyKeyboardRemove())
        return

    user_to_id = communications[user_id]['UserTo']

    flag = False

    if message.text == dislike_str:
        bot.send_message(user_id, m_dislike_user, reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(user_to_id, m_dislike_user_to, reply_markup=types.ReplyKeyboardRemove())
        free_users[user_id]['state']=0
        free_users[user_to_id]['state']=0
        flag = True
    else:
        bot.send_message(user_id, m_like, reply_markup=types.ReplyKeyboardRemove())

        update_user_like(user_to_id)

        if communications[user_id]['like'] == communications[user_to_id]['like']:
            bot.send_message(user_id, m_all_like(communications[user_id]['UserName']))
            bot.send_message(user_to_id, m_all_like(communications[user_to_id]['UserName']))
            flag = True

    if flag:
        delete_info(user_to_id)
        menu = generate_markup_home()
        bot.send_message(user_id, m_play_again, reply_markup=menu)
        bot.send_message(user_to_id, m_play_again, reply_markup=menu)


@bot.message_handler(content_types=['text', 'sticker', 'video', 'photo', 'audio', 'voice'])
def echo(message):
    """
    Resend message to anonymous friend.
    :param message:
    :return:
    """
    user_id = message.chat.id
    if message.content_type == 'sticker':
        if not connect_user(user_id):
            return

        bot.send_sticker(communications[user_id]['UserTo'], message.sticker.file_id)
    elif message.content_type == 'photo':
        if not connect_user(user_id):
            return

        file_id = None

        for item in message.photo:
            file_id = item.file_id

        bot.send_photo(communications[user_id]['UserTo'], file_id, caption=message.caption)
    elif message.content_type == 'audio':
        if not connect_user(user_id):
            return

        bot.send_audio(communications[user_id]['UserTo'], message.audio.file_id, caption=message.caption)
    elif message.content_type == 'video':
        if not connect_user(user_id):
            return

        bot.send_video(communications[user_id]['UserTo'], message.video.file_id, caption=message.caption)
    elif message.content_type == 'voice':
        if not connect_user(user_id):
            return

        bot.send_voice(communications[user_id]['UserTo'], message.voice.file_id)
    elif message.content_type == 'text':
        if message.text=="جستجوی جدید":
            recovery_data()
            keyboard=generate_markup_for_gender_finder()
            bot.send_message(user_id, "دختر میخای یا پسر؟", reply_markup=keyboard)
            return
        if message.text=="من پسرم":
            add_users(chat=message.chat,g=True)
            keyboard=generate_markup_for_gender_finder()
            bot.send_message(user_id, "دختر میخای یا پسر؟", reply_markup=keyboard)
            return
        elif message.text=="من دخترم":
            add_users(chat=message.chat,g=False)
            keyboard=generate_markup_for_gender_finder()
            bot.send_message(user_id, "دختر میخای یا پسر؟", reply_markup=keyboard)
            return
        elif message.text=="pesar mikham":
            free_users[user_id]['state']=1
            user_to_id = None
            if len(free_users) < 2:
                keyboard=generate_markup_home()
                bot.send_message(user_id, m_is_not_free_users,reply_markup=keyboard)
                return

         #   if free_users[user_id]['state'] == 0:
          #      return
            if free_users[user_id]['gender']==True:
                for user in free_users:
                    if ((user['state'] == 1 or user['state'] == 3) and user['gender']==True and user['ID']!=user_id):
                        user_to_id = user['ID']
                        user['state']=0
                        free_users[user_id]['state']=0
                        break
                    
                    
            if free_users[user_id]['gender']==False:
                for user in free_users:
                    if ((user['state'] == 2 or user['state'] == 3) and user['gender']== True and user['ID']!=user_id):
                        user_to_id = user['ID']
                        user['state']=0
                        free_users[user_id]['state']=0
                        break

            if user_to_id is None:
                keyboard=generate_markup_home()
                bot.send_message(user_id, m_is_not_free_users,reply_markup=keyboard)
                return

            keyboard = generate_markup()

            add_communications(user_id, user_to_id)

            bot.send_message(user_id, m_is_connect, reply_markup=keyboard)
            bot.send_message(user_to_id, m_is_connect, reply_markup=keyboard)
            
        elif message.text=="dokhtar mikham":
            free_users[user_id]['state']=2
            user_to_id = None
            if len(free_users) < 2:
                keyboard=generate_markup_home()
                bot.send_message(user_id, m_is_not_free_users,reply_markup=keyboard)
                return

           # if free_users[user_id]['state'] == 0:
            #    return
            if free_users[user_id]['gender']==True:
                for user in free_users:
                    if ((user['state'] == 1 or user['state'] == 3) and user['gender']==False and user['ID']!=user_id) :
                        user['state']=0
                        free_users[user_id]['state']=0
                        user_to_id = user['ID']
                        break
            
            if free_users[user_id]['gender']==False:
                for user in free_users:
                    if ((user['state'] == 2 or user['state'] == 3) and user['gender']==False and user['ID']!=user_id) :
                        user['state']=0
                        free_users[user_id]['state']=0
                        user_to_id = user['ID']
                        break

            if user_to_id is None:
                keyboard=generate_markup_home()
                bot.send_message(user_id, m_is_not_free_users,reply_markup=keyboard)
                return

            keyboard = generate_markup()

            add_communications(user_id, user_to_id)

            bot.send_message(user_id, m_is_connect, reply_markup=keyboard)
            bot.send_message(user_to_id, m_is_connect, reply_markup=keyboard)
        elif message.text=="farghi nadare":
            free_users[user_id]['state']=3
            user_to_id = None
            if len(free_users) < 2:
                keyboard=generate_markup_home()
                bot.send_message(user_id, m_is_not_free_users,reply_markup=keyboard)
                return

           # if free_users[user_id]['state'] == 0:
            #    return
            if free_users[user_id]['gender']==False:
                for user in free_users:
                    if ((user['state'] == 2 or user['state'] == 3)  and user['ID']!=user_id):
                       user_to_id = user['ID']
                       user['state']=0
                       free_users[user_id]['state']=0
                       break
            if free_users[user_id]['gender']==True:
                for user in free_users:
                    if ((user['state'] == 1 or user['state'] == 3)  and user['ID']!=user_id):
                       user_to_id = user['ID']
                       user['state']=0
                       free_users[user_id]['state']=0
                       break

            if user_to_id is None:
                keyboard=generate_markup_home()
                bot.send_message(user_id, m_is_not_free_users,reply_markup=keyboard)
                return

            keyboard = generate_markup()

            add_communications(user_id, user_to_id)

            bot.send_message(user_id, m_is_connect, reply_markup=keyboard)
            bot.send_message(user_to_id, m_is_connect, reply_markup=keyboard)
            
        if message.text != '/start' and message.text != '/stop' and \
                    message.text != dislike_str and message.text != like_str and message.text != 'NewChat':

            if not connect_user(user_id):
                return

            if message.reply_to_message is None:
                bot.send_message(communications[user_id]['UserTo'], message.text)
            elif message.from_user.id != message.reply_to_message.from_user.id:
                bot.send_message(communications[user_id]['UserTo'], message.text,
                                 reply_to_message_id=message.reply_to_message.message_id - 1)
            else:
                bot.send_message(user_id, m_send_some_messages)

if __name__ == '__main__':
    recovery_data()
    bot.stop_polling()
    bot.polling(none_stop=True)
