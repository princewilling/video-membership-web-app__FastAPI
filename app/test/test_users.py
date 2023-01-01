import json
import pytest
from jose import jwt, ExpiredSignatureError


from .. import config
from app.users import schemas

settings = config.get_settings()

def test_root(client):
    res = client.get("/")
    
    assert res.encoding == "utf-8"
    assert "Welcome to Video Membership" in res.text
    assert "Recent Videos" in res.text
    assert res.status_code == 200
    
def test_create_user(client):
    data = {"email": "local@gmail.com", "password": "1234", "password_confirm":"1234"}
    
    new_user = schemas.UserSignupSchema(**data)
    assert new_user.email == data["email"]
    res = client.post("/signup/", data=data, follow_redirects=True)
    assert res.encoding == "utf-8"
    assert "Do you need an account?" in res.text
    assert res.status_code == 200
    
def test_login_user(client, test_user):
    test_user, obj = test_user
    obj = json.loads(obj.json())
    data={"email": test_user['email'], "password": test_user['password'].get_secret_value()}
    res = client.post("/login", data=data)
    
    login_res = json.loads(schemas.UserLoginSchema(**data).json())
    payload = jwt.decode(login_res["session_id"], settings.secret_key, algorithms=[settings.jwt_algorithm])

    id: str = payload.get("user_id")
    assert id == obj["user_id"]
    assert payload.get("role") == "admin"
    assert res.status_code == 200
    
    
@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', '1234', 400),
    ('local@gmail.com', 'wrongpassword', 400),
    ('wrongemail@gmail.com', 'wrongpassword', 400),
    (None, '1234', 422),
    ('local@gmail.com', None, 422)
])    
def test_incorret_login(client, test_user, email, password, status_code):
    res = client.post("/login", data={"email": email, "password":password })
    
    assert res.status_code == status_code