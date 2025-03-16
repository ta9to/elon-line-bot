import random
from config import logger
from linebot.models import SourceGroup, SourceRoom, SourceUser
from data.responses import ELON_RESPONSES, TESLA_FACTS, SPACEX_FACTS, JOKES

class ConversationHandler:
    """会話を処理するハンドラー"""
    
    def __init__(self, line_client):
        """
        会話ハンドラーを初期化する
        
        Parameters:
        line_client (LineClient): LINE APIクライアント
        """
        self.line_client = line_client
    
    def is_group_or_room(self, source):
        """
        メッセージソースがグループまたはルームかどうかを判定する
        
        Parameters:
        source: メッセージソース
        
        Returns:
        bool: グループまたはルームの場合はTrue、そうでない場合はFalse
        """
        return isinstance(source, (SourceGroup, SourceRoom))
    
    def process_conversation(self, event, text):
        """
        通常の会話を処理する
        
        Parameters:
        event (MessageEvent): LINEのメッセージイベント
        text (str): メッセージテキスト
        
        Returns:
        bool: 処理が成功した場合はTrue、そうでない場合はFalse
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
                response = random.choice(JOKES)
            else:
                response = random.choice(ELON_RESPONSES)
            
            self.line_client.reply_message(event.reply_token, response)
            logger.info(f"会話応答を送信: {response[:30]}...")
            return True
        except Exception as e:
            logger.error(f"会話応答の送信中にエラー発生: {str(e)}")
            return False
