from datetime import date, datetime, timedelta
import re
from typing import Union

import discord
from discord.ext import commands
from tqdm import tqdm

from .weekAggregate import Week_Aggregate
from .personalDayRecord import Personal_DayRecord


class Personal_WeekRecord(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 603582455756095488
        self.channel_id = 829515424042450984

    # 今週の月〜今日までの日付を取得

    def getweek_days(self):
        # 月曜(0)から今日の曜日までの曜日を示す数字を配列に格納
        weeknumber = list(range(date.today().weekday() + 1))
        week_days = []
        for i in weeknumber:
            week_day = date.today() \
                - timedelta(days=datetime.now().weekday()) + timedelta(days=i)
            week_days.append(week_day)
        startrangge_strdt = week_days[0].strftime("%Y-%m-%d")
        endrange_strdt = datetime.now().strftime("%m-%d")
        desc_week = f"{startrangge_strdt}〜{endrange_strdt}"
        return week_days, desc_week

    def format_userrecord(self, member, day, studytime, title):
        totalStudyTime = str(Week_Aggregate(
            self.bot).minutes2time(studytime)).strip()
        # DBからテンプレートテキストを取得して置換する処理に変更する
        week_result = f'''#{title}
-
-

#もくもくオンライン勉強会
[ {day}の勉強時間 ]
---> {totalStudyTime}
#mo9mo9_{member.id}
        '''
        return week_result

    def addembed_studytimebar(self, embed, targettime, weekstudymtime):
        weekstudyhtime = int(weekstudymtime) // 60
        if weekstudyhtime > int(targettime):  # 勉強時間/目標時間が100%を超えた場合の処理
            bar = str(tqdm(
                initial=weekstudyhtime,
                total=weekstudyhtime,
                ncols=77, desc="[達成度]",
                bar_format="""
{desc}{percentage:3.0f}%|{bar}|
--->現在の積み上げ：{n}h
--->週の目標時間　：{total}h
"""
            ))
            # 文字列の末尾の目標時間を以下の変数で置換
            bar = re.sub(rf"{str(weekstudyhtime)}h$",
                         f"{str(targettime)}h", bar)
        else:  # 勉強時間/目標時間が100%未満の場合の処理
            bar = str(tqdm(
                initial=weekstudyhtime,
                total=int(targettime),
                ncols=77, desc="[達成度]",
                bar_format="""
{desc}{percentage:3.0f}%|{bar}|
--->現在の積み上げ：{n}h
--->週の目標時間　：{total}h
"""
            ))
        bar = bar.replace(" ", "", 2)
        bar = bar.replace(" ", "----")
        embed.add_field(
            name=f"📊目標設定( {targettime}時間 )", value=bar, inline=False)
        return embed

    async def sendstrfembed(self, title, desc):
        embed = discord.Embed(title=title, description=desc)
        await self.dm.send(embed=embed)

    def embedweekresult(self, member) -> Union[discord.embeds.Embed, int]:
        week_days, desc_week = self.getweek_days()
        sum_studytime = Personal_DayRecord(self.bot) \
            .aggregate_user_record(member,
                                   week_days[0],
                                   datetime.today())
        sendmessage = self.format_userrecord(
            member, desc_week, sum_studytime, "今週の振り返り")
        return Personal_DayRecord(
            self.bot).create_twitter_embed(sendmessage), sum_studytime

    def embedlastweekresult(self, member) -> Union[discord.embeds.Embed, int]:
        lastweek_days, desc_lastweek = Week_Aggregate(
            self.bot).self.getlastweek_days()
        sum_studytime = Personal_DayRecord(self.bot) \
            .aggregate_user_record(member,
                                   lastweek_days[0],
                                   lastweek_days[-1])
        sendmessage = self.format_userrecord(
            member, desc_lastweek, sum_studytime, "先週の振り返り")
        return Personal_DayRecord(
            self.bot).create_twitter_embed(sendmessage), sum_studytime

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel = self.bot.get_guild(
            self.guild_id).get_channel(self.channel_id)
        # await self.channel.purge()
        embed = discord.Embed(title="あなたの今週の勉強記録の集計してDMに送信します",
                              description="👇 使い方\n（超簡単）このメッセージにリアクションをするだけ‼️")
        embed.add_field(name="1⃣：",
                        value="- 今週の勉強集計",
                        inline=False)
        embed.add_field(name="2⃣：",
                        value="- 先週の勉強集計",
                        inline=False)
        embed.add_field(name="3⃣：",
                        value="- 今週の勉強集計（進捗割合付）",
                        inline=False)
        embed.add_field(name="4⃣：",
                        value="- 先週の勉強集計（進捗割合付）",
                        inline=False)
        self.message = await self.channel.send(embed=embed)
        self.message_id = self.message.id
        await self.message.add_reaction("1⃣")
        await self.message.add_reaction("2⃣")
        await self.message.add_reaction("3⃣")
        await self.message.add_reaction("4⃣")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        if payload.channel_id == self.channel_id:
            embed = ""  # 190行目の対策、想定しないスタンプが押された時にembedが送信されないため
            member = payload.member.guild.get_member(
                payload.member.id)  # DM用のMemberオブジェクト生成
            self.dm = await member.create_dm()
        # --------------今週〜今日までの週間集計---------------------
        if payload.message_id == self.message_id:
            select_msg = await self.channel.fetch_message(payload.message_id)
            # --------------今週の勉強集計---------------------
            if payload.emoji.name == "1⃣":
                embed, sum_studytime = self.embedweekresult(member)
            # --------------先週の勉強集計---------------------
            elif payload.emoji.name == "2⃣":
                embed, sum_studytime = self.embedlastweekresult(member)
            # --------------今週の勉強集計（進捗割合付）---------------------
            elif payload.emoji.name == "3⃣":
                embed, sum_studytime = self.embedweekresult(member)
                embed = self.addembed_studytimebar(embed,
                                                   "30",
                                                   sum_studytime)
                embed.add_field(name="🛠️工事中",
                                value="現在、週の目標を３０時間に固定しています")
            # --------------先週の勉強集計（進捗割合付）---------------------
            elif payload.emoji.name == "4⃣":
                embed, sum_studytime = self.embedlastweekresult(member)
                embed = self.addembed_studytimebar(embed,
                                                   "30",
                                                   sum_studytime)
                embed.add_field(name="🛠️工事中",
                                value="現在、週の目標を３０時間に固定しています")
            else:
                msg = await self.channel.send("1⃣,2⃣,3⃣,4⃣のスタンプをクリック下さい")
                await msg.delete(delay=3)
            await select_msg.remove_reaction(payload.emoji, payload.member)
            if embed:
                # DB-ERROR:対象期間の勉強記録がない場合の処理
                if sum_studytime == 0:
                    await self.sendstrfembed("ERROR",
                                             "勉強記録がありません")
                else:
                    await self.dm.send(embed=embed)
            # --------------DBerror処理--------------
            # else:
            #    msg = await self.channel.send("今週の勉強記録が見つかりませんでした")
            #    await self.time_sleep(msg)


def setup(bot):
    return bot.add_cog(Personal_WeekRecord(bot))
