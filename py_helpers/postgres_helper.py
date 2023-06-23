from common_includes import *
STR_DELETED_RECORDS_TABLE = 'deleted_records'


def get_table_count(api_handle: api_handler):
    sql_str = sql.SQL("SELECT schemaname as table_schema, relname as table_name, n_live_tup as row_count FROM pg_stat_user_tables ORDER BY n_live_tup DESC;")
    response = db_execute_sql(api_handle=api_handle, sql_str=sql_str)
    return response


def get_pending_notifications(api_handle: api_handler):
    sql_str = sql.SQL("SELECT * FROM public.pending_notifications;")
    response = db_execute_sql(api_handle=api_handle, sql_str=sql_str)
    return response


def update_sms_status(api_handle: api_handler):
    sql_str = sql.SQL("SELECT * FROM public.sms_status_update;")
    response = db_execute_sql(api_handle=api_handle, sql_str=sql_str)
    return response


def get_record_by_field(api_handle: api_handler, table_name: str, field_name: str = None, field_value: int = None, fields: list = None, num_records: int = None) -> dict:
    if table_name is STR_DELETED_RECORDS_TABLE:
        sql_str = sql.SQL("SELECT * FROM {table} ORDER BY created_at DESC").format(table=sql.Identifier(table_name))

    elif fields is None and field_value is None:  # get all records with all fields
        sql_str = sql.SQL("SELECT * FROM {table} ORDER BY updated_at DESC").format(table=sql.Identifier(table_name))

    elif fields is not None and field_value is None:  # get all records but filter out fields
        sql_str = sql.SQL("SELECT {f} FROM {table} ORDER BY updated_at DESC").format(table=sql.Identifier(table_name),
                                f=sql.SQL(', ').join(sql.Composed([sql.Identifier(k)]) for k in fields))
    elif fields is None and field_value is not None:  # get single record with all fields
        sql_str = sql.SQL("SELECT * FROM {table} WHERE {col_name}=%s ORDER BY updated_at DESC").format(table=sql.Identifier(table_name),
                                col_name=sql.Identifier(field_name))
    else:  # get single record but filter out fields
        sql_str = sql.SQL("SELECT {f} FROM {table} WHERE {col_name}=%s ORDER BY updated_at DESC").format(table=sql.Identifier(table_name),
                                f=sql.SQL(', ').join(sql.Composed([sql.Identifier(k)]) for k in fields), col_name=sql.Identifier(field_name))
    response = db_execute_sql(api_handle=api_handle, sql_str=sql_str, data=(field_value,), num_records=num_records)
    return response


def delete_record_by_id (api_handle: api_handler, table_name: str, record_id: int) -> dict:
    sql_str = sql.SQL("DELETE FROM {table} WHERE id = %s").format(table=sql.Identifier(table_name))
    response = db_execute_sql(api_handle=api_handle, sql_str=sql_str, data=(record_id,))
    return response


def insert_record (api_handle: api_handler, table_name: str, record_dict: dict, fields_list: list = None):
    packed_record_dict = pack_dict(api_handle, record_dict, table_name)
    fields = sql.SQL(', ').join(sql.Identifier(k) for k in list(packed_record_dict))
    num_vals = sql.SQL(', ').join(sql.Placeholder() * len(packed_record_dict))
    if 'details' in packed_record_dict:
        packed_record_dict['details'] = json.dumps(packed_record_dict['details'])
    if fields_list is not None:  # get all records but filter out fields
        sql_str = sql.SQL("INSERT INTO {table}({cols}) VALUES ({vals}) RETURNING {f}").format(table=sql.Identifier(table_name), cols=fields, vals=num_vals,
                        f=sql.SQL(', ').join(sql.Composed([sql.Identifier(k)]) for k in fields_list))
    else:
        sql_str = sql.SQL("INSERT INTO {table}({cols}) VALUES ({vals}) RETURNING *").format(table=sql.Identifier(table_name), cols=fields, vals=num_vals)

    response = db_execute_sql(api_handle=api_handle, sql_str=sql_str, data=tuple(packed_record_dict.values()), num_records=None)
    response = pack_json(response)
    return response


