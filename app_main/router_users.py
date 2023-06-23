from fastapi import APIRouter
from common_includes import *
# from common_decorators import *
from app_main.users import *
import os
router_users = APIRouter()
INT_SECS = 3600


def check_pass_phase(pass_phase: str = None) -> bool:
    current_valid_pass_phase = "123456"
    if ((pass_phase is None) or (len(pass_phase) <= 0) or (pass_phase != current_valid_pass_phase)):
        return(False)
    return(True)


@router_users.get("/generate_new_token/", tags=["misc"])
async def generate_new_token(request: Request, expiry_secs: int = Query(None), pass_phase: str = Query(None)):
    """
    Generates an access token with long validity by default. You can also generate with custom expiry by passing value in seconds to `expiry_secs` using query param
    """
    response = {'success': False, 'access_token': '', 'message': 'Error: Authentication failed - invalid pass phase suuplied.'}
    if check_pass_phase(pass_phase):
        body = await request.body()
        dummy_payload = {'message': 'token generated for testing purpose'}
        if expiry_secs is None:
            expiry_secs = INT_SECS
        response = {'access_token': encode_token(payload_dict=dummy_payload, expiry_secs=expiry_secs)}
    return(response)


@router_users.get('/login/', tags=["misc"])
async def users(request: Request, user_mail: str, user_password: str, token: str = Depends(token_auth_scheme), api_handle=Depends(api_handler)):
    """
       Parameters:
       - **fields**: This retrieves only the field name given from all record `example(fields:user_name)`.
       - **num_records**: This retrieves only the number of records mentioned `example(num_records:5)`.
       """
    return login(api_handle=api_handle,user_mail=user_mail,user_password=user_password)


@router_users.get('/users/', tags=["users"])
async def users(request: Request, fields: Optional[List[str]] = Query(None), num_records: int = Query(None), token: str = Depends(token_auth_scheme), api_handle=Depends(api_handler)):
    """
       Parameters:
       - **fields**: This retrieves only the field name given from all record `example(fields:user_name)`.
       - **num_records**: This retrieves only the number of records mentioned `example(num_records:5)`.
       """
    return get_all(api_handle=api_handle, fields=fields, num_records=num_records, table_name="users")


@router_users.get('/users/{record_id}', tags=["users"])
async def users(request: Request, record_id: int, token: str = Depends(token_auth_scheme), api_handle=Depends(api_handler)):
    return get_all(api_handle=api_handle, record_id=record_id, table_name="users")


@router_users.post('/users/', tags=["users"])
async def users(request: Request, body: dict = Body(...), token: str = Depends(token_auth_scheme), api_handle=Depends(api_handler)):
    """
    - Data is expected in json like
    - Copy **JSON** and Execute to post records to Database
        ```{
        {
          "user_name": "user_name",
          "mail_id": "mail@gmail.com",
          "password":"1234"

        }
    """
    return add(api_handle=api_handle, record_dict=body, table_name="users")


@router_users.patch('/users/{record_id}', tags=["users"])
async def users(record_id, request: Request, record_dict: dict = Body(...), token: str = Depends(token_auth_scheme), api_handle=Depends(api_handler)):
    """
    Edit an item by ID.

    This endpoint get an item with id passed the database `id`.
    ```
        {
          "user_name": "wobot", "mail_id": "wobot@gmail.com", "password":"12345678"
        }
    """
    return update(api_handle=api_handle, record_id=record_id, record_dict=record_dict, table_name="users")


@router_users.delete('/users/{record_id}', tags=["users"])
async def users(request: Request, record_id: int, token: str = Depends(token_auth_scheme), api_handle=Depends(api_handler)):
    """
    Delete an item by ID.

    This endpoint get an item with id passed the database `id`.
    """
    return delete(api_handle=api_handle, record_id=record_id, table_name="users")


@router_users.get('/todo/', tags=["todo"])
async def users(request: Request, fields: Optional[List[str]] = Query(None), num_records: int = Query(None), token: str = Depends(token_auth_scheme), api_handle=Depends(api_handler)):
    """
       Parameters:
       - **fields**: This retrieves only the field name given from all record `example(fields:user_name)`.
       - **num_records**: This retrieves only the number of records mentioned `example(num_records:5)`.
       """
    return get_todo(api_handle=api_handle, fields=fields, num_records=num_records, table_name="todo")


@router_users.get('/todo/{record_id}', tags=["todo"])
async def users(request: Request, record_id: int, token: str = Depends(token_auth_scheme), api_handle=Depends(api_handler)):
    return get_todo(api_handle=api_handle, record_id=record_id, table_name="todo")


@router_users.post('/add_remove_todo/', tags=["todo"])
async def users(request: Request, user_id: int, title: str, todoitem: str, method: str = Query(None), token: str = Depends(token_auth_scheme), api_handle=Depends(api_handler)):
    """
    - Data is expected in json like
    - Copy **JSON** and Execute to post records to Database
        ```{
        {
          "user_id": 1,
          "title": "shopping list",
          "todoitem": "apple",
          "method" : "ADD/DELETE" - default ADD
        }
    """
    return add_remove_todo(api_handle=api_handle, user_id=user_id, title=title, todoitem=todoitem, method=method)


@router_users.patch('/edit_todo_title/{record_id}', tags=["todo"])
async def users(record_id, request: Request, record_dict: dict = Body(...), token: str = Depends(token_auth_scheme), api_handle=Depends(api_handler)):
    """
    Edit an item by ID.

    This endpoint get an item with id passed the database `id`.
    ```
        {
          "title": "fruit"
        }
    """
    return update(api_handle=api_handle, record_id=record_id, record_dict=record_dict, table_name="todo")


@router_users.delete('/todo/{record_id}', tags=["todo"])
async def users(request: Request, record_id: int, token: str = Depends(token_auth_scheme), api_handle=Depends(api_handler)):
    """
    Delete an item by ID.

    This endpoint get an item with id passed the database `id`.
    """
    return delete(api_handle=api_handle, record_id=record_id, table_name="todo")


@router_users.get("/download_code/",  tags=["code"])
async def files(request: Request,token: str = Depends(token_auth_scheme), api_handle=Depends(api_handler)):
    """
          API for downloading file.
          `Execute` to get source code of fast api.
          `cd wobot`
          `pip install -r requirements.txt`
          `python3 main.py`
    """
    home_dir = './files/'
    file_name = 'wobot.zip'
    print(home_dir + file_name)
    if not os.path.isfile(home_dir + file_name):
        return {"success": False, "message": 'File does not exist'}
    else:
        return FileResponse(path=home_dir + file_name, filename=file_name)