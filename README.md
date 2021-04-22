# About discord.study
[![GitHub forks](https://img.shields.io/github/forks/mo9mo9study/discord.VCtimeRecord.svg)](https://github.com/mo9mo9study/discord.VCtimeRecord/network)
![Discord](https://discordapp.com/api/guilds/603582455756095488/widget.png?style=shield)
Discord サーバー「もくもくOnline勉強会」のBotです。

# Future
- ORMを活用したDB連携のDMモジュールを作成してそれに対応したコードに書き換える
- 今後pep8に準拠した書式で記載する
- README.mdを最新情報に修正する

# commit時のローカル運用
- ディレクトリ[.githooks/]にてcommitをトリガーに動く処理を記載しています
  - pythonの[autopep8]と[flake8]をcommit対象のファイルに対して実行します
- これを活用することでpepに準拠するように自動修正やエラー箇所を出力してくれます
- ファイル[.githooks/pre-commit]はファイル[.pre-commit-config.yaml]を元に作成されています
```py
# pre-commitを活用するための準備
## git configのコマンドを用いて、.git/hooksのパスを変更します
git config core.hooksPath .githooks
```

# 当リポジトリのファイルを事項するための準備
## 環境はvenvにて作成しています
## 実行に必要なパッケージはrequirements.txtに記載しています
```py
# pythonの仮想環境を作成する
python3 -m venv venv
# 仮想環境にアタッチする
source venv/bin/activate
# 必要なパッケージを仮想環境ないでインストールする
pip3 install -r requirements.txt
```

# 必要な認証情報
1. DiscordBOTの認証情報
2. Googleのダイナミックリンクの認証情報
```py
# ファイルをコピーして必要な認証情報を埋め込む
cp .env.sample .env
vi .env
```


--- 以下、旧資料のため修正箇所 ---------------------------------
# 環境構築

## 注意
現状は、ローカルのファイルを変更しても、コンテナ内のファイルは変更されません。
自身でマウントする環境を作るか、変更毎にdockerをbuildし直す必要があります。

## 試した環境
```
macOS 10.15.x
docker 2.3.0.3
```

## 事前準備
- Dockerをインストールしましょう。Dockerの知識が必要です。
[https://docs.docker.com/](https://docs.docker.com/)
- ローカル開発するためのDiscordサーバーを立てておきましょう。
[サーバー作成方法](https://support.discord.com/hc/ja/articles/204849977-%E3%82%B5%E3%83%BC%E3%83%90%E3%83%BC%E3%81%AE%E4%BD%9C%E6%88%90%E3%81%AE%E4%BB%95%E6%96%B9)
- BOTをサーバーに登録します
[Discordリファレンス Botアカウント作成](https://discordpy.readthedocs.io/ja/latest/discord.html)


## Fork
Forkして自身のリポジトリからプルリクを作成してください。
```
$ git clone git@github.com:mo9mo9study/discord.study.git
$ cd discord.study
```

## .env 作成
.env.default をコピーして.envを作成。
```
$ cp -i $(pwd)/entry_exit/env_vars/{.env.default,.env}
```

## .envにDiscordへの接続情報を書き込む

### BOTトークン
[BOTのトークン取得方法](https://discordpy.readthedocs.io/ja/latest/discord.html#discord-intro)
参照 7.「Copy」ボタンを使ってトークンをコピーします。
.env
```
# プール監視員
export DISCORD_BOT_TOKEN=[BOTトークン]
# Cron
export CRON_BOT_TOKEN=[BOTトークン]
# テスト007
export TEST_BOT_TOKEN=[BOTトークン]
```

### サーバーID チャンネルID

IDの取得方法
- サーバーIDは、サーバーネームを右クリック
- チャンネルIDは、ちゃん粘るを右クリック
[ユーザー/サーバー/メッセージIDはどこで見つけられる？](https://support.discord.com/hc/ja/articles/206346498-%E3%83%A6%E3%83%BC%E3%82%B6%E3%83%BC-%E3%82%B5%E3%83%BC%E3%83%90%E3%83%BC-%E3%83%A1%E3%83%83%E3%82%BB%E3%83%BC%E3%82%B8ID%E3%81%AF%E3%81%A9%E3%81%93%E3%81%A7%E8%A6%8B%E3%81%A4%E3%81%91%E3%82%89%E3%82%8C%E3%82%8B-)


## Docker imageをbuild
discord.study ディレクトリ内で以下コマンドを実行
厳密にはDockerfileが存在する
Dockerを起動すると、自動でBotが起動する状態です。
```
docker build . -t discord.study
docker run -v $(pwd)/entry_exit/env_vars:/dotfiles -itd discord.study
docker ps # discord.studyが上がっていればok
```

## 起動したDocker imageのbashでログイン
```
docker exec -it $(docker ps -lq) bash
or
docker exec -it $(docker ps|grep discord.study|awk -F' ' '{print $1}') bash
```
この状態でDiscordサーバの音声チャネルに入退室すると、それを検知したenterBotがログを標準出力に出力します。

## Botの再起動
```
$ bash /usr/src/discord.study/entry_exit/observer.sh
```


# 以下、メモ
## quickstart
```
pip install -r requirements.txt
```


## sqlite3 databaseschema
```
CREATE TABLE mem_time(
    userid INT NOT NULL PRIMARY KEY,
    username TEXT NOT NULL,
    modifeid_datetime TEXT NOT NULL DEFAULT (DATETIME('now','localtime')),
    guild_join_datetime TEXT,
    voicechannel_lastjoin_datetime TEXT,
    voicechannel_lastleave_datetime TEXT,
    message_lastsent_datetime TEXT
);
```
### trriger
```
CREATE TRIGGER mem_time_trigger AFTER UPDATE ON mem_time
BEGIN
    UPDATE mem_time SET modifeid_datetime = datetime('now', 'localtime') WHERE userid = OLD.userid ;
END;
```
