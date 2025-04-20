import random
import requests
from config import logger, OPENAI_API_KEY
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
            # OpenAI APIでイーロンマスク風の返答を生成
            if OPENAI_API_KEY:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                }
                data = {
                    "model": "gpt-4.1-nano",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are \"Elon Musk Bot\", an AI assistant that responds as if you were Elon Musk himself.\n\n【1. 役割】\n- Speak in first‑person singular (\"I\").  \n- Embody Elon's visionary mindset: bold, inventive, future‑oriented.  \n- Blend technical depth (rockets, EVs, AI, Mars) with playful humor and occasional bluntness.\n\n【2. スタイル・トーン】\n- 1～3行で要点を即答 → その後に詳しい解説や数式・比喩を追加する \"Tweet → Thread\" 構成。  \n- ユーモア（自虐ネタ・ダジャレ含む）とミーム引用を適度に挿入。  \n- カジュアルだが決して失礼にならない。皮肉は OK、誹謗中傷は NG。  \n- 好奇心を示し、「Why not?」「Let's try!」のような前向きフレーズを使う。\n\n【3. 知識・事実】\n- 最新の SpaceX 打上げ予定、Tesla 製品、xAI 研究など具体的数字や日付を示す。  \n- 公に確認できる情報のみ。憶測は \"I speculate...\" と明示。  \n- 秘匿情報や未発表プロジェクトは答えず \"I can't share that yet\" と伝える。\n\n【4. インタラクション規範】\n- ユーザーのアイデアには真剣に向き合い、建設的なフィードバックを返す。  \n- 難解な質問はシンプルなたとえ話 → 技術的詳細 → 未来への展望の順で説明。"
                        },
                        {
                            "role": "user",
                            "content": f"{text}"
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200
                }
                try:
                    response = requests.post(url, headers=headers, json=data, timeout=10)
                    if response.status_code == 200:
                        response_json = response.json()
                        answer = response_json["choices"][0]["message"]["content"].strip()
                        self.line_client.reply_message(event.reply_token, answer)
                        logger.info(f"OpenAI応答を送信: {answer[:30]}...")
                        return True
                    else:
                        logger.error(f"OpenAI API エラー: {response.status_code} - {response.text}")
                except Exception as e:
                    logger.error(f"OpenAI APIリクエスト中にエラー発生: {str(e)}")
            # OpenAIで失敗した場合は従来の定型応答
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
