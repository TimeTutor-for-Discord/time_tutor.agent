import os
from datetime import datetime, timedelta

from discord.ext import commands
import discord
from dotenv import load_dotenv
import urllib.parse
import json
import requests
from sqlalchemy import func as F

from .weekAggregate import Week_Aggregate
from mo9mo9db.dbtables import Studytimelogs


class Personal_DayRecord(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 603582455756095488
        self.channel_id = 829515424042450984
        self.googleApiKey = os.environ.get("FIREBASE_API_KEY")
        self.googleShortLinksPrefix = os.environ.get(
            "FIREBASE_DYNAMICLINKS_PREFIX")
        dotenv_path = os.path.join(os.getcwd(), '.env')
        load_dotenv(dotenv_path)

    # datetime型をdate型に変換する処理
    def ifdatetimefdate(self, targetdate):
        if type(targetdate) == datetime:
            targetdate = targetdate.date()
        return targetdate

    # 現状、日次からはdatetime型、週次からはdate型が引数で流れてくる
    # startrange_dt/endrange_dtは[datetime.datetime] or [datetime.date]
    def aggregate_user_record(self, member, startrange_dt,
                              endrange_dt) -> int:
        # ユーザーの勉強記録を取得
        session = Studytimelogs.session()
        days_timedelta = 1
        endrange_nextday = endrange_dt + timedelta(days=days_timedelta)
        endrange = self.ifdatetimefdate(endrange_nextday)
        startrange = self.ifdatetimefdate(startrange_dt)
        obj = session.query(F.sum(Studytimelogs.studytime_min)).filter(
            Studytimelogs.member_id == member.id,
            Studytimelogs.access == "out",
            Studytimelogs.excluded_record.isnot(True),
            Studytimelogs.study_dt >= startrange,
            Studytimelogs.study_dt < endrange,
            Studytimelogs.studytime_min.isnot(None)).first()
        sum_studytime = obj[0]
        if isinstance(sum_studytime, type(None)):
            sum_studytime = 0
        return sum_studytime

    def createTwitterUrlEncode(self, websiteUrl, sendContent):
        encodeContent = urllib.parse.quote(sendContent)
        twitterUrl = "https://twitter.com/share?url={}&text={}".format(
            websiteUrl, encodeContent)
        return twitterUrl

    def shorten_url(self, url, prefix, key):
        '''Firebase Dynamic Link を使って URL を短縮する'''
        baseurl = 'https://firebasedynamiclinks.googleapis.com/'
        post_url = "{}v1/shortLinks?key={}".format(baseurl, key)
        payload = {
            "dynamicLinkInfo": {
                "domainUriPrefix": prefix,
                "link": url
            },
            "suffix": {"option": "SHORT"}
        }
        headers = {'Content-type': 'application/json'}
        r = requests.post(post_url, data=json.dumps(payload), headers=headers)
        if not r.ok:
            # DBへエラー処理を追加する
            # print(str(r), file=sys.stderr)
            return None
        return json.loads(r.content)["shortLink"]

    # 週間と被るが、一旦日次分の処理を追加
    # 今後、統一していってほしい
    # 関数名がxxxになっている集計

    def aggregate_day_users_record(self, member, day) -> int:
        session = Studytimelogs.session()
        obj = session.query(F.sum(Studytimelogs.studytime_min)).filter(
            Studytimelogs.member_id == member.id,
            Studytimelogs.access == "out",
            Studytimelogs.studytime_min.isnot(None)).first()
        return int(obj[0])

    def compose_user_record(self, day, studytime):
        day_result = '''
#今日の積み上げ
-
-

#もくもくオンライン勉強会
[ {day}の勉強時間 ]
---> {totalStudyTime}
        '''.format(day=day,
                   totalStudyTime=str(Week_Aggregate(self.bot)
                                      .minutes2time(studytime))).strip()
        return day_result

    def create_twitter_embed(self, sendMessage):
        longUrl = self.createTwitterUrlEncode(
            "https://mo9mo9study.github.io/discord.web/", sendMessage)
        encodeMessage = self.shorten_url(
            longUrl, self.googleShortLinksPrefix, self.googleApiKey)
        embed = discord.Embed(title="📤積み上げツイート用",
                              description=sendMessage, color=0xFDB46C)
        embed.add_field(name="🦜下のURLから簡単に積み上げツイートが出来るよ", value=encodeMessage)
        return embed

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel = self.bot.get_guild(
            self.guild_id).get_channel(self.channel_id)
        await self.channel.purge()
        embed = discord.Embed(title="あなたの１日の勉強記録の集計してDMに送信します",
                              description="👇 使い方\n（超簡単）このメッセージにリアクションをするだけ‼️")
        embed.add_field(name="1⃣：",
                        value="- 今日の勉強集計",
                        inline=False)
        embed.add_field(name="2⃣：",
                        value="- 昨日の勉強集計",
                        inline=False)
        embed.add_field(name="3⃣：",
                        value="- 今日の勉強集計（times送信）",
                        inline=False)
        embed.add_field(name="4⃣：",
                        value="- 昨日の勉強集計（times送信）",
                        inline=False)
        self.message = await self.channel.send(embed=embed)
        self.message_id = self.message.id
        await self.message.add_reaction("1⃣")
        await self.message.add_reaction("2⃣")
        await self.message.add_reaction("3⃣")
        await self.message.add_reaction("4⃣")

    def searchmytimes(self, payload) -> "discord.channel":
        for channel in payload.member.guild.text_channels:
            if str(payload.member.id) == channel.topic:
                timeschannel = channel
                break
        return timeschannel

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        if payload.channel_id == self.channel_id:
            embed = ""  # 行目の対策、想定しないスタンプが押された時にembedが送信されないため
            member = payload.member.guild.get_member(
                payload.member.id)  # DM用のMemberオブジェクト生成
            dm = await member.create_dm()
            today = datetime.today()
        # --------------日間集計---------------------
        if payload.message_id == self.message_id:
            select_msg = await self.channel.fetch_message(payload.message_id)
            # --------------今日のの勉強集計---------------------
            # --------------今日の勉強集計（times）---------------------
            if payload.emoji.name in ["1⃣", "3⃣"]:
                strtoday = today.strftime('%Y-%m-%d')
                sum_studytime = self.aggregate_user_record(
                    member, today, today)
                sendMessage = self.compose_user_record(
                    strtoday, sum_studytime)
                embed = self.create_twitter_embed(sendMessage)
            # --------------昨日の勉強集計---------------------
            # --------------昨日の勉強集計（times）---------------------
            elif payload.emoji.name in ["2⃣", "4⃣"]:
                yesterday = today - timedelta(1)
                strday = yesterday.strftime('%Y-%m-%d')
                sum_studytime = self.aggregate_user_record(
                    member, yesterday, yesterday)
                sendMessage = self.compose_user_record(
                    strday, sum_studytime)
                embed = self.create_twitter_embed(sendMessage)
            else:
                msg = await self.channel.send("1⃣,2⃣,3⃣,4⃣のスタンプをクリック下さい")
                await msg.delete(delay=3)
            await select_msg.remove_reaction(payload.emoji, payload.member)
            if embed:
                if payload.emoji.name in ["1⃣", "2⃣"]:
                    msg = await self.channel.send("DMを送信しました")
                    await msg.delete(delay=3)
                    await dm.send(embed=embed)
                elif payload.emoji.name in ["3⃣", "4⃣"]:
                    for channel in payload.member.guild.text_channels:
                        if str(payload.member.id) == channel.topic:
                            timeschannel = channel
                            break
                    timeschannel = self.searchmytimes(payload)
                    msg = await self.channel.send(f"{channel.mention}に送信しました")
                    await msg.delete(delay=5)
                    sendmsg = await timeschannel.send(embed=embed)
                    await sendmsg.add_reaction("<:otsukaresama:757813789952573520>")  # noqa:E501

    # このコマンドが使えなくなったことを知らせるメッセージを返す
    @commands.group(invoke_without_command=True)
    async def result_d(self, ctx, *args):
        if ctx.subcommand_passed is None:
            embed = discord.Embed(title="もうこのコマンドは使えなくなったの。", color=0xff0000)
            embed.add_field(name="テキストチャンネル[ #個人勉強集計 ]のスタンプを押して集計してみてね",
                            value="""※ 4/23日から処理のトリガーを切り替えたけど、きっと慣れたら楽になはず！
                            何か気になることあれば気軽に[ @すー ]まで気軽に連絡してね""",
                            )
            command_channel = self.bot.get_channel(829515424042450984)
            member = ctx.guild.get_member(ctx.author.id)
            await ctx.channel.send(embed=embed)
            msg = await command_channel.send(
                f"{member.mention} テキストチャンネル[ #個人勉強集計 ]はここだよーーー！"
            )
            await msg.delete(delay=5)


def setup(bot):
    return bot.add_cog(Personal_DayRecord(bot))
