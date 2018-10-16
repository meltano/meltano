from sqlalchemy import create_engine


class ExternalConnector:
    def __init__(self):
        self.connections = {}

    def add_connections(self, connections):
        print("adding connections...")
        for connection in connections:
            connection_name = connection["name"]
            if connection_name not in connections:
                this_connection = {}
                if connection["dialect"] == "postgresql":
                    psql_params = ["username", "password", "host", "port", "database"]
                    user, pw, host, port, db = [
                        connection[param] for param in psql_params
                    ]
                    connection_url = (
                        f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}"
                    )
                    this_connection["connection_url"] = connection_url
                    this_connection["engine"] = create_engine(
                        this_connection["connection_url"]
                    )
        return self.connections
