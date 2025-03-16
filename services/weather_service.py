import random
from config import logger

class WeatherService:
    """天気情報を提供するサービス"""
    
    def get_weather(self, location="東京"):
        """
        天気情報を取得する
        
        Parameters:
        location (str): 場所名
        
        Returns:
        str: 天気情報
        """
        try:
            # 実際のプロダクションでは、適切な天気APIを使用
            weather_types = ["晴れ", "曇り", "雨", "雪", "嵐"]
            temp = random.randint(0, 35)
            weather = random.choice(weather_types)
            
            return f"{location}の天気:\n{weather}、気温{temp}℃\n\n火星の気温はマイナス60℃だぞ。地球は恵まれている。"
        except Exception as e:
            logger.error(f"天気情報取得中にエラー発生: {str(e)}")
            return "天気情報を取得できませんでした。火星からの通信障害かもしれない。"
