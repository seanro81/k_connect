"""
 по усовию задания - не использовать ORM или отправлять контролируемые запросы к базе
 реализованно
   - Инициализирующая Миграция
   - Откат Миграции
   - Use Case к Базе
"""

from models.user import UserInfo, User, AuthInfo, Login
from adapters.pg import conn_context_postgres, sql_exec_transaction, sql_get_cursor
from utils.settings import PG_DSL, hash_bcr
#from utils.genusers import gen_users
from pypika import Query, Table, Field, Column, functions, Order
from utils.settings import logger

users_tbl_crete = Query \
    .create_table("users") \
    .columns(
    Column("id", "UUID", nullable=False),
    Column("first_name", "VARCHAR", nullable=False),
    Column("second_name", "VARCHAR", nullable=False),
    Column("birthdate", "DATE", nullable=True),
    Column("biography", "VARCHAR", nullable=True),
    Column("city", "VARCHAR", nullable=True)) \
    .primary_key("id").if_not_exists()

authinfo_tbl_crete = Query \
    .create_table("authinfo") \
    .columns(
    Column("id", "UUID", nullable=False),
    Column("password", "VARCHAR", nullable=False),
    Column("token", "VARCHAR", nullable=False),
    Column("token_create_dt", "TIMESTAMPTZ", nullable=True),
    Column("token_valid_dt", "TIMESTAMPTZ", nullable=False)) \
    .primary_key("id").if_not_exists()

users = Table('users')
authinfo = Table('authinfo')


class SimpleORM:
    def migration(self):
        sql_list = [str(users_tbl_crete), str(authinfo_tbl_crete)]
        sql_exec_transaction(sql_list, PG_DSL)
        q = Query.from_(users).select(functions.Count("*"))
        res = sql_get_cursor(q.get_sql(), PG_DSL)
        cnt = res[0][0]
        if int(cnt) == 0:
            hashed_pwd = hash_bcr('password12345')

            user_insert = users.insert('6d082945-4db0-41cd-945f-da21e78f7da5',
                                       'Test',
                                       'Testov',
                                       '1990-01-01',
                                       'fake news',
                                       'Moscow')
            authinfo_insert = authinfo.insert('6d082945-4db0-41cd-945f-da21e78f7da5',
                                              str(hashed_pwd),
                                              '829fa770a0c82fbe6e4cd0644d419ebf14249a36',
                                              '2025-01-05 19:02:46.896 +0300',
                                              '2025-01-05 19:02:46.896 +0300')
            sql_exec_transaction([user_insert.get_sql(), authinfo_insert.get_sql()], PG_DSL)
            #gen_users()

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

    def get_user_info_by_id(self, id: str) -> UserInfo | None:
        q = Query.from_(users).select(users.id,
                                      users.first_name,
                                      users.second_name,
                                      users.birthdate,
                                      users.biography,
                                      users.city).where(users.id == id)
        user_info = sql_get_cursor(q.get_sql(), PG_DSL)
        if len(user_info) == 0:
            return None
        response = UserInfo(
            id=user_info[0][0],
            first_name=user_info[0][1],
            second_name=user_info[0][2],
            birthdate=user_info[0][3],
            biography=user_info[0][4],
            city=user_info[0][5],
        )
        return response

    def find_user_by_firstname_lastname(self, firstname: str, lastname: str) -> list[UserInfo] | None:
        name = f'{firstname}%'
        s_name = f'{lastname}%'
        q = Query.from_(users).select(users.id,
                                      users.first_name,
                                      users.second_name,
                                      users.birthdate,
                                      users.biography,
                                      users.city).where(users.first_name.like(name)).where(
            users.second_name.like(s_name)).orderby(users.id, order=Order.asc)
        logger.info(q.get_sql)
        user_info = sql_get_cursor(q.get_sql(), PG_DSL)
        if len(user_info) == 0:
            return []
        result = []
        for item in range(0, len(user_info)):
            find_user = UserInfo(
                id=user_info[item][0],
                first_name=user_info[item][1],
                second_name=user_info[item][2],
                birthdate=user_info[item][3],
                biography=user_info[item][4],
                city=user_info[item][5],
            )
            result.append(find_user)
        return result

    def get_auth(self, id: str) -> AuthInfo | None:
        q = Query.from_(authinfo).select(authinfo.id,
                                         authinfo.password,
                                         authinfo.token,
                                         authinfo.token_create_dt,
                                         authinfo.token_valid_dt).where(authinfo.id == id)
        auth = sql_get_cursor(q.get_sql(), PG_DSL)
        if len(auth) == 0:
            return None
        response = AuthInfo(
            id=auth[0][0],
            password=auth[0][1],
            token=auth[0][2],
            token_create_dt=auth[0][3],
            token_valid_dt=auth[0][4]
        )
        return response
