# coding: UTF-8

import os
from os.path import join, dirname, exists
from dotenv import load_dotenv

dotenv_path = join(os.getcwd(), '.env')

if exists(dotenv_path):
    # .envファイルが存在する場合は読み込む
    load_dotenv(dotenv_path)
    print(".env file loaded successfully.")
else:
    # .envファイルが存在しない場合は環境変数から読み込む
    print(".env file not found. Using environment variables.")


"""==============================
Bot behavior
=============================="""
# 当サービスをDiscord Developer Portalに登録したApplicationと紐づけるためのToken
Token = os.environ.get("DISCORD_BOT_TOKEN")

# 最低勉強時間=VC滞在時間(秒)。これ未満の場合は記録を残さない
# MINIMUM_STUDY_TIME_TO_RECORD = 60 # second
MINIMUM_STUDY_TIME_TO_RECORD = 1 # second

# 最低勉強時間=VC滞在時間(秒)。これ未満の場合はDiscord ServerのStudyTimeTrackerChannelに勉強終了メッセージを飛ばさない
# MINIMUM_STUDY_TIME_TO_SEND_ON_STUDY_TRACKER = 300 
MINIMUM_STUDY_TIME_TO_SEND_ON_STUDY_TRACKER = 1

"""==============================
Discord Server information
@ToDo この辺の情報はServerに招待されたagent経由で取得したい
=============================="""
GuildId=os.environ.get("DISCORD_GUILD_ID")
StudyTimeTrackerChannelId=os.environ.get("DISCORD_STUDYTIME_TRACKER_CHANNEL_ID")

"""==============================
Google credential
=============================="""
FirebaseAipkey=os.environ.get("FIREBASE_API_KEY")
FirebaseshortLinksPrefix=os.environ.get("FIREBASE_DYNAMICLINKS_PREFIX")


# # 変数が設定されているかを確認
# if not secret_key or not database_url:
#     raise EnvironmentError("Required environment variables are missing.")