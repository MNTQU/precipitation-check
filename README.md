# precipitation-check
指定した地点の降水量が0より大きいと予想されるときに、Slackにメッセージを送る

## 準備
Slack APIとYahooの[気象情報API](https://developer.yahoo.co.jp/webapi/map/openlocalplatform/v1/weather.html)のトークンが必要

## 使い方
crontabでスケジュールを設定
```
$ crontab -e
```
(例だと5分ごと)
```
5/ * * * * python precipitation-check.py
```