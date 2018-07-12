from meltano import MeltanoService
from .loader import PostgreSQLLoader


MeltanoService.register_loader("com.meltano.load.postgresql", PostgreSQLLoader)
