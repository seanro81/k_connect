import asyncio

import asyncpg
import datetime

from pypika import Query, Table, Field, Column, functions, Order
from settings.config import logging, PG_CONN_STRING


#postgres://someuser:somepassword@somehost:381/somedatabase
#'postgresql://postgres:pgpwd4habr@127.0.0.1:5432/postgres'

async def sql_exec_transaction(sql_list: list):
    conn = await asyncpg.connect(PG_CONN_STRING)
    # Execute a statement to create a new table.
    for item in sql_list:
        await conn.execute(item)
    await conn.close()


async def sql_get_cursor(query: str):
    conn = await asyncpg.connect(PG_CONN_STRING)
    rows = await conn.fetchrow(query)
    res = []
    #result = [dict(row) for row in rows]
    if rows is not None:
        for record in rows:
            res.append(record)
        await conn.close()
        return res
    await conn.close()
    return None


data = """{
"Alloc": {
"Type": "gauge",
        "Name": "Alloc",
        "Description": "Alloc is bytes of allocated heap objects.",
        "Value": 24293912
    },
    "FreeMemory": {
"Type": "gauge",
        "Name": "FreeMemory",
        "Description": "RAM available for programs to allocate",
        "Value": 7740977152
    },
    "PollCount": {
"Type": "counter",
        "Name": "PollCount",
        "Description": "PollCount is quantity of metrics collection iteration.",
        "Value": 3
    },
    "TotalMemory": {
"Type": "gauge",
        "Name": "TotalMemory",
        "Description": "Total amount of RAM on this system",
        "Value": 16054480896
    }
}
"""

input_metrics_tbl_crete = (Query.create_table("input_metrics").columns(
    Column("id", "VARCHAR", nullable=False),
    Column("text_json", "VARCHAR", nullable=False),
    Column("update_dt", "TIMESTAMPTZ", nullable=True)).primary_key("id").if_not_exists())

input_metrics = Table('input_metrics')


class SimpleORM:
    async def migration(self):
        logging.info(f"migrations: PG_CONN_STRING: {PG_CONN_STRING}")
        logging.info(f"migrations: Скрипт создания таблиц: {input_metrics_tbl_crete}")
        sql_list = [str(input_metrics_tbl_crete)]
        await sql_exec_transaction(sql_list)

        q = Query.from_(input_metrics).select(functions.Count("*"))
        res = await sql_get_cursor(q.get_sql())
        cnt = res[0]

        if int(cnt) == 0:
            t_s = datetime.datetime.now(tz=datetime.timezone.utc)
            event_date = str(t_s.isoformat(sep=' ', timespec='milliseconds'))
            metrics_insert = input_metrics.insert('all',
                                                  "{}",
                                                  event_date
                                                  )
            await sql_exec_transaction([metrics_insert.get_sql()])

    async def metrics_register(self, json_data: str, metric_id: str):
        t_s = datetime.datetime.now(tz=datetime.timezone.utc)
        event_date = str(t_s.isoformat(sep=' ', timespec='milliseconds'))

        metrics_update = (input_metrics.update().set(input_metrics.text_json, json_data).
                          set(input_metrics.update_dt, event_date).where(input_metrics.id == metric_id))

        await sql_exec_transaction([metrics_update.get_sql()])
        return 0

    async def metrics_get(self, metric_id: str):
        q = Query.from_(input_metrics).select(input_metrics.text_json).where(input_metrics.id == metric_id)
        res = await sql_get_cursor(q.get_sql())
        return res[0]

""""
async def main():
    orm = SimpleORM()
    await orm.migration()
    await orm.metrics_register(json_data=data, metric_id='all')
    await orm.metrics_get(metric_id='all')

asyncio.run(main())
"""
