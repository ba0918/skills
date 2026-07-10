# AGENTS.md

This file is the shared project instruction source for Claude Code, Codex CLI, and other agents.
`CLAUDE.md` must stay a thin wrapper that imports this file with `@AGENTS.md`.

## プロジェクト概要

単体で完結するユーティリティスキルを集めたリポジトリ。
各スキルは相互依存を持たず、`gh skills` 経由で個別にインストールできる。

ワークフロー統合やメタスキルは [claude-skills](https://github.com/ba0918/claude-skills) に置く。
このリポジトリは「つまみ食い」前提の standalone スキル棚として棲み分ける。

## 主要構成

- `skills/` — スキル本体。各スキルは `SKILL.md` を持ち、必要に応じて `references/` を含む

## スキル運用

- 各スキルは単体で完結すること。他スキルへの依存・共有契約は持たない。
- スキル本文はプラットフォーム非依存の自然言語で記述する。
  - NG: 固有のツール API 名、固有のモデル名、特定 CLI だけで通じる呼び出し形式
  - OK: 「シェルコマンドを実行する」「ファイルを読む」「ファイルを編集する」「サブエージェントに委譲する」

## 編集ルール

- `CLAUDE.md` へ直接プロジェクト指示を追加しない。共通指示が必要ならこの `AGENTS.md` を更新する。
