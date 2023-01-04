import uuid
import pytest

from app.playlists.models import Playlist
from app.videos.extractors import extract_video_id
from app.videos.models import Video

# @pytest.mark.parametrize("title", [
#      ("Docker"),
#      ("Kubernetes"),
# ])
# def test_create_playlists(authorized_client, test_user2, title):
#     res = authorized_client.post("/playlists/create/", data={"title": title})
#     obj = Playlist.objects.all()
#     obj = obj.first()

    
#     assert title in res.text
#     assert obj.user_id == test_user2.user_id
#     assert res.status_code == 200
    

# def test_get_all_playlists(client, test_playlists):
#     res = client.get("/playlists/")
#     ls = list(test_playlists)
    
#     assert ls[0].title in res.text
#     assert ls[1].title in res.text
#     assert ls[2].title in res.text
#     assert res.status_code == 200

# def test_get_all_playlists_per_user(authorized_client, test_playlists):
#     res = authorized_client.get("/playlists/user_playlist/")
#     ls = list(test_playlists)
#     print(ls)
    
#     assert ls[0].title in res.text
#     assert ls[1].title not in res.text
#     assert ls[2].title in res.text
#     assert res.status_code == 200
    
def test_get_playlist_detail(client, test_playlists):
    res = client.get(f"/playlists/{test_playlists[0].db_id}")
    
    assert test_playlists[0].title in res.text
    assert res.status_code == 200
    
def test_get_non_existing_playlists_detail(client):
    res = client.get(f"/plalists/89665643234")
    
    assert "404 Error. Page Not Found" in res.text
    assert res.status_code == 404

def test_create_plalist_no_title(authorized_client, test_user2):
    data = {"title": ""}
    res = authorized_client.post("/playlists/create/", data=data)

    assert res.status_code == 422


def test_unauthorized_user_create_playlists(client, test_playlists):
    data = {"title": "Not Created"}
    res = client.post("playlists/create/", data=data)
    
    assert len(test_playlists) == len(Playlist.objects.all())
    assert "Do you need an account?" in res.text
    assert res.status_code == 200

@pytest.mark.parametrize("title, url", [
     ("Modern Graphical User Interfaces in Python", "https://www.youtube.com/watch?v=iM3kjbbKHQU"),
     ("BASH scripting will change your life", "https://www.youtube.com/watch?v=7qd5sqazD7k"),
])
def test_add_video_to_playlist(authorized_client, test_playlists, test_videos, title, url):
    authorized_client.headers = {**authorized_client.headers, "hx-request": "true"}
    data = {"title": title, "url": url}
    
    res = authorized_client.post(f"/playlists/{test_playlists[2].db_id}/add-video/", data=data)
    obj = Playlist.objects.all()[2]
    
    assert extract_video_id(url) in obj.host_ids
    assert title in res.text
    assert res.status_code == 200
    
    
@pytest.mark.parametrize("title, url", [
      ("Modern Graphical User Interfaces in Python", "https://www.youtube.com/watch?v=iM3kjbbKHQU"),
      ("BASH scripting will change your life", "https://www.youtube.com/watch?v=7qd5sqazD7k"),
])
def test_add_video_to_playlist_unauthorized_user(client, test_playlists, title, url):
    #client.headers = {**client.headers, "hx-request": "true"}
    data = {"title": title, "url": url}
    res = client.post(f"/playlists/{test_playlists[2].db_id}/add-video/", data=data)

    assert "Do you need an account?" in res.text
    assert res.status_code == 200
    
def test_remove_video_from_playlist(authorized_client, test_playlists, test_add_video_to_playlist_be_removed):
    authorized_client.headers = {**authorized_client.headers, "hx-request": "true"}
    host_id = test_add_video_to_playlist_be_removed

    data = {"index": 0}
    res = authorized_client.post(f"/playlists/{test_playlists[2].db_id}/{host_id}/delete/", data=data)

    assert res.text == "Deleted"
    assert res.status_code == 204
    
def test_remove_video_from_non_existing_playlist(authorized_client, test_playlists, test_add_video_to_playlist_be_removed):
    authorized_client.headers = {**authorized_client.headers, "hx-request": "true"}
    host_id = test_add_video_to_playlist_be_removed

    data = {"index": 0}
    res = authorized_client.post(f"/playlists/987654456789/{host_id}/delete/", data=data)
    
    assert "value is not a valid uuid" in res.text
    assert res.status_code == 422

def test_remove_video_from_non_existing_playlist_uuid(authorized_client, test_playlists, test_add_video_to_playlist_be_removed):
    authorized_client.headers = {**authorized_client.headers, "hx-request": "true"}
    
    host_id = test_add_video_to_playlist_be_removed
    db_id = uuid.UUID("a218bf46-89ee-11ed-abbc-bdc97c4d0bf0")
    
    data = {"index": 0}
    res = authorized_client.post(f"/playlists/{db_id}/{host_id}/delete/", data=data)
    
    assert res.text == "Error. Please reload the page."
    assert res.status_code == 404
    
def test_remove_video_from_playlist_unauthorized(test_playlists, test_add_video_to_playlist_be_removed, client):
    client.headers = {**client.headers, "hx-request": "true"}
    cookies = {"session_removed":"true"}
    client.cookies = cookies

    host_id = test_add_video_to_playlist_be_removed
    
    data = {"index": 0}
    res = client.post(f"/playlists/{test_playlists[2].db_id}/{host_id}/delete/", data=data)

    assert res.text == "Please login and continue"
    assert res.status_code == 401