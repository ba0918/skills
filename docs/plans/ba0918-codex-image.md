# ba0918-codex-image 実装計画

## Goal

ユーザーのざっくりした指示から、Codex の画像生成で素材を作るスキル `ba0918-codex-image` を
このリポジトリの `skills/` に入れる。素材はシリーズの参照画像とスタイル定義に沿って作り、同梱の
スクリプトで決まった後処理と自動の検収を通してから残す。README から使い方と送信の注意が分かる
状態にする。

## Specification

[docs/spec/ba0918-codex-image.md](../spec/ba0918-codex-image.md)。コミット「docs: ba0918-codex-image
の仕様と用語を追加」で承認され、「docs: ba0918-codex-image のアニメーションのシートを 4 列固定に
する」「docs: ba0918-codex-image の透過とアニメーションの境界を決める」で追記された。以下、節は
`#見出し名` で示す。

この計画は仕様の文章を写さない。各ステップで挙げた節を、必ず仕様書そのもので読むこと。
用語（シリーズ、ドット絵、ドット絵風、テンプレート画像）の定義は、`PROJECT.md` の Glossary 節の
「ba0918-codex-image」にある。

書き方の参考として [docs/spec/ba0918-codex-exec.md](../spec/ba0918-codex-exec.md) と
`skills/ba0918-codex-exec/SKILL.md` を読んでよい。ただし、このスキルは ba0918-codex-exec に依存
しない（`#移植性と単体完結`）。

## Approach and why

成果物は 2 種類ある。後処理と検収を行う Python のスクリプトと、エージェントが読む指示文書
（`SKILL.md` と `references/`）である。

1. **スクリプトを先に、テスト駆動で作る。** 数値の仕様を守らせるのはスクリプトの役目で、
   `SKILL.md` はその呼び方を書く。呼び方（引数）が固まってから指示文書を書けば、書き直しが要らない。
   スクリプトのテストは T-01〜T-10（`#自動テスト`）と、この計画が名前を付けた追加のテスト
   （T-11〜T-14、各ステップに記す）で、1 つの振る舞いに 1 つのテストを書く。追加のテストは、
   仕様に書かれた規則のうち T-01〜T-10 が触れていないものだけを確かめる。
2. **スクリプトの引数は、この計画で決める**（仕様の `#委任`）。次のとおりにする。

   ```
   codex_image.py template --stand <PNG> [--frames <F>] --out <PNG>
   codex_image.py process  --series <series.md> --raw <PNG> --out <PNG> [--frames <F> --stand <PNG>] [--no-ground]
   codex_image.py check    --series <series.md> --raw <PNG> [--frames <F> --stand <PNG>]
   codex_image.py preview  --sheet <PNG> --frames <F> --out <GIF> [--ms <N>]
   ```

   - `--stand` はドット絵の完成品（例 32×32 の正方形）で、キャンバスのドット数はその 1 辺の px から
     読む。正方形でなければ入力の誤りである。
   - `template` に `--frames` を渡さないと、立ち絵を 1 枚だけ拡大した画像になる。これを参照画像を
     生成に渡すときの拡大に使う（`#シリーズ`）。`--frames` を渡すと、テンプレート画像になる。
     1 ドットはどちらも 10px ちょうどにする（仕様の「約 10px」を、この計画で 10px に決める）。
   - `--frames` を渡さない `process`・`check` は 1 枚の素材として扱う（行数も列数も 1）。
     `--frames` を渡すと、アニメーションのシートとして扱う。行数と列数は `#アニメーション` の
     規則でコマ数から決まるので、別の引数にしない。`--frames` は 2〜16 で、アニメーションとして扱う
     ときは `--stand` が要る。`kind: pixel` かつ `transparent: true` の `series.md` でなければ、
     `--frames` は入力の誤りである（`#アニメーション`）。
   - `--no-ground` は足元を揃えない指定である（ジャンプなど）。
   - 1 ドットのマス目が整数の px にならない元画像（1254px に 32 ドットなど）では、マス目 i の中心を
     `floor((i + 0.5) × 画像の幅 ÷ ドット数)` の px とする（縦も同じ）。
   - `check` は判定の JSON を標準出力に書いて終了コード 0 で終わる（`pass`・`fail`・`undetermined`
     のどれでも 0）。`series.md` の定義が誤っているときは、JSON を書かずに、標準エラーに理由を
     書いて 0 以外で終わる（T-01）。`process` と `template` と `preview` も、入力の誤りでは
     0 以外で終わる。
