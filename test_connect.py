from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:35054@localhost:5432/snoopdb"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("✅ データベースに接続できました！")
except Exception as e:
    print("❌ 接続エラー:", e)
    