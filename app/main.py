import pathlib
from fastapi.responses import HTMLResponse   
from fastapi import FastAPI, Request, Form, HTTPException
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import requires
from cassandra.cqlengine.management import sync_table
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
 
from . import db, utils
from . shortcuts import render, redirect
from .users.models import User
from .users.backends import JWTCookieBackend
from .users.schemas import UserSignupSchema, UserLoginSchema
from .users.decorators import login_required

from .videos.models import Video
from .videos.routers import router as video_router

from .watch_events.models import WatchEvent
from .watch_events.routers import router as watch_event_router

from .playlists.routers import router as playlist_router
from app.playlists.models import Playlist


BASE_DIR = pathlib.Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"  
STATIC_DIR = BASE_DIR / "static"  

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.add_middleware(AuthenticationMiddleware, backend=JWTCookieBackend())
app.include_router(video_router)
app.include_router(watch_event_router)
app.include_router(playlist_router)

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

DB_SEESSION = None

from .handlerz import * # noqa



@app.on_event("startup")
def on_startup():
    #triggred when fastapi starts
    global DB_SEESSION
    DB_SEESSION = db.get_session()
    sync_table(User) 
    sync_table(Video) 
    sync_table(WatchEvent)
    sync_table(Playlist)


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    if request.user.is_authenticated:
        return render(request, "dashboard.html", {}, status_code=200)
    
    return render(request, "home.html", {})  # json data REST API

@app.get("/account", response_class=HTMLResponse)
@login_required
def account_view(request: Request):
    """
    hello world
    """
    context = {}
    return render(request, "account.html", context)

@app.get("/login", response_class=HTMLResponse)
def login_get_view(request: Request):
    context = {}
    return render(request, "auth/login.html", context=context) 

@app.post("/login", response_class=HTMLResponse)
def login_post_view(request: Request, email:str = Form(...), password:str = Form(...)):
    
    raw_data = {
        "email": email,
        "password": password
    }
    
    data, errors = utils.valid_schema_data_or_error(raw_data, UserLoginSchema)
    context = {
        "data": data,
        "errors": errors,
    }
    if len(errors) > 0:
        return render(request, "auth/login.html", context=context, status_code=400)
    
    return redirect("/", cookies=data)

@app.get("/signup", response_class=HTMLResponse)
def signup_get_view(request: Request):
    context = {}
    return render(request, "auth/signup.html", context=context) 

@app.post("/signup", response_class=HTMLResponse)
def signup_post_view(request: Request, 
                    email:str = Form(...), 
                    password:str = Form(...), 
                    password_confirm:str = Form(...)):
    
    raw_data = {
        "email": email,
        "password": password,
        "password_confirm": password_confirm
    }
    
    data, errors = utils.valid_schema_data_or_error(raw_data, UserSignupSchema)
    context = {
        "data":data,
        "errors":errors
    }
    if len(errors) > 0:
        return render(request, "auth/signup.html", context=context, status_code=400)
    
    return redirect("/login", cookies=data)

@app.get("/index", response_class=HTMLResponse)
def index_view(request: Request):
    """
    hello world
    """
    context = {}
    return render(request, "index.html", context)

@app.get("/logout", response_class=HTMLResponse)
def logout_get_view(request: Request):
    if not request.user.is_authenticated:
        return redirect('/login')
    return render(request, "auth/logout.html", {})

@app.post("/logout", response_class=HTMLResponse)
def logout_post_view(request: Request):
    return redirect("/login", remove_session=True)