3. **`series.md` の front matter は自前で読む。** 後処理の実行手段は `uv run --with pillow` である
   （`#後処理の入り口`）。YAML のライブラリに頼ると依存が増えるため、先頭の `---` で囲まれた
   `キー: 値` の行だけを読む。値に使うのは仕様の 4 項目の書き方（`pixel`、`32`、`1024x1024`、
   `true`）だけである。引用符、行末のコメント、入れ子は受け付けない。
4. **テストはスクリプトを別プロセスで呼ぶ。** テストを動かしている Python（`sys.executable`）で
   `scripts/codex_image.py` を起動する。テストのコマンドが Pillow を入れた環境を用意するので、
   テストの中で `uv` は呼ばない。テストが呼ぶのは入り口（サブコマンド）だけにし、内部の関数を
   直接呼ばない。テスト用の画像は、Pillow でテストの中で合成する。画像
   ファイルをリポジトリに置かない。
5. **本文は英語で書く。** `PROJECT.md` の「言語方針」による。仕様は日本語なので、意図を英語で書く。
   用語は次の英語にそろえ、本文の最初に出るところで短く定義する。
   - シリーズ → "series"（"set"、"theme" と呼ばない）
   - ドット絵 → "pixel sprite"。`kind: pixel` に当たる
   - ドット絵風 → "pixel-style illustration"。`kind: illustration` の一種
   - テンプレート画像 → "template image"（裸の "template" はサブコマンド名だけに使う）
   - "pixel art" は、ドット絵とドット絵風のどちらにも読めるので使わない
6. **プロンプトの骨組みは `references/prompts.md` に置く。** 立ち絵、新しいシリーズの候補、
   アニメーションのシート、Web 素材の 4 つである。試行で効いた書き方（引き継ぐもの／引き継がない
   もの、加工せずに保存、演出のコマを描かない、端から約 1 割に主題を置かない）は、どれも
   プロンプトの文面でしか効かない。本文から、プロンプトを組み立てるときに読むよう指示する。
7. **`SKILL.md` は ba0918-codex-exec と同じ流儀の骨組みにする。** Scope、When this runs、What is
   sent、Before generating、Series、Procedure、Acceptance and retries、Files and cleanup、
   Judgment の並びにする。中身は写さない（あちらは呼び出し元がプロンプトを用意する前提で、
   このスキルはプロンプトを自分で組み立てる）。500 行以内に収める。
8. **Codex に添付する画像は 1 回 1 枚にする**（`#外部への送信`）。プロンプトでは、生成した画像を
   作業フォルダーの `raw.png` という名前で、加工せずに保存するよう指示する。スキルはそれを素材の
   フォルダーの `raw.png` に移す。

## Scope of change

- `skills/ba0918-codex-image/SKILL.md`（新規）
- `skills/ba0918-codex-image/references/prompts.md`（新規）
- `skills/ba0918-codex-image/scripts/codex_image.py`（新規）
- `tests/ba0918-codex-image/`（新規。テストのファイルだけ）
- `README.md`（スキル一覧への 1 行と、使い方と注意の節）
- `PROJECT.md`（Commands の表の Test 欄だけ）

これ以外のファイルは変えない。仕様書と Glossary は承認済みなので触らない。

## Step order and prerequisites

