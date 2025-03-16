import random
import json
import requests
from config import logger, OPENAI_API_KEY
from data.responses import ADVICE_LIST

class AdviceService:
    """アドバイスを提供するサービス"""
    
    def __init__(self):
        """サービスの初期化"""
        self.api_key = OPENAI_API_KEY
    
    def get_advice(self):
        """
        イーロン・マスクからのランダムなアドバイスを取得する
        
        Returns:
        str: アドバイス
        """
        try:
            advice = random.choice(ADVICE_LIST)
            return f"イーロンからのアドバイス: {advice}"
        except Exception as e:
            logger.error(f"アドバイス取得中にエラー発生: {str(e)}")
            return "アドバイスを提供できません。考え中だ。"
    
    def get_themed_advice(self, theme):
        """
        指定されたテーマに基づいてイーロン・マスクからのアドバイスを生成する
        
        Parameters:
        theme (str): アドバイスのテーマ
        
        Returns:
        str: 生成されたアドバイス
        """
        if not self.api_key:
            logger.warning("OpenAI APIキーが設定されていないため、ランダムなアドバイスを返します")
            return self.get_advice()
        
        try:
            # OpenAI API エンドポイント
            url = "https://api.openai.com/v1/chat/completions"
            
            # リクエストヘッダー
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # リクエストボディ
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "あなたはイーロン・マスクです。イーロン・マスクらしい口調、視点、考え方で回答してください。"
                    },
                    {
                        "role": "user",
                        "content": f"「{theme}」についてのアドバイスを日本語で簡潔に1-2文で教えてください。"
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 150
            }
            
            # APIリクエスト
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            # レスポンスの確認
            if response.status_code == 200:
                response_json = response.json()
                advice = response_json["choices"][0]["message"]["content"].strip()
                
                # イーロンからのアドバイスという形式に整形
                if not advice.startswith("イーロンからのアドバイス:"):
                    advice = f"イーロンからのアドバイス: {advice}"
                
                return advice
            else:
                logger.error(f"OpenAI API エラー: {response.status_code} - {response.text}")
                return self.get_advice()
            
        except Exception as e:
            logger.error(f"OpenAI APIでのアドバイス生成中にエラー発生: {str(e)}")
            # エラーが発生した場合はランダムなアドバイスを返す
            return self.get_advice()
