import jwt
import datetime
import logging 

from functools import wraps
from flask import request, abort
from google.auth.transport import requests
from google.oauth2 import id_token
from app.models.users import User
from config import Config

logger = logging.getLogger(Config.LOGGER_NAME)

def verify_jwt_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token =  request.headers['Authorization'].split(' ')[1]
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            id_info = id_token.verify_oauth2_token(token, requests.Request())
            logger.debug("Successfully verified token.")

            # See if the user exists
            email = id_info['email']
            logger.debug(f"Checking if {email} exists in database.")
            user = User().get_or_none(email=email)
            if not user:
                abort(401, f'User not found: {email}')

            exp = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            jwt_token = jwt.encode({'email': email, 'exp': exp}, Config.SECRET_KEY, algorithm='HS256')
        except ValueError:
            abort(410, 'Invalid token')
        except Exception as e:
            abort(500, 'Something went wrong')
        return f(user, jwt_token, *args, **kwargs)
    return decorated_function