import os
import json
import random
import datetime
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceGroup, SourceRoom, SourceUser
)

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数から設定を取得
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# イーロン・マスク風の返答セット
ELON_RESPONSES = [
    "完全に合理的な判断だ。",
    "地球上で最も過小評価されているのは、面白いことを考え出す能力だ。",
    "私たちは宇宙文明になる必要がある。まだそこまで遠いがね。",
    "時間は投資に値する唯一の贅沢品だ。",
    "失敗は選択肢の一つだ。失敗しないなら、十分に革新的ではない。",
    "大きな意味のあることをするには、世界を良くすることに焦点を当てるべきだ。",
    "楽観主義者になろう。未来は良くなる。",
    "私は火星で死にたい。着陸時じゃなくてね。",
    "テスラジオ、最高だ！",
    "日本のテクノロジーは常に印象的だ。",
    "これは革命的なアイデアだ！",
    "君たちの考えは、私のNeuralink計画より野心的だね。",
    "これはDogeコインより価値があるかもしれない。"
]

# テスラ関連の事実
TESLA_FACTS = [
    "テスラのModel Sは、0から100km/hまで2.1秒で加速できる。",
    "テスラのギガファクトリーは、世界最大の建物の一つだ。",
    "テスラのオートパイロットは、人間のドライバーより安全性が高い。",
    "テスラのソーラールーフは、従来の屋根より耐久性がある。",
    "テスラのバッテリーは、家庭用電力貯蔵システムとしても使われている。",
    "テスラのCybertruck発表時、「割れない」と言われたガラスが割れた。",
    "テスラは自社の特許を公開し、電気自動車の普及を促進している。",
    "テスラの車には「犬モード」という機能があり、ペットを車内に安全に残せる。"
]

# SpaceX関連の事実
SPACEX_FACTS = [
    "SpaceXのFalcon Heavy は、現在運用されている中で最も強力なロケットだ。",
    "SpaceXのStarshipは、最終的に火星への旅を可能にする予定だ。",
    "SpaceXは、再利用可能ロケットの着陸に成功した最初の民間企業だ。",
    "SpaceXのStarlinkは、全世界にインターネットを提供する衛星ネットワークだ。",
    "SpaceXは、国際宇宙ステーションに最初に民間宇宙船をドッキングさせた。",
    "SpaceXの創設当初、最初の3回のロケット打ち上げは全て失敗した。",
    "SpaceXのDragon宇宙船は、ISS往復後に海に着水する。",
    "SpaceXは2002年に設立され、最初の成功したロケット打ち上げは2008年だった。"
]

# イーロン・マスクの名言
ELON_QUOTES = [
    "人生はもっと面白くなければならない。そうでなければ、誰もが自殺を考えるだろう。",
    "私はビジネスや利益のためにやっているわけではない。世界を変えたいんだ。",
    "あなたが何か素晴らしいものを作りたいなら、美しいだけでは不十分だ。それは素晴らしく使えなければならない。",
    "エンジニアリングとは、理論や推測ではなく、実際に機能するものを作ることだ。",
    "人は批判を恐れるべきではない。理にかなった批判を恐れるべきではない。",
    "私の動機は、人類の意識が継続することを確実にすることだ。",
    "ハードワークで何かを達成できないとしたら、それはおそらく不可能だ。",
    "私は決して諦めない。失敗は選択肢にない。",
    "最初の一歩は、何かが可能だと言うことだ。そうすれば、確率は高まる。"
]

# タスク実行の応答
def execute_task(task_type):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"タスク '{task_type}' を実行しました。\n実行時間: {current_time}\n\n火星からのメッセージ: 常に前進せよ！"

# 天気情報取得（例示用・実際のAPIキーは必要）
def get_weather(location="東京"):
    # 実際のプロダクションでは、適切な天気APIを使用
    weather_types = ["晴れ", "曇り", "雨", "雪", "嵐"]
    temp = random.randint(0, 35)
    weather = random.choice(weather_types)
    
    return f"{location}の天気:\n{weather}、気温{temp}℃\n\n火星の気温はマイナス60℃だぞ。地球は恵まれている。"

