from datetime import datetime
from typing import Optional
import uuid
from fastapi import APIRouter, HTTPException, Request, Form, Depends, status
from fastapi.responses import HTMLResponse

from app import utils
from app.users.decorators import login_required
from app.shortcuts import ( get_object_or_404, is_htmx, render, redirect)

from app.watch_events.models import WatchEvent
from .models import Video
from .schemas import (VidoeCreateSchema, VideoEditSchema)


router = APIRouter(
    prefix='/videos'
)

@router.get("/", response_class=HTMLResponse)
def video_list_view(request: Request):
    q = Video.objects.all()
    context = {
        "object_list": q
    }
    return render(request, "videos/video-home.html", context)

@router.get("/user_videos", response_class=HTMLResponse)
@login_required
def video_list_view_per_user(request: Request):
    q = Video.objects.filter(user_id=request.user.username)
    context = {
        "object_list": q
    }
    return render(request, "videos/list.html", context)

@router.get("/create", response_class=HTMLResponse)
@login_required
def video_create_view(request: Request,  is_htmx=Depends(is_htmx),
                      playlist_id:Optional[uuid.UUID]=None):
    print(playlist_id)
    if is_htmx:
        return render(request, "videos/htmx/create.html", {})
    return render(request, "videos/create.html", {})


@router.post("/create", response_class=HTMLResponse)
@login_required
def video_create_post_view(request: Request, is_htmx=Depends(is_htmx), title: str=Form(...), url: str = Form(...)):
    raw_data = {
        "title": title,
        "url": url,
        "user_id": request.user.username
    }
    data, errors = utils.valid_schema_data_or_error(raw_data, VidoeCreateSchema)
    redirect_path = data.get('path') or "/videos/create" 
    
    context = {
        "data": data,
        "errors": errors,
        "title": title,
        "url": url,
    }

    if is_htmx:
        """
        Handle all HTMX requests
        """
        if len(errors) > 0:
            return render(request, "videos/htmx/create.html", context)
        context = {"path": redirect_path, "title": data.get('title')}
        return render(request, "videos/htmx/link.html", context)
    """
    Handle default HTML requests
    """
    if len(errors) > 0:
        return render(request, "videos/create.html", context, status_code=400)
    return redirect(redirect_path)

@router.get("/{host_id}", response_class=HTMLResponse)
def video_detail_view(request: Request, host_id:str):
    obj = get_object_or_404(Video, host_id=host_id)
    start_time = 0
    if request.user.is_authenticated:
        user_id = request.user.username
        start_time = WatchEvent.get_resume_time(host_id, user_id)
    context = {
        "host_id": host_id,
        "object": obj,
        "start_time": start_time  
    }
    return render(request, "videos/detail.html", context)


@router.get("/{host_id}/edit", response_class=HTMLResponse)
@login_required
def video_edit_view(request: Request, host_id: str):
    obj = get_object_or_404(Video, host_id=host_id)
    
    if obj.user_id != request.user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    context = {
        "object": obj
    }
    return render(request, "videos/edit.html", context) 



@router.post("/{host_id}/edit", response_class=HTMLResponse)
@login_required
def video_edit_post_view(request: Request, host_id: str, is_htmx=Depends(is_htmx), 
                         title: str=Form(...), url: str = Form(...)):
    raw_data = {
        "title": title,
        "url": url,
        "user_id": request.user.username
    }
    obj = get_object_or_404(Video, host_id=host_id)
    
    if obj.user_id != request.user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    data, errors = utils.valid_schema_data_or_error(raw_data, VideoEditSchema)
    if len(errors) > 0:
        return render(request, "videos/edit.html", context, status_code=400)
    obj.title = data.get('title') or obj.title
    obj.update_video_url(url, save=True)
    context = {
        "object": obj
    }
    return render(request, "videos/edit.html", context)



@router.get("/{host_id}/hx-edit", response_class=HTMLResponse)
@login_required
def video_hx_edit_view(request: Request, host_id: str, is_htmx=Depends(is_htmx)):
    if not is_htmx:
        raise HTTPException(status_code=400)
    obj = None
    not_found = False
    try:
        obj = get_object_or_404(Video, host_id=host_id)
    except:
        not_found = True
    if not_found:
        return HTMLResponse("Not found, please try again.", status_code=404)
    if obj.user_id != uuid.UUID(request.user.username):
        return HTMLResponse("Not authorized to perform requested action", status_code=403)
    context = {
        "object": obj
    }
    return render(request, "videos/htmx/edit.html", context) 



@router.post("/{host_id}/hx-edit", response_class=HTMLResponse)
@login_required
def video_hx_edit_post_view(request: Request, host_id: str, is_htmx=Depends(is_htmx), 
                            title: str=Form(...), url: str = Form(...), 
                            delete: Optional[bool] = Form(default=False)):
    if not is_htmx:
        raise HTTPException(status_code=400)
    obj = None
    not_found = False
    try:
        obj = get_object_or_404(Video, host_id=host_id)
    except:
        not_found = True
    if not_found:
        return HTMLResponse("Not found, please try again.", status_code=404)
    if obj.user_id != uuid.UUID(request.user.username):
        return HTMLResponse("Not authorized to perform requested action", status_code=403)
    if delete:
        obj.delete()
        return HTMLResponse('Item Deleted', status_code=204)
    raw_data = {
        "title": title,
        "url": url,
        "user_id": request.user.username
    }
    data, errors = utils.valid_schema_data_or_error(raw_data, VideoEditSchema)
    if len(errors) > 0:
        return render(request, "videos/htmx/edit.html", context, status_code=400)
    obj.title = data.get('title') or obj.title
    obj.update_video_url(url, save=True)
    context = {
        "object": obj
    }
    return render(request, "videos/htmx/list-inline.html", context)