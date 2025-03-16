#!/bin/bash
# イーロン・マスクBotをAWS Lambdaに更新するスクリプト

# 設定変数
LAMBDA_FUNCTION_NAME="elon-line-bot"  # Lambda関数名を実際の名前に合わせて変更してください
DEPLOYMENT_ZIP="elon-bot-deployment.zip"
REGION="ap-northeast-1"  # リージョンを実際の値に合わせて変更してください
TEMP_DIR="deploy_package"  # 一時ディレクトリ (.gitignoreに追加済み)

# 一時ディレクトリの作成
echo "デプロイパッケージを作成中..."
mkdir -p $TEMP_DIR
cd $TEMP_DIR

# 既存のファイルがあれば削除
rm -rf *

# 依存関係をインストール
echo "依存関係をインストール中..."
pip install line-bot-sdk requests -t .

# Lambda関数コードをコピー
echo "Lambda関数コードをコピー中..."
cp ../lambda_function.py .
cp ../config.py .
cp ../line_client.py .

# ディレクトリ構造を作成
mkdir -p handlers services data

# 各モジュールをコピー
cp ../handlers/*.py handlers/
cp ../services/*.py services/
cp ../data/*.py data/

# ZIPファイルを作成
echo "ZIPファイルを作成中..."
zip -r ../$DEPLOYMENT_ZIP .
cd ..

# AWS Lambdaへアップロード
echo "AWS Lambdaへアップロード中..."
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --zip-file fileb://$DEPLOYMENT_ZIP \
    --region $REGION

# 結果確認
if [ $? -eq 0 ]; then
    echo "デプロイ成功: $LAMBDA_FUNCTION_NAME がアップデートされました。"
else
    echo "エラー: デプロイに失敗しました。"
    exit 1
fi

# デプロイパッケージの最新の設定情報を表示
echo "Lambda関数の情報を取得中..."
aws lambda get-function \
    --function-name $LAMBDA_FUNCTION_NAME \
    --region $REGION \
    --query 'Configuration.[FunctionName,LastModified,Version,MemorySize,Timeout]'

echo "デプロイ完了!"
