#!/usr/bin/python

import time
import ciso8601
from influxdb import InfluxDBClient
from sqlite_interface import get_connection, select_all_from_table
from variables import DB_FILE, TABLES_AND_COLUMNS, INFLUX_PARAMS, DEBUG


def set_last_timestamp(influx_client):
    query = 'select last("value"), "time" from "{}";'
    for table, data in TABLES_AND_COLUMNS.iteritems():
        result = influx_client.query(query.format(data["metrics"][0][1]))
        if DEBUG:
            print(query.format(data["metrics"][0][1]) + ' - {}'.format(result))
        if result:
            last_time = result.get_points().next()['time']
            if DEBUG:
                print("last time for table {}: {}".format(table, last_time))
            ts = ciso8601.parse_datetime('{}'.format(last_time))
            if DEBUG:
                print("last timestamp for table {}: {}".format(table, ts))
            TABLES_AND_COLUMNS[table]["last_timestamp"] = '%s' % ts


def fetch_and_upload_data(sqlite_conn, influx_client):
    for table, data in TABLES_AND_COLUMNS.iteritems():
        where_condition = "created > \"%s\"" % data["last_timestamp"]
        rows = select_all_from_table(
            sqlite_conn, table=table, col_list=data["columns"],
            where_condition=where_condition, limit=10000)
        if rows:
            TABLES_AND_COLUMNS[table]["last_timestamp"] = rows[-1][0]
            payload = []
            for row in rows:
                ts = ciso8601.parse_datetime(row[0])
                for idx, metric in data["metrics"]:
                    json = {
                        "measurement": metric,
                        "tags": {
                        },
                        "time": "%sZ" % ts.isoformat(),
                        "fields": {
                            "value": float(row[idx])
                        }
                    }
                    payload.append(json)
            influx_client.write_points(payload)
            if DEBUG:
                print(json)
                print(rows[-1][0])
        else:
            print "no new rows for table %s" % table


def main():
    parsed_args = []  # TODO

    # create a database connection
    conn = get_connection(DB_FILE)
    client = InfluxDBClient(
        INFLUX_PARAMS["address"], INFLUX_PARAMS["port"],
        INFLUX_PARAMS["username"], INFLUX_PARAMS["password"], INFLUX_PARAMS["database"]
    )
    if 'init_db' in parsed_args:
        client.drop_database(INFLUX_PARAMS["database"])
        client.create_database(INFLUX_PARAMS["database"])
        client.create_retention_policy('pluvio', 'INF', 1, default=True)
    set_last_timestamp(client)
    with conn:
        if 'keep_running' in parsed_args:
            while True:
                fetch_and_upload_data(conn, client)
                time.sleep(4)
        else:
            fetch_and_upload_data(conn, client)


if __name__ == '__main__':
    main()