この計画は、承認されたら `main` にコミットされる。実装を始める前に、`git log --oneline -- docs/plans/ba0918-codex-image.md`
でコミット済みであることを確かめ、コミットされていなければ始めずに返す。

作業は `ba0918-codex-image` ブランチで行う。このブランチがまだなければ、`main` の最新（仕様と
計画のコミットを含む）から作って切り替える。

1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 の順に進める。

- Step 1 で入り口と `series.md` の読み込みを作る。`--series` を取る `process` と `check` がこれを使う。
- Step 2〜5 は後処理と検収を、単純なもの（1 枚の素材）から複雑なもの（シート）へ積む。
  Step 4 のアニメーションの後処理は、Step 3 のテンプレート画像と同じ行数・列数の規則を使う。
- Step 6 でプレビューを作り、スクリプトが仕上がる。
- Step 7 の `SKILL.md` は、スクリプトの引数と振る舞いが確定してから書く。
- Step 8 の README と Test 欄は、スキルの振る舞いが確定してから書く。
- Step 9 は全体の確認で、最後に行う。

コミットは各ステップで 1 つ作る。

- ファイルは 1 つずつ名前を指定してステージする。`git add -A` や `git add .` は使わない。
- メッセージは日本語で、`<type>: <件名>` の形（Conventional Commits）。件名と本文には変更の結果と
  理由を書く。「Step 2」のような計画の手順名や、作業の経緯は書かない。
- Step 9 で直すところがなければ、コミットは作らない。

## Test command

`uv run --with pytest --with pillow pytest tests/ba0918-codex-image`（仕様の `#テスト`）。
Step 8 で `PROJECT.md` の Test 欄に書くが、Step 1 からこのコマンドで回す。

## Step 1 — 入り口と series.md の読み込み