# ニュース取得（例示用）
def get_news():
    # 実際のプロダクションでは、適切なニュースAPIを使用
    fake_news = [
        "テスラ、新型電気飛行機の開発を発表",
        "SpaceX、火星への初の有人飛行を2026年に計画",
        "イーロン・マスク、AIの倫理に関する国際会議を主催",
        "テスラジオ、画期的な新機能でリスナー数が倍増",
        "Neuralink、初の人体実験が成功"
    ]
    
    return f"最新ニュース: {random.choice(fake_news)}\n\n情報は力だ。常に最新を保て。"

# ランダムなイーロン・マスクのアドバイス
def get_advice():
    advice = [
        "常に学び続けろ。知識は最強の武器だ。",
        "失敗を恐れるな。それは成功への道だ。",
        "時間は最も貴重な資源だ。賢く使え。",
        "批判は進歩のための燃料だ。",
        "大きく考えろ。宇宙の大きさほどに。",
        "行動は言葉より雄弁だ。",
        "困難は成長の機会だ。",
        "創造性を制限するな。",
        "好奇心を持ち続けろ。それが革新を生む。"
    ]
    
    return f"イーロンからのアドバイス: {random.choice(advice)}"

# メッセージソースの判定（個人、グループ、ルーム）
def is_group_or_room(source):
    return isinstance(source, (SourceGroup, SourceRoom))

def lambda_handler(event, context):
    """
    LINE Webhook用のLambdaハンドラ関数
    
    Parameters:
    event (dict): API Gatewayから渡されるイベントデータ
    context (LambdaContext): Lambda実行コンテキスト
    
    Returns:
    dict: API Gateway形式のレスポンス
    """
    
    # イベントをログに記録
    logger.info("イベント受信:")
    logger.info(json.dumps(event, indent=2))
    
    # リクエストボディを取得
    body = event.get('body', '{}')
    
    # X-Line-Signature ヘッダー値を取得
    signature = event.get('headers', {}).get('x-line-signature', '')
    if not signature:
        # 小文字のヘッダー名で試す（API Gateway経由だと小文字になる場合がある）
        signature = event.get('headers', {}).get('X-Line-Signature', '')
    
    logger.info(f"署名: {signature}")
    logger.info(f"ボディ: {body}")
    
    # Webhookの署名を検証
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("署名検証エラー")
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid signature'})
        }
    except Exception as e:
        logger.error(f"例外発生: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Exception: {str(e)}'})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'OK'})
    }

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
    テキストメッセージイベントのハンドラ
    
    Parameters:
    event (MessageEvent): LINEのメッセージイベント
    """
    text = event.message.text
    source = event.source
    logger.info(f"受信メッセージ: {text}")
    logger.info(f"ソースタイプ: {type(source).__name__}")
    
    # グループ/ルームチャットかどうかをチェック
    is_in_group = is_group_or_room(source)
    logger.info(f"グループチャット: {is_in_group}")
    
    # コマンド処理
    if text.startswith("/"):
        # グループチャットでもコマンドには常に反応
        process_command(event, text)
    elif not is_in_group:
        # 個人チャットの場合は通常どおり会話に反応
        process_conversation(event, text)
    else:
        # グループチャットでコマンド以外は反応しない
        logger.info("グループチャットでコマンドではないメッセージを無視します")

def process_command(event, text):
    """
    コマンドを処理する関数
    
    Parameters:
    event (MessageEvent): LINEのメッセージイベント
    text (str): メッセージテキスト
    """
    command = text[1:].split()[0]
    
    if command == "help":
        help_text = """イーロン・マスクbotコマンド:
