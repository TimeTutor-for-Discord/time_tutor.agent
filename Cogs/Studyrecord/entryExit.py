from datetime import datetime, timedelta, date, time

from discord.ext import commands

from mo9mo9db.dbtables import Studytimelogs  # noqa: E402, F401

import config

class ENTRY_EXIT(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild_id = config.GuildId  # もくもくOnline勉強会 # configに切り出す
        self.studytime_tracker_channel_id = config.StudyTimeTrackerChannelId  # 勉強記録   # system_channel的用途。勉強記録のリアタイログを１箇所に出力。これはconfigに切り出す
        self.NotRecordChannels = "記録無" # このキーワードが含まれているVCの時間記録は行わない。 @ToDo agent経由でignore対象のカテゴリかVCを登録できるようにしたい
        self.iri = "<:iri:873655671873212467> " # もくもくサーバで昔利用できたカスタム絵文字。現在はサーバブースト無効化により使用不可
        self.de = "<:de:873655671919370262>" # もくもくサーバで昔利用できたカスタム絵文字。現在はサーバブースト無効化により使用不可

    async def writeLog(self,
                       study_dt,
                       member,
                       channel,
                       access,
                       studytime_min=None):

        print(f"---> {self.studytime_tracker_channel_id}")
        print(f"---> {channel}")
        obj = Studytimelogs(
            study_dt=study_dt,
            guild_id=member.guild.id,
            member_id=member.id,
            voice_id=channel.id,
            access=access,
            studytime_min=studytime_min,
            studytag_no=None)
        if (self.isNotSubjectToRecordByChannel(channel)):
            print(f'{member.name} : 記録対象外のチャンネルなので記録しません')
            obj.excluded_record = True
        Studytimelogs.insert(obj)
        return obj

    # 勉強記録対象の勉強記録から最後の入室時間を取得
    def getStudyDt(self, member):
        session = Studytimelogs.session()
        obj = Studytimelogs.objects(session).filter(
            Studytimelogs.member_id == member.id,
            Studytimelogs.access == "in").order_by(
            Studytimelogs.study_dt.desc()).first()
        return obj.study_dt

    # メッセージを送信 # 送信先：self.studytime_tracker_channel_id
    async def sendstudytimelogmsg(self, now, member, study_room, access,
                                  study_seconds=None):
        if self.isNotSubjectToRecord(study_room):
            return
        print(f"[{now}] {member.name} {access}ログをDiscordに出力")
        lowerLimitToRecord=int(config.MINIMUM_STUDY_TIME_TO_RECORD)
        send_channel = self.bot.get_channel(int(self.studytime_tracker_channel_id))        
        print(f"{send_channel}に勉強記録を送信")
        if access == "in":
            print(f"入室")
            msg = f"{self.iri} [{now}]  {member.name}  joined the  {study_room.channel.name}." # noqa: E501 # flake8の指摘を無視するための記述。 noqa は "No Quality Assurance"
        elif access == "out":
            print(f"退室")
            msg = f"{self.de} [{now}]  {member.name}  Study time  {int(study_seconds / 60)} /分 *{int(lowerLimitToRecord)}分未満の場合は記録されません" # noqa: E501
        print(f"{msg}")
        await send_channel.send(msg)

    # 勉強記録対象外のVCであればTrueを返す
    def isNotSubjectToRecordByChannel(self, channel):
        return (channel is None or self.NotRecordChannels in channel.name) # 現状はchannel名に"記録無"が含まれていると記録対象外と判定される仕様
    def isNotSubjectToRecord(self, vc):
        return self.isNotSubjectToRecordByChannel(vc.channel) # Pythonにはオーバーロードが無さそうなのでとりあえず

    # 勉強時間開始とみなす条件を満たしていたらTrueを返す
    def isStartTheStudySession(self, before, after):
        # 条件
        #   before.channelがNone or 記録対象外
        #   かつ、
        #   after.channelがNone or 記録対象外ではなく、before.channelと異なる
        #====
        # after.channelがNone or 記録対象外
        if (self.isNotSubjectToRecord(after)):
            return False
        # before.channelがNone or 記録対象外 かつ　before != after
        if (self.isNotSubjectToRecord(before)
            and before.channel != after.channel):
            return True 
        return False

    # 勉強時間終了とみなす条件を満たしていたらtrueを返す
    def isFinishTheStudySession(self, before, after):
        # after.channelがNone or 記録対象外の場合
        return (self.isNotSubjectToRecord(after))


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # channelに変更がない＝VCから移動していない
        if before.channel == after.channel:
            return
        if member.bot:
            print(f'{member.name} : BOTは記録しません') # @ToDo: Logger
            return
        lowerLimitToRecord=int(config.MINIMUM_STUDY_TIME_TO_RECORD)
        lowerLimitToSend=int(config.MINIMUM_STUDY_TIME_TO_SEND_ON_STUDY_TRACKER)

        now = f" {(datetime.utcnow() + timedelta(hours=9)):%m-%d %H:%M} "
        print(f"[{now}]{member.name} : {before.channel}/{after.channel}")
        study_dt = datetime.utcnow() + timedelta(hours=9)
        # VC入室 かつ 勉強開始とみなす条件を満たしている場合    
        if (self.isStartTheStudySession(before, after)):
            print(f'{member.name} : 勉強開始時の処理')
            study_room = after
            access = "in"
            # @ToDo 前回の勉強時間がlowerLimitToRecord秒未満だった場合、access=inのレコードのみ残っているはず。そちらを物理or論理削除するロジックを追加する。そうしないと短期間でVCに出入りするとレコードを無限に増やせる
            #       e.g) select * from studytimelogs where member_id = member.id order by id desc limit 1で取得したレコードのaccessがinだった場合に処理する
            # RDB切り離し前：select→update or delete
            # RDB切り離し後：データを処理してくれるサービスへリクエストを投げる or Queueにリクエストを登録してあとはお任せ

            # DBに入室記録を登録
            await self.writeLog(study_dt, member, study_room.channel, access)
            # Discord ServerのStudy Tracker Channelにもメッセージを出力
            await self.sendstudytimelogmsg(now, member, study_room, access)
        # VC退室 かつ 勉強終了とみなす条件を満たしている場合
        elif (self.isFinishTheStudySession(before, after)):
            print(f'{member.name} : 勉強終了時の処理')
            study_room = before
            access = "out"

            try:
                start_datetime = self.getStudyDt(member) # 勉強開始時間取得
                finish_datetime = datetime.now()
                print(f"---> 勉強開始日時: {start_datetime}")

                study_delta   = finish_datetime - start_datetime
                study_seconds = int(study_delta.total_seconds())
                study_minutes = int(study_seconds / 60) # 小数点以下を切り捨てたいがそのためだけにmathをimportするのも気が引けたのでこれで

                # 勉強時間をDBへ記録
                if study_seconds >= lowerLimitToRecord:  # lowerLimitToRecord秒未満は記録しない 短時間に多数出入りをするとDBに多数のレコードを作られてしまうため
                    print(f'{member.name} : {lowerLimitToRecord}sec以上')
                    await self.writeLog(finish_datetime,
                                        member,
                                        study_room.channel,
                                        access,
                                        str(study_minutes))

                # 勉強時間をDiscord Serverに送信
                await self.sendstudytimelogmsg(now,
                                               member,
                                               study_room,
                                               access,
                                               study_seconds)
            except KeyError:
                print(f'{member.name} : Detected KeyError exception.')
                pass


def setup(bot):
    return bot.add_cog(ENTRY_EXIT(bot))
