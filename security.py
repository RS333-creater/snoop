# security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# --- 設定 ---
# このSECRET_KEYは絶対に外部に漏らしてはいけません。
# 実際の運用では環境変数などから読み込むのがベストです。
SECRET_KEY = "your-very-secret-key"  # 必ずランダムで複雑な文字列に変更してください
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# crud.pyからここに移動させます
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 関数 ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """平文のパスワードとハッシュ化されたパスワードを比較する"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """アクセストークンを生成する"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

