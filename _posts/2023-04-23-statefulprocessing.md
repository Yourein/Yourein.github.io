---
layout: page
title: Stateful Processingとその思想
tags: [プログラミング]
thumbnail-img: 
---

Processingは、初学者でもGUIプログラミングに触れることが可能で、簡単なソフトウェアのプロトタイピングについても強力なプログラミング言語 (フレームワーク?) です。

一方で、多少込み入った動作を実装しようとしたときに困りごとが多く発生する面で、ソフトウェアの開発に向いている言語であるとは言えません。  
この記事ではそのような問題を解決する思想の一つとして、Stateful Processingという思想を紹介します。  

この内容は、4/30日に函館市 亀田交流プラザで行われたMariners' Conferenceでお話した内容をさらに深堀した内容となります。副読資料として、下にGoogle Slideをembedしています。適宜読んでみてください。

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vSuBEYSpA-3Ip_rFrvbPSQkeOI7gm3yVBRr1v_bJYFtbCTfGQa__Oo-bU4hyTTYsm0nLdfrsCKNQNHC/embed?start=false&loop=false&delayms=3000" frameborder="0" width="750" height="428" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

# Processingの辛さ

Processingは、その仕様から、どうしてもグローバル領域に様々なものが散乱しがちです。  
これは一般に避けるべきアンチパターンであることは、みなさんご存知のとおりだと思います。  

さらに、UIプログラミングの辛さもここに合わさってくる場合があります。  
具体的には、UIを描画する部分にBusiness Logicを記述することでViewとLogicが同じ関数内に存在するということが起こりえます。こちらも一般には避けるべきアンチパターンとされています。

具体的にサンプルコードを示しながら説明します。

```java
void stage() {
    int stage_state = 0;
    
    for (Block block : my_blocks) {
        if (block.hp > 0) {
            stage_state |= 1;
            break;
        }
    }

    for (Block block : enemy_blocks) {
        if (block.hp > 0) {
            stage_state |= 2;
            break;
        }
    }

    if (stage_state == 0 || stage_state == 1) {
        win();
    }
    else if (stage_state == 2) {
        lose();
    }
    else {
        update();
        draw_balls();
        draw_blocks();
        draw_racket();
    }
}
```

ブロック崩しのゲームをイメージしてください。  
自分と相手が対戦していて、相手は弾をStage上に打ち出してきます。自機は典型的なブロック崩しのラケットで、マウスでラケットを操作して、敵機が打ち出してきた弾を打ち返します。  
自分と相手がそれぞれ10ブロックを持っており、弾を打ち返して相手のブロックをすべて崩すことが勝利条件です。対して、弾を打ち返さずに自分が持っているブロックがすべて相手の弾に破壊されたら敗北です。

このコードは典型的なViewとLogicが混在したコードと言えます。  
まず、ステージが終了した(相手もしくは自分のブロックがすべて壊された)かの判定を2つのfor文を用いて`stage`関数内で行っています。

これを解決するために、for文での終了判定部分を別関数に切り出してみます。

```java
int check_win_or_lose() {
    int stage_state = 0;
    
    for (Block block : my_blocks) {
        if (block.hp > 0) {
            stage_state |= 1;
            break;
        }
    }

    for (Block block : enemy_blocks) {
        if (block.hp > 0) {
            stage_state |= 2;
            break;
        }
    }

    return stage_state;
}

void stage() {
    int stage_state = check_win_or_lose();

    if (stage_state == 0 || stage_state == 1) {
        win();
    }
    else if (stage_state == 2) {
        lose();
    }
    else {
        update();
        draw_balls();
        draw_blocks();
        draw_racket();
    }
}
```

これによって、Logicがベタ書きされていた状態はなくなりました。  
しかし、これでViewとLogicが分離されたとは言い難いです。

というのも、`stage`という関数のメインの役割はViewの描画なわけですが、ここに`check_win_or_lose`や`update`というLogicが混じっているのは適切ではありません。

