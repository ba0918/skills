# Project Context

## What this is

単体で完結するユーティリティスキルを集めたリポジトリ。
各スキルは相互依存を持たず、`gh skills` 経由で個別にインストールできる。

ワークフロー統合やメタスキルは [claude-skills](https://github.com/ba0918/claude-skills) に置く。
このリポジトリは「つまみ食い」前提の standalone スキル棚として棲み分ける。

## Stack and layout

- `skills/` — スキル本体。各スキルは `SKILL.md` を持ち、必要に応じて仕様準拠の任意ディレクトリ（`references/`, `scripts/`, `assets/`）を含む

## Commands

| Purpose | Command |
|---|---|
| Install | |
| Build | |
| Test | |
| Lint | `agentskills validate ./skills/<name>` |
| Run locally | |

`agentskills` は公式バリデータ [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) が提供する CLI。`uv tool install skills-ref` で導入済み。

## Conventions specific to this project

### 言語方針

- `skills/` 以下の配布物（SKILL.md、references 等）は **英語** で書く。
  - 理由: description は毎セッション全スキル分ロードされ、本文は発火ごとにロードされるため英語の方がトークン効率が良い。加えて公開配布物として読者層が広がり、Claude 以外のエージェントでも指示追従が安定する。
- 翻訳版（SKILL-ja.md 等）は作らない。仕様に locale の仕組みはなくエージェントは読まないため、乖離コストだけが残る。
- 人間向けの日本語説明はリポジトリの README に集約する。
- リポジトリ運用ドキュメント（この PROJECT.md、README 等）は日本語でよい。

### スキル運用

- [agentskills.io の仕様](https://agentskills.io/specification) に準拠する。特にハマりやすい制約:
  - `name` は親ディレクトリ名と完全一致。小文字英数とハイフンのみ、64文字以内、先頭/末尾/連続ハイフン禁止
  - `description` は1024文字以内。「何をするか」+「いつ使うか」+ 発火のトリガーになる具体的キーワードを含める
  - SKILL.md 本文は500行以内を目安にし、詳細は `references/` へ分離する（progressive disclosure）
  - ファイル参照はスキルルートからの相対パスで、SKILL.md から1階層まで
- 各スキルは単体で完結すること。他スキルへの依存・共有契約は持たない。
- スキル本文はプラットフォーム非依存の自然言語で記述する。
  - NG: 固有のツール API 名、固有のモデル名、特定 CLI だけで通じる呼び出し形式
  - OK: 「シェルコマンドを実行する」「ファイルを読む」「ファイルを編集する」「サブエージェントに委譲する」

### 編集ルール

- 指示ファイルの役割分担:
  - `CLAUDE.md` は `@AGENTS.md` の1行だけを持つ薄いラッパー。プロジェクト指示を直接書かない。
  - `AGENTS.md` はインストール済みルールスキルから生成されるルーター。手で編集せず、スキルの追加・削除時に scaffold で再生成する。
  - プロジェクト固有の指示はこの `PROJECT.md` に書く。
- スキルを追加・変更したら `agentskills validate ./skills/<name>` を通してから完了とする。

## Constraints

## Glossary
