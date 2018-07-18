from sqlalchemy import create_engine, MetaData
from models.projects import Settings

connections = {}

def add_connections():
  print('hello')
  #   current_connections = Settings.query.first().settings['connections']
  # for connection in current_connections:
  #   connection_name = connection['name']
  #   if connection_name not in connections:
  #     this_connection = {}
  #     if connection['dialect'] == 'postgresql':
  #       connection_url = 'postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}'.format(user=connection['username'],pw=connection['password'],host=connection['host'],port=connection['port'], db=connection['database'])
  #       this_connection['connection_url'] = connection_url
  #       this_connection['engine'] = create_engine(this_connection['connection_url'])
  #       meta = MetaData()
  #       meta.reflect(bind=this_connection['engine'])
  #       this_connection['meta'] = meta
  #       print(this_connection['meta'].tables)
  #     connections[connection_name] = this_connection