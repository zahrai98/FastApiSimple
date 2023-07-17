from fastapi import APIRouter
from fastapi import UploadFile, Depends
from pathlib import Path
from typing import List
from connect_csv.con import delete_df,take_last_parametr,write_df,get_all_files,find_file
from schemas.files import FileList
from schemas.users import User
import os
from .users import get_current_user

router = APIRouter()

files_csv_name = './app/connect_csv/files.csv'


@router.post('/api/send-file')
async def create(name:str, file: UploadFile):
    path = Path('./app/files/') / file.filename
    path.write_bytes(await file.read())
    file_id = take_last_parametr(files_csv_name, 'file_id') + 1
    data = {
        'file_id': file_id,
        'file_name': [name],
        'file_path': [path]
    }
    write_df(files_csv_name, data)
    return {'file': file.filename, 'name': name}


@router.get('/api/list-file', response_model=List[FileList])
def list(current_user: User = Depends(get_current_user)):
    return get_all_files(files_csv_name)


@router.get('/api/get-file',response_model=FileList)
def retrive(id: int):
    data = find_file(files_csv_name, id)
    if data:
        return data
    return {'msg':"Not Found"}


@router.delete('/api/delete-file')
def delete_(id: int):
    data = find_file(files_csv_name, id)
    
    if data:
        print(data)
        file_path = data['file_path']
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                delete_df(files_csv_name, id)
                return {'msg':"Done"}
            except:
                return {'msg':"Problem"}
    return {'msg':"Not Found"}