Purpose: 4 つのサブコマンドを持つ入り口を作り、`series.md` の定義の誤りを検出できるようにする。
Specification: [後処理の入り口](../spec/ba0918-codex-image.md#後処理の入り口)、
[シリーズ](../spec/ba0918-codex-image.md#シリーズ)、[テスト](../spec/ba0918-codex-image.md#テスト)。
Prerequisites: `ba0918-codex-image` ブランチ。`uv` が使えること。
May change: `skills/ba0918-codex-image/scripts/codex_image.py`、`tests/ba0918-codex-image/`。
Done when: T-01 の 2 つの定義（`canvas_dots` のない `kind: pixel`、`transparent` のない
`kind: illustration`）を `check` に渡すと、JSON を書かずに 0 以外で終わる。4 つのサブコマンドの
中身は以降のステップで作る。
Shown by: test — T-01（RED → GREEN → REFACTOR）。
Left to the implementer: テストのファイル分け、合成画像を作る補助の関数の形、定義の誤りのときの
標準エラーの文面。
Stop and hand back if: `uv run --with pillow` で Pillow が入らない環境しか用意できない。

## Step 2 — 1 枚の素材の後処理

Purpose: ドット絵、イラスト、Web 素材の 1 枚の元画像を、種類ごとの決まった手順で完成品にする。
Specification: [種類ごとの後処理](../spec/ba0918-codex-image.md#種類ごとの後処理)、
[シリーズ](../spec/ba0918-codex-image.md#シリーズ)。
Prerequisites: Step 1。
May change: `scripts/codex_image.py`、`tests/ba0918-codex-image/`。
Done when: T-02、T-03、T-04 と、T-08 の後半（`transparent: false` のイラストが中央から切り出されて
`size` ちょうどになる）が通る。
Shown by: test — T-02、T-03、T-04、T-08 の後半。
Left to the implementer: 縮小の方式（イラストと Web 素材。ドット絵はマス目の中心の色を拾う方式で、
中心の位置は Approach の 2 で決まっている）。
Stop and hand back if: なし。

## Step 3 — テンプレート画像

Purpose: 立ち絵を左上のコマに置いたテンプレート画像と、参照画像を渡すための拡大画像を作る。
Specification: [アニメーション](../spec/ba0918-codex-image.md#アニメーション)、
[シリーズ](../spec/ba0918-codex-image.md#シリーズ)。
Prerequisites: Step 1。
May change: `scripts/codex_image.py`、`tests/ba0918-codex-image/`。
Done when: T-09 が通る。`--frames` なしで、立ち絵を 1 ドット 10px に拡大した 1 枚の画像ができる。
Shown by: test — T-09、T-11（32×32 の立ち絵を `--frames` なしで渡すと 320×320 になり、各 10px 四方が
立ち絵の対応するドットの色になる）。
Left to the implementer: なし（1 ドット 10px は Approach の 2、4 列固定と左上の立ち絵は仕様で
決まっている）。
Stop and hand back if: なし。

## Step 4 — アニメーションのシートの後処理

Purpose: シートの元画像を、マス目で拾い、左上を元の立ち絵で上書きし、足元を揃えた完成品にする。
Specification: [アニメーション](../spec/ba0918-codex-image.md#アニメーション)、
[種類ごとの後処理](../spec/ba0918-codex-image.md#種類ごとの後処理)。
Prerequisites: Step 2、Step 3。
May change: `scripts/codex_image.py`、`tests/ba0918-codex-image/`。
Done when: T-05 が通る。`--no-ground` を付けると足元が揃わない。コマ数より後ろの空いたコマは、
元画像に何が描かれていても完成品では透明になる。
Shown by: test — T-05、T-12（`--no-ground` を付けると、足元の高さが元画像のまま残る）、T-13（6 コマの
シートで、7〜8 コマ目に描かれたものが完成品では透明になる）。
Left to the implementer: 足元の位置の求め方（不透明なドットの一番下の行を使う、など）。
Stop and hand back if: 足元を揃えると、コマの上端から体がはみ出すシートがありうる（はみ出した分の
扱いは仕様にない）。

## Step 5 — 検収

Purpose: 元画像を書き換えずに判定し、合否と理由を JSON で返す。
Specification: [検収と作り直し](../spec/ba0918-codex-image.md#検収と作り直し)。
Prerequisites: Step 2、Step 4（期待のマス目で拾う処理を使う）。
May change: `scripts/codex_image.py`、`tests/ba0918-codex-image/`。
Done when: T-06、T-07、T-08 の前半が通る。アニメーションで 1 ドットの大きさが `undetermined` の
とき、左上のコマの判定に応じて全体が `fail` か `undetermined` になる。
Shown by: test — T-06、T-07、T-08 の前半、T-14（一色で塗っただけのシートは 1 ドットの大きさを推定
できない。その左上のコマが立ち絵と大きく違えば `fail`、左上のコマだけ立ち絵を描いておけば
`undetermined` になる）。T-07 の「`check` の前後で画像が変わらない」は、元画像のファイルのバイトを
前後で比べて確かめる。
Left to the implementer: 1 ドットの大きさを推定する方法（試行ではエッジの位置の自己相関から周期を
求めた）。ただし、周期が見つからないときは `undetermined` を返すこと。`reasons` の文面。
Stop and hand back if: 推定の方法を変えても、合成画像で ±10% の境目の内と外を安定して分けられない。
T-14 の「推定できない画像」が、選んだ推定の方法で推定できてしまう（そのときは推定できない画像の
作り方を変えてよいが、変えても作れなければ返す）。

## Step 6 — プレビュー

Purpose: シートからプレビューの GIF を作れるようにする。
Specification: [アニメーション](../spec/ba0918-codex-image.md#アニメーション)、
[後処理の入り口](../spec/ba0918-codex-image.md#後処理の入り口)。
Prerequisites: Step 4。
May change: `scripts/codex_image.py`、`tests/ba0918-codex-image/`。
Done when: T-10 が通る。空いたコマは GIF のコマに入らない。
Shown by: test — T-10。
Left to the implementer: GIF の背景の扱い（透過か、見やすい色で塗るか）と拡大の倍率。
Stop and hand back if: なし。

## Step 7 — SKILL.md と references/prompts.md

Purpose: エージェントが従う手順を `SKILL.md` に、プロンプトの骨組みを `references/prompts.md` に書く。
Specification: [移植性と単体完結](../spec/ba0918-codex-image.md#移植性と単体完結)、
[実行してよい条件](../spec/ba0918-codex-image.md#実行してよい条件)、
[外部への送信](../spec/ba0918-codex-image.md#外部への送信)、
[前提の確認](../spec/ba0918-codex-image.md#前提の確認)、
[シリーズ](../spec/ba0918-codex-image.md#シリーズ)、
[新しいシリーズの始め方](../spec/ba0918-codex-image.md#新しいシリーズの始め方)、
[ざっくりした指示の清書](../spec/ba0918-codex-image.md#ざっくりした指示の清書)、
[種類ごとの後処理](../spec/ba0918-codex-image.md#種類ごとの後処理)、
[アニメーション](../spec/ba0918-codex-image.md#アニメーション)、
[検収と作り直し](../spec/ba0918-codex-image.md#検収と作り直し)、
[実行と後始末](../spec/ba0918-codex-image.md#実行と後始末)、
[後処理の入り口](../spec/ba0918-codex-image.md#後処理の入り口)、
[保存する状態と寿命](../spec/ba0918-codex-image.md#保存する状態と寿命)、
[人の判断点](../spec/ba0918-codex-image.md#人の判断点)。
Prerequisites: Step 6。
May change: `skills/ba0918-codex-image/SKILL.md`、`skills/ba0918-codex-image/references/prompts.md`。
Done when: `agentskills validate ./skills/ba0918-codex-image` が通る。`SKILL.md` が 500 行以内。
上に挙げた仕様の各節について、それを満たす `SKILL.md` または `references/prompts.md` の見出しを
対応表にし、1 つも欠けていない。`description` と本文に名指しの条件と OpenAI への送信がある。
Shown by: artifact — 対応表（仕様の節 → 指示文書の見出し）を、この手順のコミットの本文ではなく、
実装の結果の報告に載せる。続けて `agentskills validate ./skills/ba0918-codex-image` と
`wc -l skills/ba0918-codex-image/SKILL.md` を実行する。指示どおりにエージェントが動くかは、
受け入れのときの人手確認チェックリストで確かめる。
Left to the implementer: `SKILL.md` の中の見出しの細かい分け方、`description` の文面（1024 文字以内、
英語と日本語のトリガーの言葉を含める）、`references/prompts.md` の文面。
Stop and hand back if: `SKILL.md` が 500 行に収まらない。

`SKILL.md` に書く Codex の起動の形は次のとおり。作業フォルダーの中で実行する。

```
codex exec --sandbox workspace-write --skip-git-repo-check [--model <ユーザーの指定>] --image <画像 1 枚> - < prompt.md > codex.stdout 2> codex.stderr
```

`--image` は仕様の `-i` の長い書き方で、同じ指定である。この形（画像 1 枚のあとに `-`）は、
2026-09-28 の試行で、プロンプトが標準入力から届くことを確かめてある。

## Step 8 — README と Test 欄

Purpose: 人向けの使い方と注意を README に書き、テストのコマンドを `PROJECT.md` に書く。
Specification: [README](../spec/ba0918-codex-image.md#readme)、[テスト](../spec/ba0918-codex-image.md#テスト)。
Prerequisites: Step 7。
May change: `README.md`、`PROJECT.md`（Commands の表の Test 欄だけ）。
Done when: README のスキル一覧に 1 行あり、`### ba0918-codex-image の使い方と注意点` の節に仕様の
5 点がある。`series.md` の例は、Approach の 3 の書き方だけを使い、Step 1 のスクリプトで読める。
`PROJECT.md` の Test 欄に仕様のコマンドがある。
Shown by: artifact — `README.md` と `PROJECT.md` の差分を読んで確かめる。README の `series.md` の例を
一時ファイルに書き出し、`check` がそれを定義の誤りとして弾かないことも確かめる。
Left to the implementer: README の文面。既存の節（ba0918-codex-exec の使い方と注意点など）と同じ
調子で書く。
Stop and hand back if: なし。

## Step 9 — 全体の確認

Purpose: 自動テストとバリデータを通し、人手の確認に渡せる状態にする。
Specification: [自動テスト](../spec/ba0918-codex-image.md#自動テスト)、
[人手確認チェックリスト](../spec/ba0918-codex-image.md#人手確認チェックリスト)。
Prerequisites: Step 1〜8。
May change: Step 1〜8 と同じ範囲（直すところがあったときだけ）。
Done when: テストのコマンドで T-01〜T-14 が通る。バリデータが通る。`skills/ba0918-codex-image/` に
テストのファイルがない。本文に他のスキルへの依存と絶対パスがない。利用者の環境の値がないことは、
`rg` では網羅できないため、受け入れの C-01 で人が読んで確かめる。
Shown by: check — 1. `uv run --with pytest --with pillow pytest tests/ba0918-codex-image`
2. `agentskills validate ./skills/ba0918-codex-image` 3. `ls -R skills/ba0918-codex-image`
4. `rg -n '/home/|/Users/|ba0918-codex-exec' skills/ba0918-codex-image`（一致がないこと）。
Left to the implementer: なし。
Stop and hand back if: なし。

人手確認チェックリスト（C-01〜C-08）は、Codex で実際に生成して時間とお金がかかるため、実装の
中では行わない。結果の受け入れのときに人が行う。

## Verification map

| 仕様の節 | 確かめるステップ | 方法 |
|---|---|---|
| `#移植性と単体完結` | Step 7、Step 9 | バリデータ、`rg`、C-01 |
| `#実行してよい条件`、`#外部への送信`、`#前提の確認` | Step 7 | C-01〜C-04（人手） |
| `#シリーズ` | Step 1、Step 3、Step 7 | T-01、T-09、T-11、C-05、C-06（人手） |
| `#新しいシリーズの始め方`、`#ざっくりした指示の清書` | Step 7 | C-05、C-06（人手） |
| `#種類ごとの後処理` | Step 2 | T-02〜T-04、T-08 の後半 |
| `#アニメーション` | Step 3、Step 4、Step 6、Step 7 | T-05、T-09〜T-13、C-07（人手） |
| `#検収と作り直し` | Step 5 | T-06〜T-08、T-14、C-08（人手） |
| `#実行と後始末` | Step 7 | C-03（人手） |
| `#後処理の入り口`、`#テスト` | Step 1〜6、Step 9 | T-01〜T-14、Step 9 の check |
| `#保存する状態と寿命`、`#人の判断点` | Step 7 | 対応表、C-03、C-05〜C-08（人手） |
| `#README` | Step 8 | 差分を読む、C-01 |

## Left to the implementer

各ステップに書いたものに加えて、スクリプトの内部の構造（関数の分け方、名前）。テストが呼ぶのは
サブコマンドだけなので、どう分けても承認した振る舞いは変わらない。

## Stop conditions

次のときは手を止め、分かったことを添えて返す。

- 仕様にない振る舞いを決めないと進めない（入力の形、しきい値、エラーの扱い、残すファイル）。
- 各ステップの「Stop and hand back if」に当たる。
- 同じテストが、やり方を変えても 2 回続けて通らない。
- `main` への push、既存のスキルの変更など、この計画の範囲の外の操作が必要になる。

## Out of scope

- Codex で実際に画像を生成する確認（人手確認チェックリストで、受け入れのときに人が行う）。
- 仕様の `#作らないもの` に挙げたもの。
- 数値のしきい値（±10%、5%、128、60、2%）の調整。仕様どおりの値で実装する。
