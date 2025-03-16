import unittest
from unittest.mock import patch, MagicMock
import os
import json
import sys
import random

# Add the parent directory to the Python path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.weather_service import WeatherService

class TestWeatherService(unittest.TestCase):
    """WeatherServiceのテストクラス"""
    
    def setUp(self):
        """各テスト実行前の準備"""
        # 環境変数のバックアップ
        self.original_app_id = os.environ.get('YAHOO_APP_ID')
        
        # テスト用のYahoo APP IDを設定
        os.environ['YAHOO_APP_ID'] = 'test_app_id'
        
        # WeatherServiceのインスタンスを作成
        self.weather_service = WeatherService()
        
        # randomのseedを固定して、テストの再現性を確保
        random.seed(42)
    
    def tearDown(self):
        """各テスト実行後のクリーンアップ"""
        # 環境変数を元に戻す
        if self.original_app_id:
            os.environ['YAHOO_APP_ID'] = self.original_app_id
        else:
            if 'YAHOO_APP_ID' in os.environ:
                del os.environ['YAHOO_APP_ID']
        
        # randomのseedをリセット
        random.seed()
    
    def test_init(self):
        """初期化のテスト"""
        self.assertEqual(self.weather_service.api_url, "https://map.yahooapis.jp/weather/V1/place")
        self.assertEqual(self.weather_service.geocoder_api_url, "https://map.yahooapis.jp/geocode/V1/geoCoder")
        self.assertEqual(self.weather_service.app_id, "test_app_id")
        self.assertEqual(self.weather_service.default_coordinates, "139.732293,35.663613")
        self.assertIn(32, self.weather_service.weather_codes)
        self.assertEqual(self.weather_service.weather_codes[32], "晴れ")
    
    @patch('requests.get')
    def test_get_coordinates_from_location_success(self, mock_get):
        """場所名から緯度経度を取得するテスト（成功）"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Feature": [
                {
                    "Geometry": {
                        "Type": "point",
                        "Coordinates": "139.73359259,35.66288632"
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # テスト対象メソッドの実行
        result = self.weather_service._get_coordinates_from_location("東京都港区六本木")
        
        # 検証
        self.assertEqual(result, "139.73359259,35.66288632")
        
        # requestsのget関数が正しいパラメータで呼ばれたことを確認
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://map.yahooapis.jp/geocode/V1/geoCoder")
        self.assertEqual(kwargs["params"]["query"], "東京都港区六本木")
        self.assertEqual(kwargs["params"]["appid"], "test_app_id")
        self.assertEqual(kwargs["params"]["output"], "json")
    
    @patch('requests.get')
    def test_get_coordinates_from_location_no_results(self, mock_get):
        """場所名から緯度経度を取得するテスト（結果なし）"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Feature": []}
        mock_get.return_value = mock_response
        
        # テスト対象メソッドの実行
        result = self.weather_service._get_coordinates_from_location("存在しない場所")
        
        # 検証（デフォルト座標が返されることを確認）
        self.assertEqual(result, "139.732293,35.663613")
    
    @patch('requests.get')
    def test_get_coordinates_from_location_error(self, mock_get):
        """場所名から緯度経度を取得するテスト（エラー）"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response
        
        # テスト対象メソッドの実行
        result = self.weather_service._get_coordinates_from_location("東京")
        
        # 検証（デフォルト座標が返されることを確認）
        self.assertEqual(result, "139.732293,35.663613")
    
    @patch('requests.get')
    def test_get_coordinates_from_location_exception(self, mock_get):
        """場所名から緯度経度を取得するテスト（例外）"""
        # モックレスポンスの設定
        mock_get.side_effect = Exception("Connection error")
        
        # テスト対象メソッドの実行
        result = self.weather_service._get_coordinates_from_location("東京")
        
        # 検証（デフォルト座標が返されることを確認）
        self.assertEqual(result, "139.732293,35.663613")
    
    @patch('services.weather_service.WeatherService._get_coordinates_from_location')
    @patch('requests.get')
    def test_fetch_yahoo_weather_success(self, mock_get, mock_get_coordinates):
        """Yahoo Weather APIからのデータ取得成功のテスト"""
        # 座標取得のモック
        mock_get_coordinates.return_value = "139.73359259,35.66288632"
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Feature": [
                {
                    "Property": {
                        "WeatherAreaCode": "4410",
                        "WeatherList": {
                            "Weather": [
                                {
                                    "Type": "observation",
                                    "Date": "202503161430",
                                    "Rainfall": "0.00"
                                },
                                {
                                    "Type": "forecast",
                                    "Date": "202503161530",
                                    "Rainfall": "1.25"
                                }
                            ]
                        }
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # テスト対象メソッドの実行
        result = self.weather_service._fetch_yahoo_weather("東京")
        
        # 検証
        self.assertIsNotNone(result)
        self.assertIn("Feature", result)
        self.assertEqual(result["Feature"][0]["Property"]["WeatherList"]["Weather"][0]["Rainfall"], "0.00")
        
        # requestsのget関数が正しいパラメータで呼ばれたことを確認
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://map.yahooapis.jp/weather/V1/place")
        self.assertEqual(kwargs["params"]["coordinates"], "139.73359259,35.66288632")
        self.assertEqual(kwargs["params"]["appid"], "test_app_id")
        self.assertEqual(kwargs["params"]["output"], "json")
    
    @patch('requests.get')
    def test_fetch_yahoo_weather_error(self, mock_get):
        """Yahoo Weather APIからのデータ取得エラーのテスト"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response
        
        # テスト対象メソッドの実行
        result = self.weather_service._fetch_yahoo_weather("東京")
        
        # 検証
        self.assertIsNone(result)
    
    @patch('requests.get')
    def test_fetch_yahoo_weather_exception(self, mock_get):
        """Yahoo Weather APIからのデータ取得例外のテスト"""
        # モックレスポンスの設定
        mock_get.side_effect = Exception("Connection error")
        
        # テスト対象メソッドの実行
        result = self.weather_service._fetch_yahoo_weather("東京")
        
        # 検証
        self.assertIsNone(result)
    
    def test_fetch_yahoo_weather_no_app_id(self):
        """Yahoo APP IDが設定されていない場合のテスト"""
        # APP IDを削除
        if 'YAHOO_APP_ID' in os.environ:
            del os.environ['YAHOO_APP_ID']
        
        # WeatherServiceのインスタンスを再作成
        weather_service = WeatherService()
        
        # テスト対象メソッドの実行
        result = weather_service._fetch_yahoo_weather("東京")
        
        # 検証
        self.assertIsNone(result)
    
    @patch('services.weather_service.WeatherService._get_coordinates_from_location')
    @patch('services.weather_service.WeatherService._fetch_yahoo_weather')
    def test_get_weather_success(self, mock_fetch, mock_get_coordinates):
        """天気情報取得成功のテスト"""
        # 座標取得のモック
        mock_get_coordinates.return_value = "139.73359259,35.66288632"
        # モックレスポンスの設定
        mock_fetch.return_value = {
            "Feature": [
                {
                    "Property": {
                        "WeatherAreaCode": "4410",
                        "WeatherList": {
                            "Weather": [
                                {
                                    "Type": "observation",
                                    "Date": "202503161430",
                                    "Rainfall": "0.00"
                                },
                                {
                                    "Type": "forecast",
                                    "Date": "202503161530",
                                    "Rainfall": "1.25"
                                }
                            ]
                        }
                    }
                }
            ]
        }
        
        # テスト対象メソッドの実行
        result = self.weather_service.get_weather("東京")
        
        # 検証
        self.assertIn("東京の天気", result)
        self.assertIn("晴れ", result)
        self.assertIn("現在の降水量 0.00mm/h", result)
        self.assertIn("15時30分の予測: 降水量 1.25mm/h", result)
        self.assertIn("火星の気温はマイナス60℃だぞ", result)
    
    @patch('services.weather_service.WeatherService._fetch_yahoo_weather')
    def test_get_weather_fallback(self, mock_fetch):
        """天気情報取得失敗時のフォールバックテスト"""
        # モックレスポンスの設定
        mock_fetch.return_value = None
        
        # テスト対象メソッドの実行
        result = self.weather_service.get_weather("東京")
        
        # 検証
        self.assertIn("東京の天気", result)
        # ランダム値のテストは難しいが、フォーマットは確認できる
        self.assertRegex(result, r"東京の天気:\n[^、]+、気温\d+℃\n\n火星の気温はマイナス60℃だぞ")
    
    @patch('services.weather_service.WeatherService._fetch_yahoo_weather')
    def test_get_weather_exception(self, mock_fetch):
        """天気情報取得中の例外テスト"""
        # モックレスポンスの設定
        mock_fetch.side_effect = Exception("Unexpected error")
        
        # テスト対象メソッドの実行
        result = self.weather_service.get_weather("東京")
        
        # 検証
        self.assertEqual(result, "天気情報を取得できませんでした。火星からの通信障害かもしれない。")

if __name__ == '__main__':
    unittest.main()
