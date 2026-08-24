# Agent Instructions

## Core

- 依頼された目的に沿って作業し、範囲を不必要に広げない。
- 確認済みの事実・推測・未検証の事項を区別する。
- 変更後は、その変更に適した方法で実際に検証する。
- 不可逆・破壊的・外部から見える操作は、承認なしに実行しない。
- プロジェクト固有の指示がここより具体的な場合は、そちらを適用する。

## Rule Routing

| When | Read |
|---|---|
| Always | ba0918-design, ba0918-placement, ba0918-readability, ba0918-secrets |
| commit | ba0918-commit |
| delegate | ba0918-delegation |
| design | ba0918-reuse |
| implement | ba0918-tdd |
| release | ba0918-release |
| review | ba0918-verification |

各ルールはスキル名で参照する。該当するルールをすべて読んでから、そのルールが規定する作業を始める。

## Project Context

このリポジトリが何か、ビルドとテストの方法、ここだけに適用される規約といったプロジェクト固有の文脈は `PROJECT.md` にある。変更を加える前に読むこと。
