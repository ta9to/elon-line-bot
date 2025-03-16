import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the parent directory to the Python path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers.command_handler import CommandHandler
from services.weather_service import WeatherService

class TestCommandHandler(unittest.TestCase):
    """CommandHandlerのテストクラス"""
    
    def setUp(self):
        """各テスト実行前の準備"""
        # モックのLINEクライアントを作成
        self.mock_line_client = MagicMock()
        
        # CommandHandlerのインスタンスを作成
        self.command_handler = CommandHandler(self.mock_line_client)
        
        # WeatherServiceをモックに置き換え
        self.mock_weather_service = MagicMock()
        self.command_handler.weather_service = self.mock_weather_service
    
    @patch('handlers.command_handler.WeatherService')
    def test_init(self, mock_weather_service_class):
        """初期化のテスト"""
        # 新しいCommandHandlerインスタンスを作成
        handler = CommandHandler(self.mock_line_client)
        
        # WeatherServiceが初期化されたことを確認
        mock_weather_service_class.assert_called_once()
        
        # コマンドマップに'/weather'が含まれていることを確認
        self.assertIn('weather', handler.command_map)
        self.assertEqual(handler.command_map['weather'], handler.handle_weather)
    
    def test_handle_weather_default_location(self):
        """weatherコマンドのデフォルト位置のテスト"""
        # モックイベントの作成
        mock_event = MagicMock()
        mock_event.reply_token = "reply-token-123"
        
        # WeatherServiceのget_weatherメソッドのモック設定
        self.mock_weather_service.get_weather.return_value = "東京の天気: 晴れ、気温25℃"
        
        # テスト対象メソッドの実行
        result = self.command_handler.handle_weather(mock_event, "/weather")
        
        # 検証
        self.assertTrue(result)
        self.mock_weather_service.get_weather.assert_called_once_with("東京")
        self.mock_line_client.reply_message.assert_called_once_with(
            "reply-token-123", "東京の天気: 晴れ、気温25℃"
        )
    
    def test_handle_weather_custom_location(self):
        """weatherコマンドのカスタム位置のテスト"""
        # モックイベントの作成
        mock_event = MagicMock()
        mock_event.reply_token = "reply-token-123"
        
        # WeatherServiceのget_weatherメソッドのモック設定
        self.mock_weather_service.get_weather.return_value = "大阪の天気: 曇り、気温22℃"
        
        # テスト対象メソッドの実行
        result = self.command_handler.handle_weather(mock_event, "/weather 大阪")
        
        # 検証
        self.assertTrue(result)
        self.mock_weather_service.get_weather.assert_called_once_with("大阪")
        self.mock_line_client.reply_message.assert_called_once_with(
            "reply-token-123", "大阪の天気: 曇り、気温22℃"
        )
    
    def test_handle_weather_error(self):
        """weatherコマンドのエラーハンドリングテスト"""
        # モックイベントの作成
        mock_event = MagicMock()
        mock_event.reply_token = "reply-token-123"
        
        # WeatherServiceのget_weatherメソッドが例外を発生させるように設定
        self.mock_weather_service.get_weather.side_effect = Exception("API error")
        
        # テスト対象メソッドの実行
        result = self.command_handler.handle_weather(mock_event, "/weather")
        
        # 検証 - safe_replyデコレータによりFalseが返されることを確認
        self.assertFalse(result)
        self.mock_weather_service.get_weather.assert_called_once()
        # reply_messageは呼ばれないはず（例外がキャッチされるため）
        self.mock_line_client.reply_message.assert_not_called()

if __name__ == '__main__':
    unittest.main()
