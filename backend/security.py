# security.py (最終完成版)

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# ★ 認証コード生成に必要なライブラリ
import random
import string

# --- 設定 ---
# このSECRET_KEYは絶対に外部に漏らしてはいけません。
# 実際の運用では環境変数などから読み込むのがベストです。
SECRET_KEY = "your-very-secret-key-for-snoop-app"  # 必ずランダムで複雑な文字列に変更してください
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# パスワードハッシュ化の設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- 関数 ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """平文のパスワードとハッシュ化されたパスワードを比較する"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """パスワードをハッシュ化する"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """アクセストークンを生成する"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # 有効期限が指定されなかった場合のデフォルト値
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ★★★ この関数が認証コードを生成します ★★★
def create_verification_code(length: int = 6) -> str:
    """ランダムな数字の認証コードを生成する"""
    return "".join(random.choices(string.digits, k=length))

