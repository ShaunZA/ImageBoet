# coding=utf-8
import string
import urllib
import io
import main

import sys
from PIL import Image

CommandName = 'getgif'

retry_on_telegram_error = main.get_platform_command_code('web', 'retry_on_telegram_error')
get = main.get_platform_command_code('web', 'get')

def run(keyConfig, message, totalResults=1):
    args = {'cx': keyConfig.get('Google', 'GCSE_GIF_SE_ID1'),
            'key': keyConfig.get('Google', 'GCSE_APP_ID'),
            'searchType': 'image',
            'safe': "off",
            'q': str(message),
            'fileType': 'gif',
            'start': 1}
    return Send_Animated_Gifs(str(message), args, keyConfig, totalResults)


def is_valid_gif(imagelink):
    if not get.wasPreviouslySeenImage(imagelink):
        global gif, image_file, fd
        try:
            fd = urllib.urlopen(imagelink)
            image_file = io.BytesIO(fd.read())
            gif = Image.open(image_file)
        except:
            return False
        else:
            try:
                gif.seek(1)
            except EOFError:
                pass
            else:
                return int(sys.getsizeof(image_file)) < 10000000 and \
                       get.ImageHasUniqueHashDigest(image_file.getvalue())
        finally:
            try:
                if gif:
                    gif.fp.close()
                if image_file:
                    image_file.close()
                if fd:
                    fd.close()
            except UnboundLocalError:
                print("gif, image_file or fd local not defined")
            except NameError:
                print("gif, image_file or fd global not defined")

def Send_Animated_Gifs(requestText, args, keyConfig, totalResults=1):
    data, total_results, results_this_page = get.Google_Custom_Search(args)
    if 'items' in data and int(total_results) > 0:
        total_sent = search_results_walker(args, data, totalResults, requestText, results_this_page, total_results, keyConfig)
        if len(total_sent) < int(totalResults):
            if int(totalResults) > 1:
                bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find any more gifs for ' +
                                                      requestText + '. I could only find ' + 
                                str(len(total_sent)) + ' out of ' + str(totalResults))
            else:
                bot.sendMessage(chat_id=chat_id, text='I\'m sorry Dave, I\'m afraid I can\'t find a gif for ' +
                                                      requestText + '.')
        return total_sent
    else:
        errorMsg = 'I\'m sorry Dave, I\'m afraid I can\'t find a gif for ' + requestText + '.'
        bot.sendMessage(chat_id=chat_id, text=errorMsg)
        return [errorMsg]

def search_results_walker(args, data, number, requestText, results_this_page, total_results, keyConfig,
                          total_sent=[], total_offset=0):
    offset_this_page = 0
    while len(total_sent) < int(number) and int(offset_this_page) < int(results_this_page):
        imagelink = data['items'][offset_this_page]['link']
        print 'got image link ' + imagelink
        offset_this_page += 1
        total_offset += 1
        if '?' in imagelink:
            imagelink = imagelink[:imagelink.index('?')]
        if is_valid_gif(imagelink):
            if number == 1:
                total_sent.append(get.get_url_and_tags(imagelink, keyConfig, requestText))
            else:
                total_sent.append(requestText + ': ' + (str(len(total_sent) + 1) + ' of ' + str(number) + '\n' if int(number) > 1 else '') + imagelink)
    if len(total_sent) < int(number) and int(total_offset) < int(total_results):
        args['start'] = total_offset + 1
        data, total_results, results_this_page = get.Google_Custom_Search(args)
        return search_results_walker(args, data, number, requestText, results_this_page, total_results, keyConfig,
                                     total_sent, total_offset)
    return total_sent

