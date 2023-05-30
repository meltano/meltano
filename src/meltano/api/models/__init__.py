from __future__ import annotations

try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    from meltano.api.meltano_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
