import pathlib
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import connection

from .. import config

BASE_DIR = pathlib.Path(__file__).resolve().parent  

SOURCE_DIR = BASE_DIR / 'ignored'
if not SOURCE_DIR.exists():
    SOURCE_DIR = BASE_DIR / 'decrypted'

settings = config.get_settings() 

ASTRADB_CONNECT_BUNDLE = BASE_DIR / SOURCE_DIR / "astradb_connect_test.zip" 
ASTRADB_CLIENT_ID = settings.db_client_id_test #'<<CLIENT ID>>'
ASTRADB_CLIENT_SECRET = settings.db_client_secret_test #'<<CLIENT SECRET>>'

def get_session():
    cloud_config= {
            'secure_connect_bundle': ASTRADB_CONNECT_BUNDLE
    }
    auth_provider = PlainTextAuthProvider(ASTRADB_CLIENT_ID, ASTRADB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    connection.register_connection(str(session), session=session)
    connection.set_default_connection(str(session))
    return session

def test_read_items():
    with TestClient(app) as client:
        response = client.get("/items/foo")
        assert response.status_code == 200
        assert response.json() == {"name": "Fighters"}
