import functools
import random
from config import logger
from data.responses import TESLA_FACTS, SPACEX_FACTS, ELON_QUOTES, ELON_RESPONSES
from services.weather_service import WeatherService
from services.news_service import NewsService
from services.task_service import TaskService
from services.advice_service import AdviceService

def safe_reply(func):
    """LINE APIへの返信を安全に行うためのデコレータ"""
    @functools.wraps(func)
    def wrapper(self, event, *args, **kwargs):
        try:
            response = func(self, event, *args, **kwargs)
            if response:
                self.line_client.reply_message(event.reply_token, response)
            return True
        except Exception as e:
            logger.error(f"{func.__name__}の実行中にエラー発生: {str(e)}")
            return False
    return wrapper

class CommandHandler:
    """コマンドを処理するハンドラー"""
    
    def __init__(self, line_client):
        """
        コマンドハンドラーを初期化する
        
        Parameters:
        line_client (LineClient): LINE APIクライアント
        """
        self.line_client = line_client
        self.weather_service = WeatherService()
        self.news_service = NewsService()
        self.task_service = TaskService()
        self.advice_service = AdviceService()
        
        # コマンドマップ
        self.command_map = {
            "help": self.handle_help,
            "tesla": self.handle_tesla,
            "spacex": self.handle_spacex,
            "quote": self.handle_quote,
            "weather": self.handle_weather,
            "news": self.handle_news,
            "advice": self.handle_advice,
            "task": self.handle_task,
            "random": self.handle_random
        }
    
    def process_command(self, event, text):
        """
        コマンドを処理する
        
        Parameters:
        event (MessageEvent): LINEのメッセージイベント
        text (str): メッセージテキスト
        
        Returns:
        bool: 処理が成功した場合はTrue、そうでない場合はFalse
        """
        command = text[1:].split()[0]
        handler = self.command_map.get(command, self.handle_unknown)
        return handler(event, text)
    
    @safe_reply
    def handle_help(self, event, text):
        """
        helpコマンドを処理する
        
        Parameters:
        event (MessageEvent): LINEのメッセージイベント
        text (str): メッセージテキスト
        
        Returns:
        str: 応答メッセージ
        """
        help_text = """イーロン・マスクbotコマンド:
/tesla - テスラに関する事実
/spacex - SpaceXに関する事実
/quote - イーロン・マスクの名言
/weather [場所] - 天気情報
/news - 最新ニュース
/advice - イーロンからのアドバイス
/task [タスク名] - タスクを実行
/random - ランダムな返答
        """
        logger.info("help応答を送信しました")
        return help_text
    
    @safe_reply
    def handle_tesla(self, event, text):
        """
        teslaコマンドを処理する
        
        Parameters:
        event (MessageEvent): LINEのメッセージイベント
        text (str): メッセージテキスト
        
        Returns:
        str: 応答メッセージ
        """
        response = random.choice(TESLA_FACTS)
        logger.info(f"teslaコマンドの応答を送信: {response}")
        return response
    
    @safe_reply
    def handle_spacex(self, event, text):
        """
        spacexコマンドを処理する
        
        Parameters:
        event (MessageEvent): LINEのメッセージイベント
        text (str): メッセージテキスト
        
        Returns:
        str: 応答メッセージ
        """
        response = random.choice(SPACEX_FACTS)
        logger.info(f"spacexコマンドの応答を送信: {response}")
        return response
    
    @safe_reply
    def handle_quote(self, event, text):
        """
        quoteコマンドを処理する
        
        Parameters:
        event (MessageEvent): LINEのメッセージイベント
        text (str): メッセージテキスト
        
        Returns:
        str: 応答メッセージ
        """
        response = random.choice(ELON_QUOTES)
        logger.info(f"quoteコマンドの応答を送信: {response}")
        return response
    
    @safe_reply
    def handle_weather(self, event, text):
        """
        weatherコマンドを処理する
        
        Parameters:
        event (MessageEvent): LINEのメッセージイベント
        text (str): メッセージテキスト
        
        Returns:
        str: 応答メッセージ
        """
        # オプションで場所を指定可能
        parts = text.split()
        location = "東京"  # デフォルト
        if len(parts) > 1:
            location = parts[1]
        
        weather_info = self.weather_service.get_weather(location)
        logger.info(f"weather応答を送信: {weather_info[:30]}...")
        return weather_info
    
    @safe_reply
    def handle_news(self, event, text):
        """
        newsコマンドを処理する
        
        Parameters:
        event (MessageEvent): LINEのメッセージイベント
        text (str): メッセージテキスト
        
        Returns:
        str: 応答メッセージ
        """
        news_info = self.news_service.get_news()
        logger.info(f"news応答を送信: {news_info[:30]}...")
        return news_info
    
    @safe_reply
    def handle_advice(self, event, text):
        """
        adviceコマンドを処理する
        
        Parameters:
        event (MessageEvent): LINEのメッセージイベント
        text (str): メッセージテキスト
        
        Returns:
        str: 応答メッセージ
        """
        advice = self.advice_service.get_advice()
        logger.info(f"advice応答を送信: {advice[:30]}...")
        return advice
    
    @safe_reply
    def handle_task(self, event, text):
        """
        taskコマンドを処理する
        
        Parameters:
        event (MessageEvent): LINEのメッセージイベント
        text (str): メッセージテキスト
        
        Returns:
        str: 応答メッセージ
        """
        parts = text.split()
        task_type = "未指定のタスク"
        if len(parts) > 1:
            task_type = parts[1]
        
        task_result = self.task_service.execute_task(task_type)
        logger.info(f"task応答を送信: {task_result[:30]}...")
        return task_result
    
    @safe_reply
    def handle_random(self, event, text):
        """
        randomコマンドを処理する
        
        Parameters:
        event (MessageEvent): LINEのメッセージイベント
        text (str): メッセージテキスト
        
        Returns:
        str: 応答メッセージ
        """
        response = random.choice(ELON_RESPONSES)
        logger.info(f"randomコマンドの応答を送信: {response}")
        return response
    
    @safe_reply
    def handle_unknown(self, event, text):
        """
        未知のコマンドを処理する
        
        Parameters:
        event (MessageEvent): LINEのメッセージイベント
        text (str): メッセージテキスト
        
        Returns:
        str: 応答メッセージ
        """
        unknown_command = "未知のコマンドだ。/helpで使用可能なコマンドを確認してくれ。"
        logger.info("未知のコマンド応答を送信しました")
        return unknown_command
