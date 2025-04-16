from dataclasses import dataclass

import asyncpg


@dataclass
class ItemEntry:
    item_id: int
    user_id: int
    title: str
    description: str


class ItemStorage:
    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        # We initialize client here, because we need to connect it,
        # __init__ method doesn't support awaits.
        #
        # Pool will be configured using env variables.
        self._pool = await asyncpg.create_pool()

    async def disconnect(self) -> None:
        # Connections should be gracefully closed on app exit to avoid
        # resource leaks.
        await self._pool.close()

    async def create_tables_structure(self) -> None:
        """
        Создайте таблицу items со следующими колонками:
         item_id (int) - обязательное поле, значения должны быть уникальными
         user_id (int) - обязательное поле
         title (str) - обязательное поле
         description (str) - обязательное поле
        """
        # In production environment we will use migration tool
        # like https://github.com/pressly/goose
        async with self._pool.acquire() as connection:
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    item_id BIGINT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL
                )
            ''')

    async def save_items(self, items: list[ItemEntry]) -> None:
        """
        Напишите код для вставки записей в таблицу items одним запросом, цикл
        использовать нельзя.
        """
        # Don't use str-formatting, query args should be escaped to avoid
        # sql injections https://habr.com/ru/articles/148151/.
        it1 = []
        for i in items:
            it1.append({'item_id': i.item_id, 'user_id': i.user_id, 
                        'title': i.title, 'description': i.description})
        async with self._pool.acquire() as connection:      
            await connection.executemany('''
            INSERT INTO items (item_id, user_id, title, description)
            VALUES ($1, $2, $3, $4)
            ''', [(it1[i]['item_id'], it1[i]['user_id'], it1[i]['title'], it1[i]['description'])
                  for i in range(len(it1))])
            

    async def find_similar_items(
        self, user_id: int, title: str, description: str
    ) -> list[ItemEntry]:
        """
        Напишите код для поиска записей, имеющих указанные user_id, title и description.
        """
        async with self._pool.acquire() as connection:
            result = await connection.fetch('''SELECT item_id FROM items 
                                   WHERE
                                        user_id = $1
                                        and title = $2
                                        and description = $3 

            ''', user_id, title, description)
            res_list = []
            for i in result:
                res_list.append(ItemEntry(item_id=i[0], user_id=None, title=None, description=None))
            return res_list