import random
from config import logger
from data.responses import ADVICE_LIST

class AdviceService:
    """アドバイスを提供するサービス"""
    
    def get_advice(self):
        """
        イーロン・マスクからのアドバイスを取得する
        
        Returns:
        str: アドバイス
        """
        try:
            advice = random.choice(ADVICE_LIST)
            return f"イーロンからのアドバイス: {advice}"
        except Exception as e:
            logger.error(f"アドバイス取得中にエラー発生: {str(e)}")
            return "アドバイスを提供できません。考え中だ。"
