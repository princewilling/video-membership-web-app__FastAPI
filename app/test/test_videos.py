import pytest

from app.videos.models import Video
from app.videos.schemas import VideoEditSchema

def test_get_all_videos(client, test_videos):
    res = client.get("/videos/")
    ls = list(test_videos)
    
    assert ls[0].title in res.text
    assert ls[1].title in res.text
    assert ls[2].title in res.text
    assert res.status_code == 200
    

def test_get_one_video(client, test_videos):
    res = client.get(f"/videos/{test_videos[0].host_id}")
    
    assert test_videos[0].title in res.text
    assert test_videos[0].host_id in res.text
    assert res.status_code == 200

def test_get_one_video_not_exist(client):
    res = client.get(f"/videos/89665643234")
    
    assert "404 Error. Page Not Found" in res.text
    assert res.status_code == 404


@pytest.mark.parametrize("title, url", [
     ("System Design: How to store passwords in the database?", "https://www.youtube.com/watch?v=zt8Cocdy15c"),
     ("BASH scripting will change your life", "https://www.youtube.com/watch?v=7qd5sqazD7k"),
])
def test_create_videos(authorized_client, test_user2, title, url):
    res = authorized_client.post("/videos/create/", data={"title": title, "url": url})
    obj, _ = Video.get_or_create(url)
    
    assert title in res.text
    assert obj.host_service in url
    assert obj.host_id in url
    assert obj.user_id == test_user2.user_id
    assert res.status_code == 200

def test_create_video_no_title_no_url(authorized_client, test_user2):
    data = {"title": "", "url": ""}
    res = authorized_client.post("/videos/create/", data=data)

    #obj, _ = Video.get_or_create(data["url"])
    
    # assert obj.host_service in data["url"]
    # assert obj.host_id in data["url"]
    # assert obj.user_id == test_user2.user_id
    assert res.status_code == 422

def test_unauthorized_user_delete_video(client, test_videos):
    data = {"title": f"{test_videos[2].title}", "url":f"{test_videos[2].url}", "delete":True}
    res = client.post(f"/videos/{test_videos[2].host_id}/hx-edit", data=data)
    
    assert len(test_videos) == len(Video.objects.all())
    assert "Do you need an account?" in res.text
    assert res.status_code == 200

def test_delete_video_success(authorized_client, test_videos):
    authorized_client.headers = {
         **authorized_client.headers,
         "hx-request": "true"
         }
    
    data = {"title": f"{test_videos[1].title}", "url":f"{test_videos[1].url}", "delete":True}
    res = authorized_client.post(f"/videos/{test_videos[1].host_id}/hx-edit", data=data)

    assert len(test_videos) != len(Video.objects.all())
    assert "Item Deleted" in res.text
    assert res.status_code == 204


def test_delete_video_non_exist(authorized_client):
    authorized_client.headers = {
         **authorized_client.headers,
         "hx-request": "true"
         }
    data = {"title": "Non existing title", "url":"8000000", "delete":True}
    res = authorized_client.post(f"/videos/8000000/hx-edit", data=data)
    
    assert "Not found, please try again." in res.text
    assert res.status_code == 404
    
def test_update_video_succuess(authorized_client, test_videos):
    authorized_client.headers = {
         **authorized_client.headers,
         "hx-request": "true"
         }
    data = {"title": f"{test_videos[0].title},  Updated!!!", 
            "url": f"{test_videos[0].url}"
            }
    
    res = authorized_client.post(f"/videos/{test_videos[0].host_id}/hx-edit", data=data)
    updated_video = VideoEditSchema(**data)

    assert updated_video.title == data['title']
    assert updated_video.title in res.text
    assert updated_video.url == data['url']
    assert res.status_code == 200

def test_unauthorized_user_update_video(client, test_videos):    
    data = {"title": f"{test_videos[2].title}, Update!!!", "url":f"{test_videos[2].url}", "delete":True}
    res = client.post(f"/videos/{test_videos[2].host_id}/hx-edit", data=data)
    
    assert "Do you need an account?" in res.text
    assert res.status_code == 200

def test_update_video_non_exist(authorized_client):
    authorized_client.headers = {
         **authorized_client.headers,
         "hx-request": "true"
         }
    
    data = {"title": "updated title", "url": "updatd url",}
    res = authorized_client.post(f"/videos/8000000/hx-edit", data=data)
    
    assert "Not found, please try again." in res.text
    assert res.status_code == 404

def test_update_other_user_video(authorized_client, test_videos):
    authorized_client.headers = {
         **authorized_client.headers,
         "hx-request": "true"
    }
    data = {
        "title": f"{test_videos[2].title},  Updated!!!", 
        "url": f"{test_videos[2].url}",
        "delete": True
        }
    res = authorized_client.post(f"/videos/{test_videos[2].host_id}/hx-edit", data=data)
    
    assert "Not authorized to perform requested action" in res.text
    assert res.status_code == 403