import os
import logging

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数から設定を取得
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
YAHOO_APP_ID = os.environ.get('YAHOO_APP_ID')

# その他の設定
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
