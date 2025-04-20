from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, logger

class LineClient:
    """LINE APIとの対話を抽象化するクラス"""
    
    def __init__(self):
        """LINE APIクライアントを初期化する"""
        self.line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        self.handler = WebhookHandler(LINE_CHANNEL_SECRET)
        self._bot_user_id = None
    
    def verify_signature(self, body, signature):
        """
        署名を検証する
        
        Parameters:
        body (str): リクエストボディ
        signature (str): X-Line-Signature ヘッダー値
        
        Returns:
        bool: 署名が有効な場合はTrue、そうでない場合はFalse
        """
        try:
            self.handler.handle(body, signature)
            return True
        except InvalidSignatureError:
            logger.error("署名検証エラー")
            return False
        except Exception as e:
            logger.error(f"例外発生: {str(e)}")
            return False
    
    def reply_message(self, reply_token, text):
        """
        メッセージを返信する
        
        Parameters:
        reply_token (str): 返信トークン
        text (str): 送信するテキスト
        
        Returns:
        bool: 送信が成功した場合はTrue、そうでない場合はFalse
        """
        try:
            self.line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=text)
            )
            logger.info(f"メッセージを送信: {text[:30]}...")
            return True
        except Exception as e:
            logger.error(f"メッセージ送信中にエラー発生: {str(e)}")
            return False
    
    def get_handler(self):
        """
        WebhookHandlerを取得する
        
        Returns:
        WebhookHandler: LINE WebhookHandler
        """
        return self.handler

    def get_bot_user_id(self) -> str:
        """Bot 自身の userId を返す（キャッシュ付き）"""
        if self._bot_user_id is None:
            self._bot_user_id = self.line_bot_api.get_bot_info().user_id
        return self._bot_user_id
