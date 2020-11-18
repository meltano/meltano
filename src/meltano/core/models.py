from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

SystemMetadata = MetaData()
SystemModel = declarative_base(metadata=SystemMetadata)
