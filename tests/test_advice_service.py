import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import random
import json

# Add the parent directory to the Python path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.advice_service import AdviceService
from data.responses import ADVICE_LIST

class TestAdviceService(unittest.TestCase):
    """AdviceServiceのテストクラス"""
    
    def setUp(self):
        """各テスト実行前の準備"""
        # AdviceServiceのインスタンスを作成
        self.advice_service = AdviceService()
        
        # randomのseedを固定して、テストの再現性を確保
        random.seed(42)
    
    def tearDown(self):
        """各テスト実行後のクリーンアップ"""
        # randomのseedをリセット
        random.seed()
    
    def test_get_advice_success(self):
        """アドバイス取得成功のテスト"""
        # テスト対象メソッドの実行
        result = self.advice_service.get_advice()
        
        # 検証: フォーマットが正しいことを確認
        self.assertTrue(result.startswith("イーロンからのアドバイス: "))
        self.assertTrue(any(advice in result for advice in ADVICE_LIST))
    
    @patch('random.choice')
    def test_get_advice_exception(self, mock_choice):
        """アドバイス取得中の例外テスト"""
        # random.choiceが例外を発生させるようにモック
        mock_choice.side_effect = Exception("Random choice error")
        
        # テスト対象メソッドの実行
        result = self.advice_service.get_advice()
        
        # 検証
        self.assertEqual(result, "アドバイスを提供できません。考え中だ。")
        
        # random.choiceが呼ばれたことを確認
        mock_choice.assert_called_once_with(ADVICE_LIST)
    
    def test_advice_format(self):
        """アドバイスのフォーマットテスト"""
        # 全てのアドバイスをテスト
        for advice in ADVICE_LIST:
            # random.choiceをモックして特定のアドバイスを返すようにする
            with patch('random.choice', return_value=advice):
                result = self.advice_service.get_advice()
                expected = f"イーロンからのアドバイス: {advice}"
                self.assertEqual(result, expected)
    
    @patch('requests.post')
    def test_get_themed_advice_success(self, mock_post):
        """テーマ付きアドバイス取得成功のテスト"""
        # 期待される結果
        advice_text = "未来を見据えて行動しろ。今日の決断が明日の現実を作る。"
        expected_advice = f"イーロンからのアドバイス: {advice_text}"
        
        # requestsのモックレスポンスを設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": advice_text
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # APIキーを直接設定
        self.advice_service.api_key = "dummy_key"
        
        # テスト実行
        result = self.advice_service.get_themed_advice("起業")
        
        # 検証
        self.assertEqual(result, expected_advice)
        mock_post.assert_called_once()
        
        # リクエストに起業に関するテーマが含まれていることを確認
        call_args = mock_post.call_args[1]
        request_data = call_args["json"]
        user_message = request_data["messages"][1]["content"]
        self.assertIn("起業", user_message)
    
    def test_get_themed_advice_no_api_key(self):
        """APIキーがない場合のテーマ付きアドバイステスト"""
        # APIキーがない場合は通常のget_adviceが呼ばれることを確認
        self.advice_service.api_key = None
        with patch.object(AdviceService, 'get_advice', return_value="イーロンからのアドバイス: テストアドバイス") as mock_get_advice:
            result = self.advice_service.get_themed_advice("起業")
            
            # 検証
            mock_get_advice.assert_called_once()
            self.assertEqual(result, "イーロンからのアドバイス: テストアドバイス")
    
    @patch('requests.post')
    def test_get_themed_advice_api_error(self, mock_post):
        """API呼び出しエラー時のテスト"""
        # requestsのモックを設定してエラーを発生させる
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        # APIキーを直接設定
        self.advice_service.api_key = "dummy_key"
        
        # get_adviceをモックしてフォールバックの動作を確認
        with patch.object(AdviceService, 'get_advice', return_value="イーロンからのアドバイス: フォールバックアドバイス") as mock_get_advice:
            result = self.advice_service.get_themed_advice("起業")
            
            # 検証
            mock_get_advice.assert_called_once()
            self.assertEqual(result, "イーロンからのアドバイス: フォールバックアドバイス")
    
    @patch('requests.post')
    def test_get_themed_advice_exception(self, mock_post):
        """例外発生時のテスト"""
        # requestsのモックを設定して例外を発生させる
        mock_post.side_effect = Exception("Connection error")
        
        # APIキーを直接設定
        self.advice_service.api_key = "dummy_key"
        
        # get_adviceをモックしてフォールバックの動作を確認
        with patch.object(AdviceService, 'get_advice', return_value="イーロンからのアドバイス: フォールバックアドバイス") as mock_get_advice:
            result = self.advice_service.get_themed_advice("起業")
            
            # 検証
            mock_get_advice.assert_called_once()
            self.assertEqual(result, "イーロンからのアドバイス: フォールバックアドバイス")

if __name__ == '__main__':
    unittest.main()