/tesla - テスラに関する事実
/spacex - SpaceXに関する事実
/quote - イーロン・マスクの名言
/weather [場所] - 天気情報
/news - 最新ニュース
/advice - イーロンからのアドバイス
/task [タスク名] - タスクを実行
/random - ランダムな返答
        """
        try:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_text))
            logger.info("help応答を送信しました")
        except Exception as e:
            logger.error(f"help応答の送信中にエラー発生: {str(e)}")
        
    elif command == "tesla":
        try:
            response = random.choice(TESLA_FACTS)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
            logger.info(f"teslaコマンドの応答を送信: {response}")
        except Exception as e:
            logger.error(f"teslaコマンド応答の送信中にエラー発生: {str(e)}")
        
    elif command == "spacex":
        try:
            response = random.choice(SPACEX_FACTS)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
            logger.info(f"spacexコマンドの応答を送信: {response}")
        except Exception as e:
            logger.error(f"spacexコマンド応答の送信中にエラー発生: {str(e)}")
        
    elif command == "quote":
        try:
            response = random.choice(ELON_QUOTES)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
            logger.info(f"quoteコマンドの応答を送信: {response}")
        except Exception as e:
            logger.error(f"quoteコマンド応答の送信中にエラー発生: {str(e)}")
        
    elif command == "weather":
        # オプションで場所を指定可能
        parts = text.split()
        location = "東京"  # デフォルト
        if len(parts) > 1:
            location = parts[1]
        try:
            weather_info = get_weather(location)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=weather_info))
            logger.info(f"weather応答を送信: {weather_info[:30]}...")
        except Exception as e:
            logger.error(f"weather応答の送信中にエラー発生: {str(e)}")
        
    elif command == "news":
        try:
            news_info = get_news()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=news_info))
            logger.info(f"news応答を送信: {news_info[:30]}...")
        except Exception as e:
            logger.error(f"news応答の送信中にエラー発生: {str(e)}")
        
    elif command == "advice":
        try:
            advice = get_advice()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=advice))
            logger.info(f"advice応答を送信: {advice[:30]}...")
        except Exception as e:
            logger.error(f"advice応答の送信中にエラー発生: {str(e)}")
        
    elif command == "task":
        parts = text.split()
        task_type = "未指定のタスク"
        if len(parts) > 1:
            task_type = parts[1]
        try:
            task_result = execute_task(task_type)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=task_result))
            logger.info(f"task応答を送信: {task_result[:30]}...")
        except Exception as e:
            logger.error(f"task応答の送信中にエラー発生: {str(e)}")
    
    elif command == "random":
        try:
            response = random.choice(ELON_RESPONSES)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
            logger.info(f"randomコマンドの応答を送信: {response}")
        except Exception as e:
            logger.error(f"randomコマンド応答の送信中にエラー発生: {str(e)}")
        
    else:
        try:
            unknown_command = "未知のコマンドだ。/helpで使用可能なコマンドを確認してくれ。"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=unknown_command)
            )
            logger.info("未知のコマンド応答を送信しました")
        except Exception as e:
            logger.error(f"未知のコマンド応答の送信中にエラー発生: {str(e)}")

def process_conversation(event, text):
    """
    通常の会話を処理する関数
    
    Parameters:
    event (MessageEvent): LINEのメッセージイベント
    text (str): メッセージテキスト
    """
    try:
        text_lower = text.lower()
        
        if "テスラ" in text_lower or "tesla" in text_lower:
            response = f"テスラについて話しているのか？素晴らしい。{random.choice(TESLA_FACTS)}"
        elif "spacex" in text_lower or "スペースx" in text_lower:
            response = f"SpaceXは私の情熱だ。{random.choice(SPACEX_FACTS)}"
        elif "火星" in text_lower or "mars" in text_lower:
            response = "火星は人類の次の大きなフロンティアだ。我々は多惑星種になる必要がある。"
        elif "ai" in text_lower or "人工知能" in text_lower:
            response = "AIは人類最大のリスクであり、最大の可能性でもある。慎重に発展させなければならない。"
        elif "こんにちは" in text_lower or "hello" in text_lower or "hi" in text_lower:
            response = "やあ、テスラジオのメンバーたち。今日は何を革新する？"
        elif "ありがとう" in text_lower or "thank" in text_lower:
            response = "感謝は人間の最も美しい特性の一つだ。その気持ちを大切にしろ。"
        elif "おやすみ" in text_lower or "good night" in text_lower:
            response = "良い休息を。明日はさらに革新的なアイデアで世界を変えよう。"
        elif "joke" in text_lower or "冗談" in text_lower:
            jokes = [
                "なぜロケット科学者は良いパーティーゲストなのか？彼らは雰囲気を高めるからだ！",
                "私の車はどこにでも行ける。ただし、バッテリーの充電範囲内に限る。",
                "火星への移住計画？それは「地球外」の考え方だ。",
                "テスラのAIが私に言った。「あなたは私のヒーローです」と。充電してあげただけなのに。"
            ]
            response = random.choice(jokes)
        else:
            response = random.choice(ELON_RESPONSES)
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
        logger.info(f"会話応答を送信: {response[:30]}...")
    except Exception as e:
        logger.error(f"会話応答の送信中にエラー発生: {str(e)}")