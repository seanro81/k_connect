import asyncpg


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


if __name__ == "__main__":
    
