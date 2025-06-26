# notification_sender.py

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from firebase_admin import messaging

import crud
from database import SessionLocal

def send_scheduled_notifications():
    """
    現在の時刻に合致する通知設定をデータベースから探し、
    FCMプッシュ通知を送信する関数。
    スケジューラによって定期的に実行される。
    """
    print(f"[{datetime.now()}] Running notification check...")

    # バックグラウンドタスクでは、このように手動でDBセッションを管理する
    db: Session = SessionLocal()

    try:
        # 現在の時刻（時:分）を取得
        # サーバーのタイムゾーンに依存しないようにUTCで比較するのが望ましいが、
        # 簡単のため、サーバーのローカル時刻で比較する
        current_time = datetime.now().strftime("%H:%M")

        # 現在の時刻に設定されている、有効な通知を取得
        notifications_to_send = crud.get_notifications_by_time(db, time_str=current_time)

        if not notifications_to_send:
            print(f"No notifications to send at {current_time}.")
            return

        print(f"Found {len(notifications_to_send)} notifications to send at {current_time}.")

        for notif in notifications_to_send:
            # ユーザーがFCMトークンを持っているか確認
            if notif.user and notif.user.fcm_token:
                print(f"  - Sending notification for habit '{notif.habit.name}' to user {notif.user.id}")

                # FCMメッセージの作成
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=f"今日の習慣リマインダー！",
                        body=f"「{notif.habit.name}」の時間ですよ！頑張りましょう！"
                    ),
                    token=notif.user.fcm_token,
                )

                # メッセージの送信
                try:
                    response = messaging.send(message)
                    print(f"    Successfully sent message: {response}")
                except Exception as e:
                    print(f"    Error sending message for user {notif.user.id}: {e}")
            else:
                print(f"  - Skipping user {notif.user.id}: No FCM token found.")

    finally:
        # 忘れずにDBセッションを閉じる
        db.close()