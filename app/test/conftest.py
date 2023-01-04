import pathlib
from pydantic import BaseModel, EmailStr
import pytest
import json
import uuid
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import connection
from fastapi.testclient import TestClient
from cassandra.cqlengine.management import sync_table, drop_table


from app.playlists.models import Playlist
from app.playlists.schemas import PlaylistCreateSchema
from app.users.auth import login
from app.users.models import User
from app.users.schemas import UserSignupSchema
from app.videos.models import Video
from app.videos.schemas import VidoeCreateSchema
from app.watch_events.models import WatchEvent

from .. import config
from ..main import app

class UserOut(BaseModel):
    user_id: uuid.UUID

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

DB_SEESSION = None

@pytest.fixture
def setup(override_get_session):
    try:    
        global DB_SEESSION 
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
    
    new_user = UserSignupSchema(**user_data)
    assert new_user.email == user_data["email"]
    res = client.post("/signup/", data=user_data)
    
    assert res.status_code == 200
    obj = User.objects.get(email=new_user.email)
    obj = UserOut(**dict(obj))
    #obj = json.loads(obj.json())
    new_user = (new_user.dict())
    return new_user, obj

@pytest.fixture
def test_user2(client):
    user_data = {"email": "next@gmail.com", "password": "1234", "password_confirm":"1234"}
    
    new_user = UserSignupSchema(**user_data)
    assert new_user.email == user_data["email"]
    res = client.post("/signup/", data=user_data)
    
    assert res.status_code == 200
    obj = User.objects.get(email=new_user.email)
    obj = UserOut(**dict(obj))
    #obj = json.loads(obj.json())
    return obj

@pytest.fixture
def token(test_user2):
    return login(test_user2, expires=60)

@pytest.fixture
def authorized_client(client, token):
    cookies = {"session_id":token}
    client.cookies = cookies
    
    return client

@pytest.fixture
def test_videos(test_user, test_user2):
    _, test_user = test_user 
    videos_data = [{
        "title": "5 Unique Python Project Ideas for Your Resume | Python Projects for Beginners to Advanced",
        "url": "https://www.youtube.com/watch?v=6erwYj4T86c",
        "user_id": test_user.user_id
    }, {
        "title": "Modern Graphical User Interfaces in Python",
        "url": "https://www.youtube.com/watch?v=iM3kjbbKHQU",
        "user_id": test_user2.user_id
    }, {
        "title": "You Are Going To Like These New Features In Python 3.11",
        "url": "https://www.youtube.com/watch?v=b3_THpKM4EU",
        "user_id": test_user2.user_id
    }]

    def create_video_schema(video):
        return VidoeCreateSchema(**video)

    video_map = map(create_video_schema, videos_data)
    videos = list(video_map)

    videos = Video.objects.all()
    assert len(videos) == len(videos_data)
    return videos

@pytest.fixture
def test_playlists(test_user, test_user2):
    _, test_user = test_user 
    playlists_data = [{
        "title": "MongoDB",
        "user_id": test_user.user_id
    }, {
        "title": "PostgresQL",
        "user_id": test_user2.user_id
    }, {
        "title": "Apache Cassandra",
        "user_id": test_user2.user_id
    }]

    def create_playlist_schema(playlist):
        obj = PlaylistCreateSchema(**playlist)
        obj = Playlist.objects.create(title=obj.title, user_id=obj.user_id)
        return obj
        
    playlist_map = map(create_playlist_schema, playlists_data)
    playlists = list(playlist_map)

    playlists = Playlist.objects.all()
    assert len(playlists) == len(playlists_data)
    return playlists


@pytest.fixture
def test_add_video_to_playlist_be_removed(authorized_client, test_playlists):
    authorized_client.headers = {**authorized_client.headers, "hx-request": "true"}
    data = {"title": "BASH scripting will change your life", "url": "https://www.youtube.com/watch?v=7qd5sqazD7k"}
    
    res = authorized_client.post(f"/playlists/{test_playlists[2].db_id}/add-video/", data=data)
    obj = Playlist.objects.all()[2]
    
    obj = obj.host_ids
    return obj[0]
    

    