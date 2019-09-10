import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import requests
from gtts import gTTS
import detectlanguage

def main():
    #авторизация
    VkApiKey = 'VK API KEY'
    session = requests.Session()
    vk_session = vk_api.VkApi(token=VkApiKey)
    detectlanguage.configuration.api_key = 'Language Detection API KEY' 
    vk = vk_session.get_api()
    upload = VkUpload(vk_session)
    longpoll = VkLongPoll(vk_session)
    print('Authorization success.\nBot is online.\n----------------------')

    available_langs = ['ar', 'cs', 'da', 'nl', 'en', 'fil', 'fi', 'fr', 'de', 'el', 'hi', 'hu', 'id', 'it', 'ja', 'ko', 'cmn', 'nb', 'pl', 'pt', 'ru', 'sk', 'es', 'sv', 'tr', 'uk', 'vi'] #список языков, доступных для озвучки гуглом
    lang = "ru"

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            try:
            	#пытаемся определить язык, если пользователь ввёл символы, отправляем сообщение об ошибке
                lang = detectlanguage.simple_detect(event.text)								
            except:
                print('id{}: "{}"'.format(event.user_id, event.text), 'Error!', end='\n\n')
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message='Ошибка, введите текст.'
                )
                continue
            #если язык для озвучки не доступен, ставим по дефолту русский и отправляем голосовое
            if lang not in available_langs : lang = "ru"
            print('id{}: "{}"'.format(event.user_id, event.text), lang, end='\n')
            tts = gTTS(event.text, lang)
            name = "audio.mp3"
            tts.save(name)
            api_url = 'https://api.vk.com/method/docs.getMessagesUploadServer'
            params = {
                'access_token': VkApiKey,
                'type': 'audio_message',
                'peer_id': event.user_id,
                'v': '5.95'
            }
            result = requests.get(api_url, params=params)
            data = result.json()
            afile = requests.post(data['response']['upload_url'], files={'file': open('audio.mp3', 'rb')}).json()['file']
            api_url = 'https://api.vk.com/method/docs.save'
            params = {
                'access_token': VkApiKey,
                'file': afile,
                'title': 'Voice message',
                'v': '5.95'
            }
            result = requests.get(api_url, params=params)
            doc = result.json()
            owner_id = str(doc['response']['audio_message']['owner_id'])
            id = str(doc['response']['audio_message']['id'])
            docattachment = 'doc'+owner_id+'_'+id
            print(docattachment)
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                attachment = docattachment
            )

            print('Done!\n')

if __name__ == '__main__':
    main()
