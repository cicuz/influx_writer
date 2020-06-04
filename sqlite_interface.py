import sqlite3
from sqlite3 import Error


def get_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def select_all_from_table(conn, table, col_list=None, where_condition=None, limit=-1):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    query = "SELECT " + ("*" if not col_list else ", ".join(col_list))
    query += " FROM " + table
    if where_condition is not None:
        query += " WHERE %s" % where_condition
    query += " LIMIT %d;" % limit

    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    return rows
