---
layout: page
title: JSONにバイトエンコードされた文字列を乗せたいときに読む記事
tags: [Python3]
---

まれに発生する要望だと思います。

# 文脈

Pythonの暗号ライブラリ ```crypto``` にあるRSA暗号を使って文字列を暗号化するとバイトエンコードされた文字列が手に入ります。\
これをJSONに乗せてサーバーサイドに送りたいという状況になりました(具体的にはパスワードを暗号化して送信したかった)

しかしJSONにバイトエンコードされた文字列をそのまま乗せることはできません。\
やろうとすると「Object of type bytes is not JSON serializable」と怒られます。

# 結論

バイトエンコードされた文字列をBase64エンコード→文字列にデコードというステップを踏んでからJSONに乗せるとよいです。

```python
import requests
import json
import base64

crypted = b"Hello world" #暗号化されたバイト文字列 (この状態では乗らない)
b64_message = base64.b64encode(crypted) #暗号化された文章をそのままデコードするとエラーなので注意
send_message = b64_message.decode('utf-8')

send_data = {'message': send_message}

request.post(url, json = json.dumps(send_data, ensure_ascii = False, indent = 4), headers={'Content-Type': 'application/json'})
```