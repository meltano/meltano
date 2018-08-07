from meltano.common.service import MeltanoService
from .loader import PostgresLoader


MeltanoService.register_loader("com.meltano.load.postgres", PostgresLoader)