def update_record_by_id (api_handle: api_handler, table_name: str, record_id: int, record_dict: dict, return_record: bool = True) -> dict:
    response = {'success': True}
    packed_record_dict = pack_dict(api_handle, record_dict, table_name)
    try:
        db_cur = api_handle.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        if 'details' in packed_record_dict:
            sql_str = sql.SQL("SELECT details FROM {table} WHERE id = %s").format(table=sql.Identifier(table_name))
            db_cur.execute(sql_str, (record_id,))
            if db_cur.rowcount == 0:  # rowcount will be 1 if update was successful
                api_handle.capture_error(STR_MSG_NO_RECORDS_FOUND)
                return {'success': False}

            records = db_cur.fetchall()
            existing_details = records[0]['details']  # retrieve existing details json field
            if existing_details is None:
                existing_details = {}
            success, message = modify_json_fields(record_dict=packed_record_dict, existing_details_dict=existing_details)
            if not success:
                api_handle.capture_error(message)
                response = {'success': False}
                return response

            # update 'details' fields separately since it requires to be json dumped format
            sql_str = sql.SQL("UPDATE {table} SET details=%s WHERE id = %s  RETURNING *").format(table=sql.Identifier(table_name))

            db_cur.execute(sql_str, (json.dumps(existing_details), record_id))
            if db_cur.rowcount == 0:  # rowcount will be 1 if update was successful
                api_handle.capture_error(STR_MSG_NO_RECORDS_FOUND)
                return {'success': False}

            packed_record_dict.pop('details')  # remove the details key from dict since it has been updated

        if len(packed_record_dict) > 0:  # check if there are any other fields that need to be updated
            sql_str = sql.SQL("UPDATE {table} SET {new_vals} WHERE id = {id}  RETURNING *").format(
                table=sql.Identifier(table_name),
                new_vals=sql.SQL(', ').join(sql.Composed([sql.Identifier(k), sql.SQL(" = "), sql.Placeholder(k)]) for k in packed_record_dict.keys()),
                id=sql.Placeholder('id'))

            packed_record_dict.update({'id': record_id})
            res = db_cur.execute(sql_str, packed_record_dict)

            if db_cur.rowcount == 0:  # rowcount will be 1 if update was successful
                api_handle.capture_error(STR_MSG_NO_RECORDS_FOUND)
                return {'success': False}
        if return_record:
            updated_row = db_cur.fetchall()
            response.update({'records': updated_row})
        db_cur.close()

    except (psycopg2.ProgrammingError, psycopg2.DataError, psycopg2.IntegrityError) as msg:
        api_handle.capture_error(msg.pgerror)
        response = {'success': False}
        return response

    response.update({'success': True})
    packed_response = pack_json(response)
    return packed_response


#
# ONLY BATCH LOGS NEEDS THIS FUNCTION - TRY TO ELIMINATE
#
def insert_multiple_records (api_handle: api_handler, table_name: str, records: list, fields_list: list = None, return_record: bool = True):
    """
        - fields_list: list with order of fields according to which records are provided.
            example: ['id', 'pod_name', 'pod_health', 'location_id']

        - records: a list of tuples containing values.
            # assuming fields_list looks like that in the example
            example:[
                ('1001071', 'pod_name_1', 'health_of_pod_1', 1),
                ('1001089', 'pod_name_15', 'health_of_pod_15', 9),
                .......
            ]
    """
    response = {'success': True}
    try:
        fields = sql.SQL(', ').join(sql.Identifier(k) for k in fields_list)
        sql_str = sql.SQL("INSERT INTO {table}({cols}) VALUES %s RETURNING *").format(table=sql.Identifier(table_name), cols=fields)

        db_cur = api_handle.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        psycopg2.extras.execute_values(db_cur, sql_str, records, template=None, page_size=1000)
        if return_record:
            new_row = db_cur.fetchall()
            response.update({'records': new_row})
        db_cur.close()
    except (psycopg2.ProgrammingError, psycopg2.DataError, psycopg2.IntegrityError) as msg:
        api_handle.capture_error(msg.pgerror)
        ic("EXCEPTION", msg.pgerror, msg)
        response = {'success': False}
    return response


def check_if_record_exists_in_table (api_handle: api_handler, table_name: str, field_name: str, field_value: str) -> bool:
    if (table_name is None) or (field_value is None) or (field_name is None):
        return False
    response = get_record_by_field(api_handle=api_handle, table_name=table_name, field_name=field_name, field_value=field_value, num_records=0)
    if (response['success'] is True):
        return True
    if (len(response['records']) > 0):
        return True
    return False



