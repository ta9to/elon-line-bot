import datetime
from config import logger

class TaskService:
    """タスク実行サービス"""
    
    def execute_task(self, task_type):
        """
        タスクを実行する
        
        Parameters:
        task_type (str): タスクの種類
        
        Returns:
        str: タスク実行結果
        """
        try:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return f"タスク '{task_type}' を実行しました。\n実行時間: {current_time}\n\n火星からのメッセージ: 常に前進せよ！"
        except Exception as e:
            logger.error(f"タスク実行中にエラー発生: {str(e)}")
            return f"タスク '{task_type}' の実行に失敗しました。イノベーションには時に失敗がつきものだ。"
