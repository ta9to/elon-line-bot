import json
from linebot.models import MessageEvent, TextMessage
from config import logger
from line_client import LineClient
from handlers.command_handler import CommandHandler
from handlers.conversation_handler import ConversationHandler

# LINEクライアントの初期化
line_client = LineClient()
command_handler = CommandHandler(line_client)
conversation_handler = ConversationHandler(line_client)

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
    if not line_client.verify_signature(body, signature):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid signature'})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'OK'})
    }

# メッセージイベントハンドラーの設定
@line_client.get_handler().add(MessageEvent, message=TextMessage)
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
    is_in_group = conversation_handler.is_group_or_room(source)
    logger.info(f"グループチャット: {is_in_group}")
    
    # コマンド処理
    if text.startswith("/"):
        # グループチャットでもコマンドには常に反応
        command_handler.process_command(event, text)
        return

    # メンション検知
    mention = getattr(event.message, "mention", None)
    logger.info(f"mention: {mention}")
    mentionees = getattr(mention, "mentionees", []) if mention else []
    logger.info(f"mentionees: {mentionees}")
    bot_user_id = line_client.get_bot_user_id()
    logger.info(f"bot_user_id: {bot_user_id}")
    is_mentioned = any(
        (getattr(m, "user_id", None) == bot_user_id)     # ① @bot
        or (getattr(m, "type", None) == "all")           # ② @all
        for m in mentionees
    )
    logger.info(f"メンション: {is_mentioned}")

    if is_mentioned:
        # メンションがあれば必ず会話処理
        conversation_handler.process_conversation(event, text)
        return

    if not is_in_group:
        # 個人チャットの場合は通常どおり会話に反応
        conversation_handler.process_conversation(event, text)
    else:
        # グループチャットでコマンド・メンション以外は反応しない
        logger.info("グループチャットでコマンドでもメンションでもないメッセージを無視します")