これを解決するためにState hoistingという概念を用います。  
これは、Viewに必要なStateをViewの引数に渡して、State自体はViewを呼び出す関数やクラスで保持するという考え方で、Jetpack Composeの文脈で主に用いられる用語です。詳しくは[State and Jetpack Compose](https://developer.android.com/jetpack/compose/state#state-hoisting)を読んでください。

さて、これにしたがって、先程のコードをもう少し書き換えてみます。

```java
void stage(int stage_state) {
    if (stage_state == 0 || stage_state == 1) {
        win();
    }
    else if (stage_state == 2) {
        lose();
    }
    else {
        draw_balls();
        draw_blocks();
        draw_racket();
    }
}

void draw() {
    int state = check_win_or_lose();
    
    if (state == 3) {
        update();
    }

    stage(state);
}
```

Logicを担当するコードをもう一層上で呼び出し、Viewの描画に必要なStateは引数として渡しています。
これにより、最も最上層のdraw[^1]ではViewとLogicが混在してしまっていますが、Logicを担う関数はLogicに注力して、Viewを担う関数ではViewに注力するようになりました。

ところで、このコードにはまだ問題点があります。  
次は、ViewやLogic部分の話ではなく、`check_win_or_lose`関数の問題です。  
`check_win_or_lose`関数や、(ここでは定義を示していませんが、)`update`関数は`my_blocks`や`enemy_blocks`などのグローバル領域に置かれた変数を参照しています。

次に問題としたいのは、このグローバル領域に散乱する変数です。  
この節の最初にも書いたことではありますが、Processingではその仕様上、グローバル領域に変数が散乱しがちで、これを解決するのはかなり難しいです。  
グローバル領域にある変数は往々にして様々な関数から参照されるわけなので、ライフタイムや現在の状態を管理するのが非常に面倒です。ですので、解決するのは難しいですが、どうにかしたいというのは正直なところです。

# Statefulの原則

これらを解決するために、以下のような原則を提案します。

- State(変数)はそれに依存するViewが受け持つ
- View自身については、その親もしくはPAppletが受け持つ

より具体的には、View Partsをクラス化して、それぞれのStateをカプセル化してしまおうという発想です。  
しかし、View Partsの中には他のView Partsで起こったEventにしたがって状態を変化させる必要が生じる場面があります。そのような場合は、外部にsetterを提供することで解決することとします。  
ここでいう責務を受け持つとは、外部には「自分が変数hogeを持っています！」と周知し(実際クラス内部で宣言し)、その変数のライフタイムがView (のクラス) のライフタイムと一致するもしくは、Viewよりあとに誕生しViewより先に死ぬことをいいます。

例えば、以下のような例を考えてみます。

```java
class Hoge {
    private Huga hugaInstance;

    public Hoge(Huga h) {
        hugaInstance = h;
    }
}

class Huga {

}

Hoge hoge;
Huga huga;

void setup() {
    huga = new Huga();
    hoge = new Hoge(huga);
}
```

この例は、原則を守っていないと判断します。  
というのも、HogeのstateであるhugaInstanceのライフタイムがHogeのインスタンスであるhogeより長いからです。

これを解決する例として、Hogeのインスタンスを作成するときに一緒にHugaのインスタンスを生成するという方法があります。

```java
Hoge hoge;

void setup() {
    hoge = new Hoge(new Huga());
}
```

構文解析的にはHugaのインスタンスほうが生成されるタイミングが早いですが、Hugaのポインタは外部に露出しておらず、十分にHugaというStateに対する責任を持てていると思います。

# View と Logicを分離する

先程のState hoistingの例で、`draw`関数内部ではまあLogic関数とView関数が同時に呼ばれても仕方ないだろうとしていましたが、本当は、極力そういった部分を減らしたいです。

そこで、Event Flowという概念を導入します。  
詳しくは後々説明するので、ここでは深く考えなくて結構ですが、それぞれのViewはこのEvent Flowというものを監視します。  
Event Flowには`enum Event`が流れてきて、自分に関係のあるEventが流れてきたら、それに合わせて対応を行うという形を取ることで、ViewとLogicをあたかも別スレッドで処理しているかのような気持ちになれます。 (実際はEvent FlowにEventを流す処理が手続き的にあるので、全くそんなことはない)

# 実装

[![Yourein/ProcessingState - GitHub](https://gh-card.dev/repos/Yourein/ProcessingState.svg)](https://github.com/Yourein/ProcessingState)

詳細は上のGitHubレポジトリを見ていただけるといいと思います。(一部以下で紹介する実装と異なる部分がありますが、これについては後で補足します。)

## 基底クラス

まず、Viewを定義するクラスのためのinterfaceを定義します。[^2]

```java
interface View {
    abstract public void draw();
}

interface Interactive {
    abstract public void onEvent(Event kind);
}

abstract class Actionable {
    abstract protected void action(Event kind);
}
```

また、これを継承した抽象クラスを定義します。実際のViewを定義する際はこれから定義する抽象クラスのなかから適切なものを選んで継承します。

```java
abstract class Item implements View {
    private Point position;

    abstract public void draw();
}

abstract class InteractiveItem implements View, Interactive {
    private Point position;

    abstract public void draw();
    abstract public void onEvent(Event kind);
}

abstract class InteractiveActionableItem extends Actionable implements View, Interactive {
    private Point position;

    abstract public void draw();
    abstract public void onEvent(Event kind);
    abstract protected void action(Event kind);
}
```

つづいて、`onEvent`や`action`が引数としてとる`Event`を定義します。

```java
enum Event {
    onKeyTyped, onKeyPressed, onKeyReleaseed,
    onClicked, onDragged, onMouseMoved, onMousePressed, onMouseReleased, onMouseWheel,
    newFrame
}
```

`Event`はenum型で、単にイベントの種別を判断するためだけに用いられるものです。

最後に、`Point`型の定義を示しておきます。(単純にx, yがfloatで入っているだけです。)

```java
class Point {
    public float x;
    public float y;

    public Point(float _x, float _y) {
        x = _x;
        y = _y;
    }
}
```

## 各クラスの意味

上の実装例では`Item`、`InteractiveItem`、`InteractiveActionableItem`という3つの抽象クラスを定義しました。  
これらについて、補足をします。

これからこのクラスを使って行っていくことはViewを木構造とすることです。  
Statefulの原則にもあったように、Viewの責任はその親が持つこととしています。逆に、親Viewは子Viewの責任を持ちます。これは、子のmethodやstateに干渉できるのは基本的に直属の親しかいない状態を表していて、一つのViewが0個以上いくつかのViewを持つことを考えると、自ずとView全体は木構造となります。

木のノードはそれぞれ上の抽象クラスいずれかを継承したもので、親と子の間でStateのやりとりが発生する場合があることを`InteractiveItem`と`InteractiveActionableItem`という2つのクラスが明示するようになっています。

より具体的には、`InteractiveItem`は上層から流れてくるEvent Flowを`onEvent`関数でcatchして、`InteractiveActionableItem`は`onEvent`関数でcatchされたEventの結果、callbackが必要となった場合に`onEvent`関数から呼ばれます。

抽象的なレベルに話を戻すと、Viewはその直属の親に依存しており、`InteractiveItem`を継承したViewには直属の親からEvent Flowを監視する(親から子への一方通行の)pipeがあり、`InteractiveActionableItem`を継承したViewには直属の親と双方向にやりとりをするpipeがあるというイメージです。

## Event Flow

先程からちょこちょこEvent Flowという言葉を使っているので、ここで説明を入れることにします。  
`InteractiveItem`が上層からEventを受け取った後、その`InteractiveItem`の子Viewのうち、`InteractiveItem`かもしくは`InteractiveActionableItem`である子、すなわち、`interface Interactive`をimplementsしている子に対して上層から受け取ったEventをバケツリレー式に流してもらう動作を実装します。  

```java
class HogeView extends InteractiveView {
    private Point position;
    private ArrayList<View> childs;

    public HogeView(Point pos) {
        position = pos;

        // 子Viewの宣言とか
        // (コンストラクタの引数として子Viewを受け取ってもいい)
    }

    void draw() {
        childs.stream().forEach((i) -> { i.draw(); });
    }

    void onEvent(Event kind) {
        childs.stream()
            .filter((i) -> { return i instanceOf Interactive; });
            .forEach((i) -> { i.onEvent(kind); });
    }
}
```

これによって、最上位(PApplet)で発生したEventを木構造の葉に当たる部分のViewまで伝播させることができます。  

この動作がリアクティブプログラミングにおけるFlowやグラフ理論におけるFlow(を流している状態)に見えるのでFlowと呼んでいますが、実際にはDFSや木上のクエリ処理と言ったほうが正しいかもしれません。

イメージ的には、この問題で時間計算量を考えずにナイーブに実装したパターンと見て取ることもできますね。  
- [D - Ki : AtCoder Beginner Contest 138](https://atcoder.jp/contests/abc138/tasks/abc138_d)

## Viewを作る

実際に先程定義した抽象クラスを用いて、Viewを作ってみます。  
今回はButtonを例として作ってみることにします。  

```java
interface ClickHandler {
    public onClicked();
}

class Button extends InteractiveActionableItem {
    private Point position;
    private float viewWidth, viewHeight;
    private ClickHandler clickHandler;

    public Button(Point pos, float _width, float _height, ClickHandler handler) {
        position = pos;
        viewWidth = _width;
        viewHeight = _height;
        clickHandler = handler;
    }

    public void draw() {}
    public void onEvnet(Event kind) {}
    protected void action(Event kind) {}
}
```

`ClickHandler`というinterfaceを定義することで、lambdaを受け取れるようにします。いわゆる`@FunctionalInterface`というやつです。[^3]

以下は特にonEventとactionの実装について見てみます。

```java
public void onEvent(Event kind) {
    if (kind == Event.onClicked) {
        if (isMouseOverRect(position.x, position.y, position.x + viewWidth, position.y + viewHeight)) {
            action(kind);
        }
    }
}

public void action(Event kind) {
    if (kind == Event.onClicked) {
        clickHandler.onClicked();
    }
}
```

まず、onEventに渡されたEvent種別を確認します。  
ボタンなので、マウスがクリックされたイベント、すなわち`Event.onClicked`以外は無視してしまって大丈夫です。もし他の機能をViewに搭載したい場合は必要な場合もあるので、適宜追加します。

`Event.onClicked`をcatchすると、マウスカーソルがボタンを表す矩形上にあるかを確認します。  
矩形上にあるならばaction関数に渡します。

本当ならば、ここでaction関数に渡さずに、onEvent関数に処理を任せてもいいですが、actionの処理が込み入った処理である場合や、他のEventもcatchしなければいけないViewでは可読性が低下する可能性があります。  
ゆえに、あえてcallbackや内部処理を行う部分をactionという別関数に切り分けることで一定の可読性を担保する設計としています。  
もし葉が`InteractiveItem`で、`action`がない場合は、何かしら別のprivateな関数を作ってそこでハンドリングすることをおすすめします。(必須ではないです)

## How the View should be?

Stateful ProcessingではViewの実装について詳細なことを定めていません。  
既存のProcessingのように`width`, `height`を用いたり、座標をベタ書きしても良いと思いますし、Viewが木構造であることを利用して宣言的UIのようなシステムを構築してもよいと思います。

## Viewの結合

ボタンを実装してみたので、実際にこのボタンを使ったコードを書いてみることにします。
このサンプルのrepoは下のリンクから見れます。

[![Yourein/ProcessingState - GitHub](https://gh-card.dev/repos/Yourein/ProcessingState.svg)](https://github.com/Yourein/ProcessingState)

ボタンを押した回数、画面に表示されるカウンタがインクリメントされて行くようなアプリを考えます。

まずは、カウンタ部分を実装してみます。

```java
class CounterView extends Item {
    private int count = 0;
    private Point position;

    public CounterView(Point pos) {
        position = pos;
    }

    public void draw() {
        fill(255);
        String content = "Current: " + count;
        text(content, position.x - textWidth(content)/2.0, position.y);
        fill(0);
    }

    public void increment() {
        this.count++;
    }
}
```

`count`というメンバをもち、setterとして`increment`というpublicなメンバ関数を持ちます。

次に、`Button`と`CounterView`をまとめるViewを作ります。

```java
class RootView extends InteractiveItem {
    ArrayList<View> child = new ArrayList<View>();
    private Point position = new Point(0, 0);

    public RootView() {
        child.add(
            new Button(
                new Point(width/2 - 100, height/2 + 50),
                230,
                80,
                "Button",
                () -> { this.incrementCounter(); }
            )
        );

        child.add(
            new CounterView(
                new Point(width/2, height/2)
            )
        );
    }

    void draw() {
        child.stream().forEach((i) -> { i.draw(); });
    }

    void onEvent(Event kind) {
        child.stream()
            .filter((i) -> { 
                return i instanceof Interactive; 
            })
            .forEach((i) -> {
                ((Interactive) i).onEvent(kind);
            });
    }

    void incrementCounter() {
        ((CounterView) this.child.get(1)).increment();
    }
}
```

ここまで上のViewなら、コンストラクタ内で子Viewのインスタンスを生成してしまって良いと思います。  
下に行けば行くほどに上層のViewの情報を必要とするViewが多くなる傾向があるため、適切な部分を見つけて、コンストラクタの中で宣言をベタ書きするのをやめるのが良いと思います。

これで必要なViewは揃ったので、あとはこれをPApplet側から呼び出すだけです。

```java
RootView rootView;

void setup() {
    size(1280, 720);
    textSize(48);
    
    rootView = new RootView();
}

void draw() {
    background(50);
    
    rootView.draw();
}

void mouseClicked() { rootView.onEvent(Event.onClicked); }
```

さて、これでアプリケーションは完成です(GIFを埋め込んでも良かったのですが、手元で動かして頂いたほうがいいかなと思うので、Git cloneして手元で動かしてみてください)。

## View Tree

上のアプリケーションがどのような構造になっているかを分解してみます。

![](https://firebasestorage.googleapis.com/v0/b/kdatabase-1088a.appspot.com/o/statefulprocessing%2FScreenshot from 2023-04-26 22-27-10.png?alt=media)



[^1]: Processingではこの`void draw`関数が最上層になります。Arduinoの`void loop`と同じようなものだと思っていただければ大丈夫です。
[^2]: Actionableがabstract classとなっていますが、これは`action`を`protected`とするためです。
[^3]: Processing-3を使っている人は、lambdaが使えないので、適宜別の実装をしてください。lambdaみたいな抽象クラスを定義して、具象クラスをインスタンスとして渡す実装をすると良いです。