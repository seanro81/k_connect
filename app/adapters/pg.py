import asyncpg

from pypika import Query, Table, Field, Column, functions, Order


#postgres://someuser:somepassword@somehost:381/somedatabase
async def sql_exec_transaction(sql_list: list):
    conn = await asyncpg.connect('postgresql://postgres:pgpwd4habr@127.0.0.1:5432/postgres')
    # Execute a statement to create a new table.
    for item in sql_list:
        await conn.execute(item)
    await conn.close()


async def sql_get_cursor(query: str):
    conn = await asyncpg.connect('postgresql://postgres:pgpwd4habr@127.0.0.1:5432/postgres')
    rows = await conn.fetchrow(query)
    result = [dict(row) for row in rows]
    await conn.close()
    return result


"""
{
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


input_metrics_tbl_crete = Query \
    .create_table("input_metrics") \
    .columns(
    Column("id", "VARCHAR", nullable=False),
    Column("text_json", "VARCHAR", nullable=False),
    Column("last_update", "DATETIME", nullable=True))\
    .primary_key("id").if_not_exists()

input_metrics = Table('input_metrics')


class SimpleORM:
    def migration(self):
        sql_list = [str(input_metrics_tbl_crete)]
        sql_exec_transaction(sql_list)
       

    def user_register(self, user: User, auth: AuthInfo):
        user_insert = users.insert(user.id,
                                   user.first_name,
                                   user.second_name,
                                   str(user.birthdate),
                                   user.biography,
                                   user.city)
        authinfo_insert = authinfo.insert(user.id,
                                          auth.password,
                                          auth.token,
                                          str(auth.token_create_dt),
                                          str(auth.token_valid_dt))
        sql_exec_transaction([user_insert.get_sql(), authinfo_insert.get_sql()], PG_DSL)
        return 0




if __name__ == "__main__":
    
