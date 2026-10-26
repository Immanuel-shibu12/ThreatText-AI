"""
ThreatText AI - MongoDB Audit & Scan History Logger
Persists email threat scans and explainability reviews to MongoDB.
Gracefully operates offline if MongoDB is inactive.
"""

import datetime
from typing import Dict, Any, Optional

try:
    import pymongo
    HAS_PYMONGO = True
except ImportError:
    HAS_PYMONGO = False

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "threattext_db"
COLLECTION_NAME = "email_scans"

class ThreatDatabase:
    def __init__(self, uri: str = MONGO_URI):
        self.client = None
        self.db = None
        self.collection = None
        self.is_connected = False
        self._connect(uri)

    def _connect(self, uri: str):
        if not HAS_PYMONGO:
            return
        try:
            self.client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=1000)
            # Test connection
            self.client.server_info()
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]
            self.is_connected = True
            print(f"[ThreatText AI] MongoDB connected successfully to '{DB_NAME}.{COLLECTION_NAME}'.")
        except Exception as e:
            self.is_connected = False
            # Silent fallback: offline mode
            pass

    def log_scan(
        self,
        subject: str,
        body_snippet: str,
        prediction: str,
        risk_score_pct: float,
        threat_level: str,
        model_used: str,
        top_phishing_triggers: list
    ) -> Optional[str]:
        """Saves a scan review record to MongoDB."""
        if not self.is_connected or self.collection is None:
            return None

        record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "subject": subject,
            "body_snippet": body_snippet[:300],
            "prediction": prediction,
            "risk_score_pct": risk_score_pct,
            "threat_level": threat_level,
            "model_used": model_used,
            "top_triggers": [t.get("phrase", "") for t in top_phishing_triggers[:5]],
            "created_at": datetime.datetime.utcnow()
        }

        try:
            res = self.collection.insert_one(record)
            return str(res.inserted_id)
        except Exception:
            return None

    def get_recent_scans(self, limit: int = 10) -> list:
        if not self.is_connected or self.collection is None:
            return []
        try:
            cursor = self.collection.find().sort("_id", -1).limit(limit)
            out = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                if "created_at" in doc and hasattr(doc["created_at"], "isoformat"):
                    doc["created_at"] = doc["created_at"].isoformat()
                out.append(doc)
            return out
        except Exception:
            return []

# Singleton instance
db_logger = ThreatDatabase()

if __name__ == "__main__":
    print("Database connected:", db_logger.is_connected)
    if db_logger.is_connected:
        doc_id = db_logger.log_scan(
            subject="Test Verification",
            body_snippet="Urgent bank account notice...",
            prediction="Phishing",
            risk_score_pct=92.5,
            threat_level="Critical Threat",
            model_used="logistic_regression",
            top_phishing_triggers=[{"phrase": "urgent"}, {"phrase": "account"}]
        )
        print("Logged test scan with ID:", doc_id)
