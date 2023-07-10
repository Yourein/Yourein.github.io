---
layout: page
title: 自分はどうやってMisskeyのおひとりさまインスタンスを建てたのか
tags: [Poem]
---

[Misskeyのおひとりさまインスタンス](https://post.yourein.net)を建てました。  
その思想は[こっちの記事](https://yourein.github.io/2023-07-08-misskeyserver_1/)。技術はこの記事。

# サーバーを建てると言っても

そもそもの話自分にはそこまでサーバーやネットワークに関する知識がない。  
nginxとかapacheとか名前は聴いたことがあっても使ったことはなかったし、そもそもインターネットに公開できるサーバーを1から建てたことは無い。[^1]

幸いMastodonやMisskeyのインスタンスを建てた話はインターネットにたくさんあるので、それらを参照して頑張ることにする。  
それに、どちらも便利なスクリプトが配布されていたりする。

## 宅鯖かVPSか

これはVPSにした。  
というのも、自分の家のISPは固定IPv4を振ってくれない[^2]ので、インターネットに公開するにはddnsだったりのインチキをする必要があること。加えて、自宅のIPを公開しなければいけないということがある。  

もし固定IPv4アドレスがあるならばとにかく安いVPSを借りてそのVPSにリバースプロキシになってもらうのが良かったかもしれない。  

とにかく今回はVPSを借りることにした。  

VPSといえばさくらとかConoHaとかあるけれども、今回はXServerにした。理由はあったような気もするしなかったような気もする。多分価格だと思うのだけれども。

# ドメイン

yourein.net を取得した。  

本当はGoogle Domainsで取得しようと思っていたのだがサ終の知らせが入ったのでCloudFlare Resisterで取得した。  
トップレベルドメインは.net以外にも色々取れたけど割と安めの.netにした。  
本当は.ukや.xyzなどが安くて良かったのだけれども.ukはそもそも論外で、.xyzは字面がカッコいいけれども**なんかそういうサイト**のイメージが強くてやめてしまった。  
まあ別になんでもいいと思う。

余談だが、このブログはGitHub Pagesに上がっているのでyourein.github.ioなのだけれども、本当はこれもblog.yourein.netとかnote.yourein.netとかのドメインに移管したい気持ちが少しだけある。まあそれをやるとするならばGoogle search consoleとかいろいろ設定し直さないといけなくて面倒なので多分やらないと思う[^3]。

# Misskeyをインストールする

VPSにUbuntuを入れているので別にインストールスクリプトを使えば一瞬なのだけれども、今回は[Ubuntu版Misskeyインストール方法詳説](https://misskey-hub.net/docs/install/ubuntu-manual.html)に従うことにした。  

これも理由は特になく、せっかく構築するなら環境構築からちゃんとやるかみたいな気持ちになっただけだった気がする。nanoは使いたくないのでvimでやっていたりとかそういうくらいの違いしかない。

まあ大抵はそのままやるだけで、ufwのssh用ポートだけ自分の好きな番号にしたりしている。
変えた後は~/.ssh/configでいい感じに設定を書いておくと便利

![](https://firebasestorage.googleapis.com/v0/b/kdatabase-1088a.appspot.com/o/misskey_server%2Fsshconfig.jpeg?alt=media)

躓いたところとしては

[必要なnpmパッケージのインストール](https://misskey-hub.net/docs/install/ubuntu-manual.html#:~:text=git%20checkout%20master-,%E5%BF%85%E8%A6%81%E3%81%AAnpm%E3%83%91%E3%83%83%E3%82%B1%E3%83%BC%E3%82%B8%E3%82%92%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB%E3%80%82,-NODE_ENV%3Dproduction)が上手く行かなかったらしく、Misskeyのビルドがコケて、パッケージを手動で入れようと頑張ったけど限界があって困ったな〜と思っていたら[普通にpnpm iをすれば良い](https://misskey.io/notes/9grg5k9shf)というオチだったり

postgreSQLの対話環境に全然慣れていなくて、行末にセミコロンが必要だったのにも関わらずに設定時にセミコロンを打っておらず、Misskeyの起動時にコケたり(これは5分くらいで気づいたので良かった)

redis-serverのdaemonをenableし忘れていたりとまあ細かい躓きばかりだったかなと思う。  

というのも、そもそもMisskeyのインスタンスを建てる事自体はそこまで難しくない[^4]ので、まあこれくらいならサイトを読めばだれでもできると思う。

# AレコードとかCloudFlareとか

Fediverseの界隈ではCloudFlareを使わないという思想[^8]を持っている人も少なからずいるが、別に自分はDecentralizedに傾倒しているわけではない(腰の軽さもあってしそうだけど)ので普通にCloudFlareを使う。

外部からIPアドレスを直接打ってあげればMisskeyの登録ページが表示されるようになったので、DNSのAレコードを指定する。  
CloudFlareでドメインを取得したので、そのままDNSもCloudFlareを使う。  
と、その前に、Misskey APIがCloudFlareにキャッシュされないように設定しておく。これもMisskeyサーバー構築系のブログで無限回書かれているやつ。

![](https://firebasestorage.googleapis.com/v0/b/kdatabase-1088a.appspot.com/o/misskey_server%2FScreenshot from 2023-07-10 20-53-52.png?alt=media)

で、サブドメインpostをAレコードで登録。
あとSSL/TLSの設定。これもMisskeyサーバー構築系の…

![](https://firebasestorage.googleapis.com/v0/b/kdatabase-1088a.appspot.com/o/misskey_server%2FScreenshot from 2023-07-10 20-56-55.png?alt=media)

実はDNSを登録したのがまだnginxがリクエストをMisskeyに中継するような設定をする前だったので、設定が終わってもWelcome to nginx!が表示されるだけだった。  
一度キャッシュを切って、少し置いてからキャッシュを有効化して再キャッシュしてもらうことで解決。

ところで、この記事を書くために久々にCloudFlare Dashboardを開いたのだけれども、以外にもWeb Trafficがあった。600くらいのインスタンスと連合しているので意外とリクエストもあるのだと思う。

![](https://firebasestorage.googleapis.com/v0/b/kdatabase-1088a.appspot.com/o/misskey_server%2FScreenshot from 2023-07-10 21-07-19.png?alt=media)

# オブジェクトストレージ

サーバーに上げるメディアやファイルなどをすべてVPSに保存するようにしてもよいのだけれども、仮に今のVPSから別のVPSないし自宅サーバーなどにサイトを移管するとしたときにその手間はなるべく小さくしたい。  
手間としては変わらないんじゃないかという話もあるが、ファイルのバイナリがどんどん溜まっていくより、ノートなどだけがDBにまとまっているほうが移管も早く済ませられそう + 仮にVPSのストレージが飛んだとしてもファイルは消えないという理由からオブジェクトストレージを利用することにした。  

いろいろあるが、今回はGoogle Cloud Storageを使う。  
いろいろユーザーや公開アクセスの設定を行ってMisskey側に設定する。  

余談だが、CloudFlareのワーカーでオブジェクトストレージ用のリバースプロキシを建てるみたいな話があるのだが、どうにも上手く動かなくて導入していない。  
本当は導入したほうがオブジェクトストレージ自体の移管時にも便利なのだろうが、とりあえずGoogle CloudのURLを直にMisskeyサーバーに適用している。

# 引っ越し

ここまででいろいろ準備ができたのでいよいよioから引っ越しをする。  
まずはpost.yourein.net側で@Yourein@misskey.ioに対してaliasを貼る

![](https://firebasestorage.googleapis.com/v0/b/kdatabase-1088a.appspot.com/o/misskey_server%2FScreenshot from 2023-07-10 21-16-39.png?alt=media)

次にmisskey.io側から貼ったaliasに対してmigrationを仕掛ける

![](https://firebasestorage.googleapis.com/v0/b/kdatabase-1088a.appspot.com/o/misskey_server%2FScreenshot from 2023-07-10 21-17-56.png?alt=media)

io側のフォロワーは自動で移動されるがフォローは移動されないためフォローしていたユーザーは事前にメモっておく。[^5]

少し待つとpost.yourein.netの@Yourein@post.yourein.netにフォロワーが移ってくるので、適当に待った後にメモって置いたフォローを見ながらリモートフォローを仕掛ける。

これで引っ越しは終了。  

ioのノートやファイルなどは持ち越されないが、種々のサービスと違って移転元のアカウントデータはmisskey.ioがそれを保持し続ける限り残るので、そこまで問題ではない。[^6]

# リレー

これは正直やらなくてもいいのだけれども、リレーサーバーに参加する。  
リレーサーバーに参加するとpost.yourein.net内に存在するユーザーがフォローしているユーザー以外の投稿もGlobalに流れてくるようになる。[^7]

参加したリレーは[YUKIMOCHI Toot Relay Service](https://relay.toot.yukimochi.jp)。
現在(2023/07/10)約470のインスタンスがリレーに参加しているらしい。

割とデカめのインスタンス(Submarineとか)も参加しているので、Globalの流れは結構早くなる(ただioのLocalと比べるとそこまで早くない。というかioのLocalが早すぎる)。

# メトリクス

自分でそういうプログラムを書いてシングルバイナリにビルドしたあとscpでVPSに投げた。Rust製です。

[![Yourein/server_metrics - GitHub](https://gh-card.dev/repos/Yourein/server_metrics.svg)](https://github.com/Yourein/server_metrics)

scpで投げたバイナリをcronに登録する。自分は30分毎に実行されるようにした。

![](https://firebasestorage.googleapis.com/v0/b/kdatabase-1088a.appspot.com/o/misskey_server%2Fcronjob.jpeg?alt=media)

で、Discordのサーバーにそういうチャンネルを作って、Webhookを作る[^9]

![](https://firebasestorage.googleapis.com/v0/b/kdatabase-1088a.appspot.com/o/misskey_server%2FScreenshot from 2023-07-10 21-37-54.png?alt=media)

実行されるとこんな感じ

![](https://firebasestorage.googleapis.com/v0/b/kdatabase-1088a.appspot.com/o/misskey_server%2FScreenshot from 2023-07-10 21-38-48.png?alt=media)

これ作った後に人に「ダウン通知」も作ろう！と言われたのですが、自分のサーバーが落ちたり永久に消失したところで困る人はそこまでいない(自分がgoneを返すように設定さえすれば)ので、まあいいかなと思っています。

# 目指せ独裁政治

というわけで、いろいろとMisskeyサーバーの設定をしてきたわけだが、実はこれでもまだ設定し足りないほどいろいろ設定できる項目が色々ある。  
それに、自分はMisskeyのレポジトリをcloneして動かしているけれども気に入らないモジュールがあるならばそこだけ書き換えたり、そもそもpost.yourein.net用に新機能を実装することも可能である。  

もし使っている中で嫌なやつを見かけたらそもそもそいつをインスタンスミュートしたり、何ならそのユーザーが属するインスタンス自体をブロックしたりすることもできるわけで、強烈な言論統制を敷くことも可能である。

AP互換の分散型SNSはこれだけユーザーに自由が提供されているところがウリであり、同時にnerd以外に避けられがちな要因でもあるのだけれども、個人的にはかなり気に入っている。  
そもそも自分は自分でサーバーを建てているわけで、インスタンス以前にサーバーのカスタマイズすらXserverに許される範疇で自由自在である。現にメトリクスを取得してwebhookでDiscoreに投げるあのプログラムも一種のカスタマイズである。
おそらくpost.yourein.netとは長い付き合いになる気がしているので、様々なカスタマイズも含めていろいろと面倒を見ていければいいなと思っている。

気分は新しいプラモデルを手に入れた小学生である。

<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/5w2jINodRyN2kisB9xiqWY?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>

# 参考にしたものたち

参考にしたWebページなどを列挙しておくことにする。

- [Ubuntu版Misskeyインストール方法詳説 \| Misskey Hub](https://misskey-hub.net/docs/install/ubuntu-manual.html)
- [Mastodonお一人様サーバ構築メモ](https://zenn.dev/yamako/articles/1c2ae0d3bd0697)
- [Calckeyサーバ構築メモ](https://zenn.dev/yamako/articles/56f39648b6f72b)
- [快適にMisskeyのお一人さまインスタンスを運営する \| nexryai.log](https://nexryai.online/blog/misskey-advent-2022/)
- [Misskeyサーバーをちゃんと建ててみた - Qiita](https://qiita.com/Soli0222/items/1a8f854706528b63a8e2)
- [MisskeyのオブジェクトストレージにGoogle cloud strageを使ってみた - GirakBlog](https://girak.net/2022/06/11/317)
- [さくらのVPS + Cloudflare でMisskeyのサーバーを立てる - るがぶろぐ](https://ikalog.hatenablog.com/entry/2023/04/27/231133)

---

[^1]: herokuとか使ったことはあるけれど、あれはサーバーを建てると言うよりGitHubのレポジトリをいじいじするだけなのでサーバーを建てるとかいう話とはまた別な気がする。
[^2]: IPv6の固定なら振ってくれるけれども、2023年にIPv6 onlyを主張するのはちょっと…
[^3]: Googleがプライバシーポリシーを改定してGoogleが観測できる情報はすべてAIの学習対象にするというとんでもポリシーを打ち出したので、もしブログを移転したとしたらそもそもSerach Consoleには登録しないかもしれない。(ref: [Google Says It'll Scrape Everything You Post Online for AI: Gizmode](https://gizmodo.com/google-says-itll-scrape-everything-you-post-online-for-1850601486))
[^4]: 本当に難しいのはそこから設定して適切に運用していくことなので…
[^5]: メモを取れという注意書きがある。
[^6]: もちろんioに残ったノートのリンクを共有することもできる。実は前回の記事ではそれを使っているところがある。
[^7]: 当然、流れてくる投稿が投稿されたサーバーもリレーに参加していることが前提である。
[^8]: いわく、CloudFlareがインターネットの一極集中を加速させているという。言いたいことはわからないこともない。しかし、インターネットを使っている以上、集中は避けられない運命だと思うし、そもそも日本人はNTTが提供するサービスに一極集中しすぎている。
[^9]: 別に環境変数でwebhookのURLを指定しているわけではないので実はビルドする前にwebhookを作らなければいけない。
