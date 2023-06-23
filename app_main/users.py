from common_includes import *


def get_all(api_handle: api_handler, record_id: int = None, fields: list = None, num_records: int = None, table_name: str = None):
    return get_record_by_field(api_handle=api_handle, table_name=table_name, field_name="id", field_value=record_id, fields=fields, num_records=num_records)


def add(api_handle: api_handler, record_dict: dict, table_name: str = None):
    return insert_record(api_handle=api_handle, table_name=table_name, record_dict=record_dict)


def update(api_handle: api_handler, record_id: int, record_dict: dict, table_name: str = None):
    return update_record_by_id(api_handle=api_handle, table_name=table_name, record_id=record_id, record_dict=record_dict)


def delete(api_handle: api_handler, record_id: int, table_name: str = None):
    return delete_record_by_id(api_handle=api_handle, table_name=table_name, record_id=record_id)


def login(api_handle: api_handler,user_mail: str, user_password: str):
    sql_str = sql.SQL("SELECT * FROM users WHERE mail_id='" + str(user_mail) + "' and password='" + str(user_password) + "';")
    response = db_execute_sql(api_handle=api_handle, sql_str=sql_str)
    if not response["success"]:
        return {"success": False, "message": "Invalid user credential if New User Sign IN"}
    return response


def get_todo(api_handle: api_handler, record_id: int = None, fields: list = None, num_records: int = None, table_name: str = None):
    if record_id is None:
        response = get_all(api_handle=api_handle, fields=fields, num_records=num_records, table_name="todo")
    else:
        response = get_all(api_handle=api_handle, record_id=record_id, table_name="todo")
    if response["success"]:
        for record in response["records"]:
            my_list_values = record["my_list"]
            cleaned_my_list_values = [value.strip() for value in my_list_values]
            record["my_list"] = cleaned_my_list_values
    return response


def add_remove_todo(api_handle: api_handler, user_id: int, title: str, todoitem: str, method: str = None):
    todo = []
    sql_str = sql.SQL("select * from todo where user_id =" + str(user_id) + " and title='" + str(title) + "'")
    response = db_execute_sql(api_handle=api_handle, sql_str=sql_str)
    if response['success']:
        todo = response['records'][0]['my_list']
        todo_list = [item.strip() for item in todo]

        if method == "DELETE":
            print(len(todo_list))
            if len(todo_list) == 0:
                return {"success": False, "message": "No item to delete"}
            if todoitem not in todo_list:
                return {"success": False, "message": "Item Not in list"}
            todo_list.remove(str(todoitem))
            sql_str = sql.SQL("UPDATE todo SET my_list = %s WHERE user_id = %s and title = %s;")
            response = db_execute_sql(api_handle=api_handle, sql_str=sql_str, data=(todo_list, user_id, title,))
        else:
            todo_list.append(str(todoitem))
            sql_str = sql.SQL("UPDATE todo SET my_list = %s WHERE user_id = %s and title = %s;")
            response = db_execute_sql(api_handle=api_handle, sql_str=sql_str, data=(todo_list, user_id, title,))
    else:
        todo.append(todoitem)
        todo_list = [value.rstrip() for value in todo]
        sql_str = sql.SQL("INSERT INTO todo(user_id, my_list, title) VALUES(%s,%s,%s);")
        response = db_execute_sql(api_handle=api_handle, sql_str=sql_str, data=(user_id, todo_list, title,))
    return response