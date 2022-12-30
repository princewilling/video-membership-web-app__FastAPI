import pytest

from app.videos.models import Video

def test_get_all_videos(client, test_videos):
    res = client.get("/videos/")
    ls = list(test_videos)
    
    assert ls[0].title in res.text
    assert ls[1].title in res.text
    assert ls[2].title in res.text
    assert ls[3].title in res.text
    assert res.status_code == 200
    

def test_get_one_video(client, test_videos):
    res = client.get(f"/videos/{test_videos[0].host_id}")
    
    assert test_videos[0].title in res.text
    assert test_videos[0].host_id in res.text
    assert res.status_code == 200

def test_get_one_video_not_exist(client, test_videos):
    res = client.get(f"/videos/89665643234")
    
    assert "404 Error. Page Not Found" in res.text
    assert res.status_code == 404


@pytest.mark.parametrize("title, url", [
     ("System Design: How to store passwords in the database?", "https://www.youtube.com/watch?v=zt8Cocdy15c"),
     ("BASH scripting will change your life", "https://www.youtube.com/watch?v=7qd5sqazD7k"),
])
def test_create_videos(authorized_client, test_user2, test_videos, title, url):
    res = authorized_client.post("/videos/create/", data={"title": title, "url": url})
    obj, _ = Video.get_or_create(url)
    
    assert title in res.text
    assert obj.host_service in url
    assert obj.host_id in url
    assert obj.user_id == test_user2.user_id
    assert res.status_code == 200

def test_create_video_no_title(authorized_client, test_user2):
    data = {"title": "", "url": "https://www.youtube.com/watch?v=7pT0oviBZk0"}
    res = authorized_client.post("/videos/create/", data=data)
    obj, _ = Video.get_or_create(data["url"])
    
    assert obj.host_service in data["url"]
    assert obj.host_id in data["url"]
    assert obj.user_id == test_user2.user_id
    assert res.status_code == 200

def test_unauthorized_user_delete_video(client, test_user2, test_videos):
    data = {"title": f"{test_videos[2].title}", "url":f"{test_videos[2].url}", "delete":True}
    res = client.post(f"/videos/{test_videos[2].host_id}/hx-edit", data=data)
    
    assert len(test_videos) == len(Video.objects.all())
    assert "Do you need an account?" in res.text
    assert res.status_code == 200

def test_delete_post_success(authorized_client, test_user2, test_videos):
    authorized_client.headers = {
         **authorized_client.headers,
         "hx-request": "true"
         }
    
    data = {"title": f"{test_videos[2].title}", "url":f"{test_videos[2].url}", "delete":True}
    res = authorized_client.post(f"/videos/{test_videos[2].host_id}/hx-edit", data=data)

    assert len(test_videos) != len(Video.objects.all())
    assert "Item Deleted" in res.text
    assert res.status_code == 204


def test_delete_post_non_exist(authorized_client, test_videos):
    authorized_client.headers = {
         **authorized_client.headers,
         "hx-request": "true"
         }
    data = {"title": "Non existing title", "url":"8000000", "delete":True}
    res = authorized_client.post(f"/videos/8000000/hx-edit", data=data)
    
    assert "Not found, please try again." in res.text
    assert res.status_code == 404

def test_random():
    assert 44==44



"""['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__',
'__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__',
'__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__',
'__subclasshook__', '__weakref__', '_content', '_decoder', '_elapsed', '_get_content_decoder', '_num_bytes_downloaded',
'_prepare', '_request', 'aclose', 'aiter_bytes', 'aiter_lines', 'aiter_raw', 'aiter_text', 'aread', 'charset_encoding',
'close', 'content', 'cookies', 'default_encoding', 'elapsed', 'encoding', 'extensions', 'has_redirect_location',
'headers', 'history', 'http_version', 'is_client_error', 'is_closed', 'is_error', 'is_informational', 'is_redirect',
'is_server_error', 'is_stream_consumed', 'is_success', 'iter_bytes', 'iter_lines', 'iter_raw', 'iter_text',
'json', 'links', 'next_request', 'num_bytes_downloaded', 'raise_for_status', 'read', 'reason_phrase', 'request',
'status_code', 'stream', 'text', 'url']"""