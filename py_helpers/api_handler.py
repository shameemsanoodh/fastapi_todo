from common_includes import *
import psycopg2
from psycopg2.sql import Identifier, SQL
import time


class api_handler:
    """
        class for handling db_connections, commits and rollbacks
    """
    def __init__(self, request: Request = None):
        self.start_at = None
        self.request = None
        self.result = {}
        self.success = True
        self.message = "default value"

        # DB Related:
        self.call_rollback = False
        self.db_conn = None
        self.table_columns = {}
        self.db_profile_name = None

        self.start_at = time.time()
        self.request = request

        self.startup()
        return

    def startup(self, db_profile_name: str = None):
        """
            This function commits/rollbacks the transaction and closes DB connection
        """
        # DB Related:
        self.db_profile_name = db_profile_name

        if (self.db_conn is not None):
            self.db_conn = db_disconnect(db_conn = self.db_conn, rollback = self.call_rollback)

        # DB Related:
        self.db_conn = db_connect(db_profile_name=self.db_profile_name)
        return


    def capture_error(self, message: str = "error"):
        """
            Helper function will call this method to indicate something went wrong when executing the sql query
        """
        # print("api_handler: capture_error - message=[" + str(message) + "]")
        self.success = False
        self.message = message
        self.call_rollback = True
        return

    def log_data(self, process_time: float, result: dict = None) -> str:
        """
            result can be passed in too, if we want that to be logged as well.
        """
        request_details = ""
        if self.request is not None:
            request_dict = self.request.__dict__
            client = request_dict['scope'].get('client', None)
            method = request_dict['scope'].get('method', None)
            path = request_dict['scope'].get('path', None)
            query = request_dict['scope'].get('query_string', None)
            body = request_dict.get('_body', None)
            request_details = "client = {client}, method = {method}, path = {path}, query = {query}, body = {body} , response_time={time}".format(
                client=client, method=method, path=path, query=query, body=body, time=process_time)
        return str(request_details)

    def shutdown(self):
        """
            This function commits/rollbacks the transaction and closes DB connection
        """
        self.stop_at = time.time()
        process_time = (self.stop_at - self.start_at) * 1000
        logmsg = self.log_data(process_time=process_time)

        # DB Related:
        self.db_conn = db_disconnect(db_conn = self.db_conn, rollback = self.call_rollback)

        return

    def __del__(self):
        self.shutdown()
        return


# -------------------------------------


def enumerate_tables_columns (api_handle: api_handler):
    if (len(api_handle.table_columns) > 0):
        return
    sql_str = sql.SQL("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    response = db_execute_sql(api_handle=api_handle, sql_str=sql_str, data=())
    table_name_list = []
    for table in response['records']:
        for key, name in table.items():
            table_name_list.append(name)
    for table_name in table_name_list:
        sql_str = sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s;")
        column_response = db_execute_sql(api_handle=api_handle, sql_str=sql_str, data=(table_name, ))
        column_name_list = []
        for column in response['records']:
            for key, name in column.items():
                column_name_list.append(name)
        api_handle.table_columns[table_name] = column_name_list
    return


def populate_list_all_table_columns (api_handle: api_handler, table_name: str = None):
    if (table_name is not None) and (table_name in api_handle.table_columns):
        return
    sql_str = sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s;")
    response = db_execute_sql(api_handle=api_handle, sql_str=sql_str, data=(table_name, ))
    col_names = []
    for col in response['records']:
        for key, col_name in col.items():
            col_names.append(col_name)
    api_handle.table_columns[table_name] = col_names
    return


def pack_dict (api_handle: api_handler, record_dict: dict, table_name: str) -> dict:
    populate_list_all_table_columns(api_handle=api_handle, table_name=table_name)
    details_dict = {}
    new_record_dict = {}
    for key, val in record_dict.items():
        if (key != 'details') and (key not in api_handle.table_columns[table_name]):
            details_dict.update({key: val})
            continue
        new_record_dict.update({key: val})
    if len(details_dict) != 0:
        new_record_dict.update({'details': details_dict})
    return(new_record_dict)


def modify_json_fields (record_dict: dict, existing_details_dict: dict) -> tuple:
    """
        record_dict can be of type
            {"some_key": "val", "details": {"remove": "some_field_name", "existing_key": "new_value", "new_key": "some_value" }} OR
            {"some_key": "val", "details": {"remove": ["field1", "field2"], "existing_key": "new_value", "new_key": "some_value" }}
        This function will remove all fields mentioned as values in the "remove" key and update remaining keys in the existing details json field.
    """
    if 'details' in record_dict:
        if record_dict.get('details') != {}:
            existing_details_dict.update(record_dict['details'])
        success = True
        message = "No error"
    else:
        success = False
        message = "Key [details] missing"
    return success, message


def unpack_json (response):
    if 'records' not in response:
        return response

    new_records = []
    for record in response['records']:
        if 'details' not in record:
            new_records.append(record)
        else:
            # if 'details' field is present in record
            new_record = {}
            if record.get('details') is not None:
                for key, val in record['details'].items():
                    new_record.update({key: val})
            del record['details']
            new_record.update(record)
            new_records.append(new_record)
    response['records'] = new_records
    return response


def pack_json (response):
    if 'records' not in response:
        return response

    new_records = []
    for record in response['records']:
        if record.get('details', None) is None:
            new_records.append(record)
        else:
            new_record = {}
            for key, val in record['details'].items():
                new_record.update({key: val})
            del record['details']
            new_record.update(record)
            new_records.append(new_record)
    response['records'] = new_records
    return response


def db_dumpinfo (db_conn):
    if db_conn is None: return
    db_cur = None
    try:
        db_cur = db_conn.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)
        db_cur.execute('SELECT version()')
        # display the PostgreSQL database server version
        db_version = db_cur.fetchone()
        #print(".txt info=[" + str(db_version) + "]")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print('Error: db_table_create')
    finally:
        if (db_cur is not None):
            db_cur.close()
            self.db_conn = None
    return


