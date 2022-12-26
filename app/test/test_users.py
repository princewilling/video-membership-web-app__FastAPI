import pytest

from app.users import schemas
    
def test_root(client):
    res = client.get("/")
    
    assert res.encoding == "utf-8"
    assert "Welcome to Video Membership" in res.text
    assert res.status_code == 200
    
def test_create_user(client):
    data = {"email": "local@gmail.com", "password": "1234", "password_confirm":"1234"}
    
    new_user = schemas.UserSignupSchema(**data)
    assert new_user.email == "local@gmail.com"
    res = client.post("/signup/", data=data, follow_redirects=True)
    assert res.encoding == "utf-8"
    assert "Do you need an account?" in res.text
    assert res.status_code == 200


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