import uuid
from app.config import get_settings
from app.users.exceptions import InvalidUserIDException
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

from app.users.models import User
from app.shortcuts import templates
from .extractors import extract_video_id
from .exceptions import InvalidYouTubeVideoURLException, VideoAlreadyAddedException

settings = get_settings()
  
class Video(Model):
    __keyspace__ = settings.keyspace
    host_id = columns.Text(primary_key=True) # YouTube, Vimeo
    db_id = columns.UUID(primary_key=True, default=uuid.uuid1)
    host_service = columns.Text(default='youtube')
    title = columns.Text() #source
    url = columns.Text() #source
    user_id = columns.UUID()
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __repr__(self) ->  str:
        return f"Video(title={self.title}, host_id={self.host_id}, host_service={self.host_service})"
    
    def as_data(self):
        return {f"{self.host_service}_id": self.host_id, "path":self.path}
    
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