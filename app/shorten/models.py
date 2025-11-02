from datetime import datetime
from sqlalchemy import String, Column, DateTime, Integer
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class ShortUrlModel(Base):
    __tablename__ = "short_url"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), nullable=False)
    short_code = Column(String(6), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now,
        onupdate=datetime.now, nullable=False)
    access_count = Column(Integer, nullable=False, default=0)

    def to_dict(self, access_count: bool = False) -> dict:
        return {
            'id': self.id,
            'url': self.url,
            'shortCode': self.short_code,
            'createdAt': self.created_at.isoformat() + 'Z',
            'updatedAt': self.updated_at.isoformat() + 'Z',
            'accessCount': self.access_count
        }
