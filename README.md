# skills

AI コーディングエージェント向けの、単体で使えるスキル集です。[Agent Skills 仕様](https://agentskills.io/specification) に準拠しているので、Claude Code、GitHub Copilot、Codex、Cursor など対応エージェントならそのまま使えます。

このリポジトリのスキルはどれも他のスキルや共有ファイルに依存していません。必要なものを 1 つだけ入れても、そのまま動きます。複数のスキルを組み合わせて回すワークフロー系のスキルは、別リポジトリ [claude-skills](https://github.com/ba0918/claude-skills) にあります。

スキルの名前にはすべて `ba0918-` が付いています。同じ名前のスキルが別の作者から配布されていても衝突しないようにするためです。

## インストール

GitHub CLI（`gh`）のスキル機能を使うのが一番簡単です。この機能はまだプレビュー段階で、コマンドの形が変わる可能性があります。

```sh
gh skill install ba0918/skills ba0918-handoff
```

インストール先のエージェントは対話式で選べます。スキル名を省略すると、スキルも対話式で選べます。

対話なしで入れたい場合はフラグで指定します。

```sh
gh skill install ba0918/skills ba0918-handoff --agent <エージェント名> --scope user
```

- `--agent` の値は `claude-code`、`amp`、`codex` など。対応一覧は `gh skill install --help` で確認できます
- `--scope user` はホームディレクトリ配下に入れ、どのプロジェクトでも使えるようにします。省略すると今いるリポジトリの中にだけ入ります

`gh` を使わない場合は、`skills/` 配下の該当フォルダを、お使いのエージェントがスキルを読む場所にそのままコピーしてください（Claude Code なら `~/.claude/skills/`）。

## スキル一覧

| スキル | 何をするか |
|---|---|
| [ba0918-handoff](skills/ba0918-handoff) | 作業中の文脈を `.agents/HANDOFF.md` に保存し、次のセッションで読み込んで続きから始める |
| [ba0918-refactor](skills/ba0918-refactor) | 指定した範囲の既存コードを、挙動を変えずに読みやすく整える。見つけたバグは直さず報告し、似たコードへの展開は同意を得てから行う |
| [ba0918-teacher](skills/ba0918-teacher) | 実作業でユーザーがコードを書き、レビューするのを、段階的なヒントと学習記録で支える |

`ba0918-handoff` を入れたら、`.gitignore` に `/.agents/HANDOFF.md` を 1 行足しておいてください。引き継ぎファイルは作業中の状態を書き出したもので、コミットする対象ではありません。足し忘れても保存時にスキルが同じ行を提案します。

細かい挙動は各スキルの `SKILL.md` に書いてあります。インストール前に `gh skill preview ba0918/skills <スキル名>` で読むこともできます。

### ba0918-teacher の使い方と注意点

`ba0918-teacher` を `enable [学習テーマ]` で呼ぶと、エージェントがユーザーの学習を支える teacher モードになります。`disable` で終了します。

- 学習記録はリポジトリの外、`~/.agents/ba0918-teacher/` に保存されます。
- 記録への書き込みのたびに許可を求められる場合は、この置き場所をエージェントの許可設定に足すと、毎回許可する手間を減らせます。
- `disable` 後も teacher のように振る舞うと感じたら、新しいセッションを始めればリセットされます。
- Claude Code では、インストールした `SKILL.md` の先頭にある `---` で囲まれた設定欄（frontmatter）に `disable-model-invocation: true` を足すと、ユーザーが呼んだときだけ動くことをより確実にできます。

## 開発者向け

スキル本文は英語で書かれています。エージェントが読むファイルは英語のほうが消費するトークンが少なく、Claude 以外のエージェントでも指示に従いやすいためです。人間向けの説明はこの README に集めています。

スキルを追加・変更したら、公式のバリデータで仕様に沿っているか確認してください。

```sh
agentskills validate ./skills/<スキル名>
```

`agentskills` コマンドは [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) が提供しています（`uv tool install skills-ref` で入ります）。

リポジトリの運用ルールは `PROJECT.md` にあります。

## ライセンス

[MIT License](LICENSE)
