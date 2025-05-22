from database import Base, engine
from models import User

# テーブルを作成する
Base.metadata.create_all(bind=engine)
