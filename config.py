# coding: UTF-8

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(os.getcwd(), '.env')
load_dotenv(dotenv_path)

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
