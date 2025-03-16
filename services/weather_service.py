import os
import random
import requests
from config import logger

class WeatherService:
    """天気情報を提供するサービス"""
    
    def __init__(self):
        """WeatherServiceの初期化"""
        # Yahoo Weather APIのエンドポイント
        self.api_url = "https://map.yahooapis.jp/weather/V1/place"
        
        # Yahoo Geocoder APIのエンドポイント
        self.geocoder_api_url = "https://map.yahooapis.jp/geocode/V1/geoCoder"
        
        # Yahoo APIの認証情報
        self.app_id = os.environ.get('YAHOO_APP_ID')
        
        # 東京の緯度経度（デフォルト値）
        self.default_coordinates = "139.732293,35.663613"
        
        # 天気コードと日本語の天気の対応表
        self.weather_codes = {
            0: "竜巻",
            1: "熱帯暴風雨",
            2: "ハリケーン",
            3: "激しい雷雨",
            4: "雷雨",
            5: "雨と雪",
            6: "雨と霙",
            7: "雪と霙",
            8: "凍る霧雨",
            9: "霧雨",
            10: "凍る雨",
            11: "にわか雨",
            12: "にわか雨",
            13: "にわか雪",
            14: "小雪",
            15: "吹雪",
            16: "雪",
            17: "雹",
            18: "霙",
            19: "砂塵",
            20: "霧",
            21: "靄",
            22: "煙霧",
            23: "強風",
            24: "風",
            25: "寒冷",
            26: "曇り",
            27: "ほとんど曇り（夜）",
            28: "ほとんど曇り（昼）",
            29: "一部曇り（夜）",
            30: "一部曇り（昼）",
            31: "晴れ（夜）",
            32: "晴れ",
            33: "晴れ（夜）",
            34: "晴れ（昼）",
            35: "雨と雹",
            36: "暑い",
            37: "局地的な雷雨",
            38: "散在する雷雨",
            39: "散在する雷雨",
            40: "散在するにわか雨",
            41: "大雪",
            42: "散在するにわか雪",
            43: "大雪",
            44: "一部曇り",
            45: "雷雨",
            46: "にわか雪",
            47: "局地的な雷雨",
            3200: "不明"
        }
    
    def _get_coordinates_from_location(self, location):
        """
        場所名から緯度経度を取得する
        
        Parameters:
        location (str): 場所名
        
        Returns:
        str: 緯度経度（"経度,緯度"の形式）
        """
        if not self.app_id:
            logger.warning("Yahoo APP IDが設定されていません")
            return self.default_coordinates
            
        try:
            params = {
                'query': location,
                'appid': self.app_id,
                'output': 'json'
            }
            
            response = requests.get(
                self.geocoder_api_url,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'Feature' in data and len(data['Feature']) > 0:
                    # 最初の結果の座標を取得
                    coordinates = data['Feature'][0]['Geometry']['Coordinates']
                    logger.info(f"場所名 '{location}' の座標: {coordinates}")
                    return coordinates
                else:
                    logger.warning(f"場所名 '{location}' の座標が見つかりませんでした")
                    return self.default_coordinates
            else:
                logger.error(f"Yahoo Geocoder API エラー: {response.status_code} - {response.text}")
                return self.default_coordinates
                
        except Exception as e:
            logger.error(f"Yahoo Geocoder API リクエスト中にエラー発生: {str(e)}")
            return self.default_coordinates
    
    def _fetch_yahoo_weather(self, location):
        """
        Yahoo Weather APIから天気情報を取得する
        
        Parameters:
        location (str): 場所名
        
        Returns:
        dict: 天気情報のJSON
        """
        if not self.app_id:
            logger.warning("Yahoo APP IDが設定されていません")
            return None
            
        try:
            # 場所名から緯度経度を取得
            coordinates = self._get_coordinates_from_location(location)
            
            params = {
                'coordinates': coordinates,
                'appid': self.app_id,
                'output': 'json'
            }
            
            response = requests.get(
                self.api_url,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Yahoo Weather API エラー: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Yahoo Weather API リクエスト中にエラー発生: {str(e)}")
            return None
    
    def get_weather(self, location="東京"):
        """
        天気情報を取得する
        
        Parameters:
        location (str): 場所名
        
        Returns:
        str: 天気情報
        """
        try:
            # Yahoo Weather APIから天気情報を取得
            weather_data = self._fetch_yahoo_weather(location)
            
            if weather_data and 'Feature' in weather_data:
                # APIレスポンスから必要な情報を抽出
                feature = weather_data['Feature'][0]
                weather_list = feature['Property']['WeatherList']['Weather']
                weather_area_code = feature['Property']['WeatherAreaCode']
                
                # 現在の天気情報（最初のエントリ）
                current_weather = weather_list[0]
                rainfall = current_weather['Rainfall']
                
                # 天気の状態を判断
                if float(rainfall) == 0:
                    weather_state = "晴れ"
                elif float(rainfall) < 1:
                    weather_state = "小雨"
                elif float(rainfall) < 5:
                    weather_state = "雨"
                else:
                    weather_state = "大雨"
                
                # 予測情報があれば取得
                forecast_info = ""
                if len(weather_list) > 1:
                    forecast = weather_list[-1]
                    forecast_rainfall = forecast['Rainfall']
                    forecast_time = forecast['Date']
                    forecast_hour = forecast_time[8:10]
                    forecast_min = forecast_time[10:12]
                    forecast_info = f"\n{forecast_hour}時{forecast_min}分の予測: 降水量 {forecast_rainfall}mm/h"
                
                # 天気情報を整形
                weather_info = f"{location}の天気:\n{weather_state}、現在の降水量 {rainfall}mm/h{forecast_info}\n\n火星の気温はマイナス60℃だぞ。地球は恵まれている。"
                return weather_info
            else:
                # APIからデータを取得できない場合はランダムな天気情報を返す（フォールバック）
                logger.warning("Yahoo Weather APIからデータを取得できませんでした。ランダムな天気情報を返します。")
                weather_types = ["晴れ", "曇り", "雨", "雪", "嵐"]
                temp = random.randint(0, 35)
                weather = random.choice(weather_types)
                
                return f"{location}の天気:\n{weather}、気温{temp}℃\n\n火星の気温はマイナス60℃だぞ。地球は恵まれている。"
                
        except Exception as e:
            logger.error(f"天気情報取得中にエラー発生: {str(e)}")
            return "天気情報を取得できませんでした。火星からの通信障害かもしれない。"
