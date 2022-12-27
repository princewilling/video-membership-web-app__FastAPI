import pathlib
import pytest
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import connection
from fastapi.testclient import TestClient
from cassandra.cqlengine.management import sync_table, drop_table


from app.playlists.models import Playlist
from app.users import schemas
from app.users.models import User
from app.videos.models import Video
from app.watch_events.models import WatchEvent

from .. import config
from ..main import app

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

SOURCE_DIR = BASE_DIR / 'ignored'
if not SOURCE_DIR.exists():
    SOURCE_DIR = BASE_DIR / 'decrypted'

settings = config.get_settings() 

ASTRADB_CONNECT_BUNDLE = BASE_DIR / SOURCE_DIR / "astradb_connect_test.zip" 
ASTRADB_CLIENT_ID = settings.db_client_id #'<<CLIENT ID>>'
ASTRADB_CLIENT_SECRET = settings.db_client_secret #'<<CLIENT SECRET>>'


@pytest.fixture
def override_get_session():
    cloud_config= {
            'secure_connect_bundle': ASTRADB_CONNECT_BUNDLE
    }
    auth_provider = PlainTextAuthProvider(ASTRADB_CLIENT_ID, ASTRADB_CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    connection.register_connection(str(session), session=session)
    connection.set_default_connection(str(session))
    return session

#app.dependency_overrides[get_session] = override_get_session

@pytest.fixture
def setup(override_get_session):
    try:    
        DB_SEESSION = override_get_session
        
        print("#######")
        drop_table(User)
        drop_table(Video) 
        drop_table(WatchEvent)
        drop_table(Playlist)
        
        
        print("*******")
        sync_table(User)
        sync_table(Video) 
        sync_table(WatchEvent)
        sync_table(Playlist) 
        
    except:
        DB_SEESSION.shutdown()

@pytest.fixture
def client(setup):
    yield TestClient(app)
    

@pytest.fixture
def test_user(client):
    user_data={"email": "local@gmail.com",  "password": "1234", "password_confirm":"1234"}
    
    new_user = schemas.UserSignupSchema(**user_data)
    assert new_user.email == user_data["email"]
    res = client.post("/signup/", data=user_data)
    
    assert res.status_code == 200
    new_user = (new_user.dict())
    return new_user
    