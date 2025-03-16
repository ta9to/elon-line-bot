import random
from config import logger
from data.responses import FAKE_NEWS

class NewsService:
    """ニュース情報を提供するサービス"""
    
    def get_news(self):
        """
        最新ニュースを取得する
        
        Returns:
        str: ニュース情報
        """
        try:
            # 実際のプロダクションでは、適切なニュースAPIを使用
            news = random.choice(FAKE_NEWS)
            
            return f"最新ニュース: {news}\n\n情報は力だ。常に最新を保て。"
        except Exception as e:
            logger.error(f"ニュース取得中にエラー発生: {str(e)}")
            return "ニュースを取得できませんでした。情報網に問題が発生しているようだ。"
