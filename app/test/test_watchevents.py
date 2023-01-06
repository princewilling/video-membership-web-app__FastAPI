import pytest
from app.watch_events.models import WatchEvent
from app.watch_events.schemas import WatchEventSchema

def test_watchevent_uncomplete(authorized_client, test_videos, test_user2):
    data = {"host_id": test_videos[0].host_id, "start_time": 0.0, "end_time": 1.50, "duration":10.58 , "complete": False}
    res = authorized_client.post("/api/events/watch", json=data)

    created_event = WatchEventSchema(**res.json())
    assert created_event.host_id == data["host_id"]
    assert created_event.complete == data["complete"]
    
    resume_time = WatchEvent.get_resume_time(test_videos[0].host_id, test_user2.user_id)
    assert resume_time == data["end_time"]
    
    
def test_create_watchevent_complete(authorized_client, test_videos, test_user2):
    data = {"host_id": test_videos[0].host_id, "start_time": 05.10, "end_time": 10.50, "duration":10.58 , "complete": True}
    res = authorized_client.post("/api/events/watch", json=data)

    created_event = WatchEventSchema(**res.json())
    assert created_event.host_id == data["host_id"]
    assert created_event.complete == data["complete"]
    
    resume_time = WatchEvent.get_resume_time(test_videos[0].host_id, test_user2.user_id)
    assert resume_time == 0.0


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