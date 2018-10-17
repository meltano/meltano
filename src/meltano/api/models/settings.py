from .base import Base
from ..app import db


class Settings(Base):
    __tablename__ = "setting"
    settings = db.Column(db.JSON(), nullable=False, default={"connections": []})

    def serializable(self):
        return {"settings": self.settings}

    def __repr__(self):
        return f"<Settings for {self.project} id: {self.id}>"
