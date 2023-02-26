import os
import sys
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)
# channel_secret = ''
# channel_access_token = ''
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

@app.route("/", methods=['POST'])
def linebot_test():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text= True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    json_data = json.loads(body) # 轉成dict, 不然單純body是str
    
    reply_toen = json_data['events'][0]['replyToken']
    user_id = json_data['events'][0]['source']['userId']
    # 得到對談者的profile
    profile = line_api.get_profile(user_id)
    reply_text = f'你是{profile.display_name}!, 你好 有什麼可以幫助你的?'
    # 設定quick reply button and action
    quick_reply_action = QuickReply(items=[
        QuickReplyButton(action=URIAction(label='google', uri='https://www.google.com.tw/')),
        QuickReplyButton(action=LocationAction(label='locate'))
    ])
    line_api.reply_message(reply_toen,TextSendMessage(text=reply_text, quick_reply=quick_reply_action))

    return 'Ok'
    
if __name__ == "__main__":
    app.run()