def db_connect(db_profile_name: str = None):
    db_conn = None
    while True:
        try:
            db_host = os.getenv('EASTVANTAGE_DB_HOST')
            db_name = os.getenv('EASTVANTAGE_DB_NAME')
            db_user = os.getenv('EASTVANTAGE_DB_USER')
            db_password = os.getenv('EASTVANTAGE_DB_PWD')
            db_port = os.getenv('EASTVANTAGE_DB_PORT')
            db_conn = psycopg2.connect(host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_password)
            break
        except (Exception, psycopg2.DatabaseError) as error:
            print('Error: db_connect:', error)
        except psycopg2.OperationalError as msg:
            print('Error: db_connect: %s' % msg)
    return db_conn


def db_disconnect (db_conn = None, rollback: bool = False):
    if db_conn is not None:
        if rollback:  # some error has occurred
            db_conn.rollback()
        else:  # no errors, commit transaction
            db_conn.commit()

        db_conn.close()
        db_conn = None
    return None


def db_execute_sql (api_handle: api_handler, sql_str: psycopg2.sql.SQL, data: tuple = None, num_records: int = None) -> dict:
    try:
        records = []
        response = {'success': True}
        db_cur = api_handle.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        db_cur.execute(sql_str, data)

        if (db_cur.rowcount > 0) and (db_cur.description is not None):                    # rowcount will be 1 or greater if delete was successful
            if (num_records is None) or (num_records <= -1):
                # if num_records is None or -1 it implies get all records
                records = db_cur.fetchall()
            elif (num_records == 0):
                # if the call just wants the query to be run and record count to be returned
                # so not fetch any records then num_records will be set at 0
                records = []
            else:
                # any other non zro positive number will be passed to the fetch query
                records = db_cur.fetchmany(num_records)
        db_cur.close()
        if (db_cur.rowcount <= 0):                    # No matching record found
            response.update({'success': False})
        # here total_count returns the count as per db_cur query response.
        # count is the number of records fetched - which could be < total_count since the user
        # may have requested fewer than all the records be returned or pagination maybe implemented
        response.update({'total_count': db_cur.rowcount})
        response.update({'count': len(records)})
        response.update({'records': records})
        api_handle.result = response

    except (psycopg2.ProgrammingError, psycopg2.DataError, psycopg2.IntegrityError) as msg:
        api_handle.capture_error(msg.pgerror)
        response = {'success': False}
        print(msg)

    unpacked_response = unpack_json(response)
    return unpacked_response
