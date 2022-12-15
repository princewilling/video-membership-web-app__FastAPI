from fastapi import HTTPException, Request
from functools import wraps

from app.users.auth import verify_user_id
from app.users.exceptions import LoginRequiredException

def login_required(func):
    @wraps(func)
    def wrapper(request: Request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise LoginRequiredException(status_code=401)
        return func(request, *args, **kwargs)
    return wrapper

# def login_required(func):
#     @wraps(func)
#     def wrapper(request: Request, *args, **kwargs):
#         session_token = request.cookies.get('session_id')
#         user_session = verify_user_id(session_token)
#         if user_session is None:
#             raise LoginRequiredException(status_code=401)
#         return func(request, *args, **kwargs)
#     return wrapper