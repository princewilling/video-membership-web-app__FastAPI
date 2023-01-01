from datetime import datetime
import uuid
import pytz
from app.config import get_settings
from app.users.exceptions import InvalidUserIDException
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

from app.users.models import User
from app.shortcuts import templates
from .extractors import extract_video_id
from .exceptions import InvalidYouTubeVideoURLException, VideoAlreadyAddedException
from cassandra.cqlengine.query import (DoesNotExist, MultipleObjectsReturned)

settings = get_settings()
  
class Video(Model):
    __keyspace__ = settings.keyspace
    host_id = columns.Text(primary_key=True) # YouTube, Vimeo
    db_id = columns.UUID(primary_key=True, default=uuid.uuid1)
    created_at = columns.DateTime(primary_key=True, default=datetime.now())
    host_service = columns.Text(default='youtube')
    title = columns.Text() #source
    url = columns.Text() #source
    user_id = columns.UUID(index=True)

    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) ->  str:
        return f"Video(title={self.title}, host_id={self.host_id}, host_service={self.host_service})"
    
    def as_data(self):
        return {f"{self.host_service}_id": self.host_id, "path":self.path, "title":self.title}
    
    def render(self):
        basename = self.host_service # youtube, vimeo
        template_name = f"videos/renderers/{basename}.html"
        context = {"host_id": self.host_id}
        t = templates.get_template(template_name)
        return t.render(context)
    
    @property
    def path(self): 
        return f"/videos/{self.host_id}"
    
    @staticmethod
    def get_or_create(url, user_id=None, **kwargs):
        host_id = extract_video_id(url)
        obj = None
        created = False
        try:
            obj = Video.objects.get(host_id=host_id)
        except MultipleObjectsReturned:
            q = Video.objects.allow_filtering().filter(host_id=host_id)
            obj = q.first()
        except DoesNotExist:
            obj = Video.add_video(url, user_id=user_id, **kwargs)
            created = True
        except:
            raise Exception("Invalid Request")
        return obj, created
    
    def update_video_url(self, url, save=True):
        host_id = extract_video_id(url)
        if not host_id:
            return None
        self.url = url
        self.host_id = host_id
        if save:
            self.save()
        return url
    
    @staticmethod
    def add_video(url, user_id=None, **kwargs):
        
        host_id = extract_video_id(url)
        if host_id is None:
            raise InvalidYouTubeVideoURLException("Invalid YouTube Video URL")
        user_exists = User.check_exists(user_id)
        if user_exists is None:
            raise InvalidUserIDException("Invalid User id")
        
        q = Video.objects.allow_filtering().filter(host_id=host_id) #, user_id=user_id)
        
        if q.count() != 0:
            raise VideoAlreadyAddedException("Video already exists")
        return Video.create(host_id=host_id, user_id=user_id, url=url, **kwargs)