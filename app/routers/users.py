from fastapi import APIRouter
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, UploadFile
from pathlib import Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from schemas.users import UserInDB, Token, TokenData
from connect_csv.con import read_df, take_last_parametr, write_df
from typing import Union
import pathlib
from connect_csv.con import delete_df,take_last_parametr,write_df,get_all_files,find_file
from schemas.files import FileList
from schemas.users import User
from typing import List
import os

router = APIRouter()
users_csv_name = './app/connect_csv/users.csv'

#use a valid secret key
SECRET_KEY = "????"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(df, username: str):
    user = df[df["username"] == username].values
    if len(user) == 0:
        return False
    user_dict = {"username":df[df["username"] == username]['username'].values[0], 
            "hashed_password":df[df["username"] == username]["hashed_password"].values[0]}
    return UserInDB(**user_dict)


def authenticate_user(df, username: str, password: str):
    user = get_user(df, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(read_df(users_csv_name), username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/api/register")
def register(user: OAuth2PasswordRequestForm = Depends()):
    if not get_user(read_df(users_csv_name), user.username):
        user_id = take_last_parametr(users_csv_name, 'user_id')+1
        data = {
            "user_id": user_id,
            "username": [user.username],
            "password": [get_password_hash(user.password)]
        }
        write_df(users_csv_name, data)
        return {"username": user.username, "msg": "ok"}
    else:
        return {"msg": "there are another user with this username"}


@router.post("/api/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(read_df(users_csv_name), form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
