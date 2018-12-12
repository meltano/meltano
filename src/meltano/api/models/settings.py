from .base import Base
from ..app import db
from sqlalchemy.ext.mutable import MutableDict


class Settings(Base):
    __tablename__ = "setting"
    settings = db.Column(
        MutableDict.as_mutable(db.JSON()), nullable=False, default={"connections": []}
    )

    def serializable(self):
        return {"settings": self.settings}

    def __repr__(self):
        return f"<Settings id: {self.id}>"
