from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

 
from .scraper import Discogs

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

# 控制兩個不同問題
flag = {}
# 存入字典
main_dic = {}

line_bot_api.broadcast(TextSendMessage(text='☘️ The Best Album ☘️\n\n 你好 ~\n 我可以幫你找尋最合適的專輯\n 請先輸入歌手名稱......'))

@csrf_exempt

def callback(request):
    global flag
    global main_dic
    
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        
        for event in events:
            
            userid = event.source.user_id
            flag.setdefault(userid, True)
            if isinstance(event, MessageEvent) and flag[userid]:  # 如果有訊息事件
                try:
                    line_bot_api.push_message(userid,TextSendMessage(text='✨資料爬取中請稍候......'))
                    album = Discogs(event.message.text)
                    albums_dic = album.get_albums_dic() # 取得輸入歌手後 回傳一個song_dic
                    songs_list = album.get_song_list(albums_dic)

                    # 回復傳入的訊息文字
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text= songs_list)
                    )

                    line_bot_api.push_message(userid,TextSendMessage(text=" ✨ 接著請輸入你想要的歌曲"))
                    line_bot_api.push_message(userid,TextSendMessage(text=" ❗️ 輸入歌曲之間要用空格隔開喔"))
                    
                    # update flag and main_dic for the user
                    flag[userid] = False  
                    main_dic[userid] = albums_dic
                    
                except:
                    line_bot_api.push_message(userid,TextSendMessage(text=" ❗️錯誤❗️\n 請輸入正確的歌手名稱......"))
                
                
            elif isinstance(event, MessageEvent) and not flag[userid]: # 如果有訊息事件
                album = Discogs(event.message.text)
                value = main_dic[userid]
                best_albums = album.get_the_best_albums(value)

                # 回復傳入的訊息文字
                line_bot_api.reply_message(  
                    event.reply_token,
                    TextSendMessage(text= best_albums)
                )   
                line_bot_api.push_message(userid,TextSendMessage(text='謝謝你的使用🤗'))
                line_bot_api.push_message(userid,TextSendMessage(text="☘️ The Best Album ☘️\n\n 你好 ~\n 我可以幫你找尋最合適的專輯\n 請先輸入歌手名稱......"))
                
                flag[userid] = True

        return HttpResponse()

    
    else:
        return HttpResponseBadRequest()