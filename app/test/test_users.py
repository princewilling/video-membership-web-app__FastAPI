import pytest

from app import db
from app.users.models import User

@pytest.fixture(scope='module')
def setup():
    #setup
    session = db.get_session()
    yield session
    
    #teardown
    q = User.objects.filter(email='test@test.com')
    if q.count() != 0:
        q.delete()
    session.shutdown()

def test_create_user(setup):
    User.create_user(email="test@test.com", password="1234")

def test_duplicate_user(setup):
    with pytest.raises(Exception):
        User.create_user(email="test@test.com", password="12323454")
        

def test_invalid_email(setup):
    with pytest.raises(Exception):
        User.create_user(email="test#tes", password="123454")
        
        
