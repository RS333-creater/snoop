# Snoop - 習慣トラッカーアプリ

## 概要
Snoopは、ユーザーが自身の習慣を管理し、進捗を記録することで生活習慣の改善をサポートするアプリケーションです。目標を設定し、毎日の進捗を記録して、視覚的に確認できます。また、通知機能により、習慣を継続するためのリマインダーも提供します。

## 特徴
- **習慣管理**: 習慣の追加、削除、編集が可能。
- **進捗の記録**: 毎日の習慣達成状況を記録し、可視化。
- **カレンダー表示**: 各習慣の進捗状況をカレンダー形式で確認。
- **通知機能**: 習慣の進捗を忘れないようにリマインダー通知を送信。
- **目標設定**: ユーザーが習慣に対して目標を設定し、その達成度を追跡。

## 技術スタック
- **フロントエンド**: React.js
- **バックエンド**: FastAPI 
- **データベース**: PostgreSQL 
- **通知機能**: Firebase Cloud Messaging / Push Notification API

## インストール手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/RS333-creater/snoop.git
cd snoop
```

### 2. フロントエンドのセットアップ
```bash
npm install
npm start
```

### 3. バックエンドのセットアップ
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
バックエンドは [http://127.0.0.1:8000](http://127.0.0.1:8000) で動作します。

### 4. データベースのセットアップ
```bash
python manage.py migrate
```

## 使用方法
1. ユーザー登録画面で新しいアカウントを作成。
2. ホーム画面で習慣を追加し、進捗を記録。
3. 習慣の詳細ページでカレンダーやグラフを使って進捗を確認。
4. 設定画面で通知機能を有効にし、リマインダーを受け取る。

## 今後の機能追加予定
- **習慣の共有機能**: ユーザー同士で習慣の進捗を共有。
- **目標達成の報酬システム**: 目標達成時に報酬を提供。
- **ソーシャルメディア連携**: 達成状況をSNSで共有。

## 貢献方法
1. リポジトリをフォーク。
2. 新しいブランチを作成（`git checkout -b feature-name`）。
3. 変更を加え、コミット（`git commit -m 'Add new feature'`）。
4. プルリクエストを送信。

## ライセンス
このプロジェクトは **MITライセンス** の下で公開されています。

