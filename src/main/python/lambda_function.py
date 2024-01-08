import os
import json
import hmac
import base64
import hashlib
import requests
import traceback
import linebot
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from linebot.exceptions import LineBotApiError

def concat_str(*args):
    result = ''.join(args)
    return result

def getLeaderBoards():
    actId = os.environ.get('ACT_ID')
    amount = os.environ.get('PLAYER_AMOUNT')
    startIndex = '0'
    leaderBoardsUrl = os.environ.get('RIOT_LEADER_BOARDS_URL')
    url = concat_str(leaderBoardsUrl, actId, "?size=", amount, "&startIndex=", startIndex)
    print("URL:", url)

    headerTokenName = 'X-Riot-Token'
    riotToken = os.environ.get('RIOT_TOKEN')

    response = requests.get(url, headers={headerTokenName : riotToken})
    return response

def lambda_handler(event, context):
  # 環境変数からLINE Botのチャネルアクセストークンを取得
  line_bot_api = linebot.LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
  try:
    channel_secret = '...' # Channel secret string
    body = '...' # Request body string
    hash = hmac.new(channel_secret.encode('utf-8'),
    body.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(hash)

    leaderBoards = getLeaderBoards()
    jsonData = leaderBoards.json()

    userId = os.environ.get('LINE_USER_TOKEN')

    line_bot_api.push_message(userId, TextSendMessage("本日のリーダーボードは以下です。"))
    rangeSize = int(os.environ.get('PLAYER_AMOUNT'))

    for num in range(rangeSize):
        line_bot_api.push_message(userId, TextSendMessage(
          text="Rank:" + json.dumps(jsonData["players"][num]["leaderboardRank"]) + "\nRankedRating:" + json.dumps(jsonData["players"][num]["rankedRating"]) + "\nName:" + json.dumps(jsonData["players"][num]["gameName"])
    ))

    # # リプライ用トークン
    # replyToken = event['events'][0]['replyToken']
    # # 受信メッセージ
    # messageText = event['events'][0]['message']['text']
    # # メッセージを返信（受信メッセージをそのまま返す）
    # line_bot_api.reply_message(replyToken, TextSendMessage(text=messageText))

    # # LINEからメッセージを受信
    # if event['events'][0]['type'] == 'message':
    #   print("passed events")
    #   print("message:"+event['events'][0]['message']['text'])
    #   # メッセージタイプがテキストの場合
    #   if event['events'][0]['message']['type'] == 'text':
    #     print("passed text")
    #     print("message:"+event['events'][0]['message']['type'])
    #     # リプライ用トークン
    #     replyToken = event['events'][0]['replyToken']
    #     # 受信メッセージ
    #     messageText = event['events'][0]['message']['text']
    #     # メッセージを返信（受信メッセージをそのまま返す）
    #     line_bot_api.reply_message(replyToken, TextSendMessage(text=messageText))
  except LineBotApiError as le:
    print(traceback.format_exc())
    return {'isBase64Encoded': False, 'statusCode': 500, 'headers': {}, 'body': json.dumps('LineBotApiError Exception occurred. ' + le)}
  except Exception as e:
    print(traceback.format_exc())
    return {'isBase64Encoded': False, 'statusCode': 500, 'headers': {}, 'body': json.dumps('Exception occurred. ' + e)}

  return {
    'isBase64Encoded': False,
    'statusCode': 200,
    'body': json.dumps('from Lambda')
  }
