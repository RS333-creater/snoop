import firebase_admin
from firebase_admin import credentials

SERVICE_ACCOUNT_FILE = 'firebase-service-account.json'

try:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")