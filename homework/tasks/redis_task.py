import redis.asyncio as aredis


class UsersByTitleStorage:
    def __init__(self):
        self._client = aredis.StrictRedis()

    async def connect(self) -> None:
        # Redis client does not require explicit connect method
        pass

    async def disconnect(self) -> None:
        await self._client.aclose()

    async def save_item(self, user_id: int, title: str) -> None:
        await self._client.sadd(f"title:{title}", user_id)

    async def find_users_by_title(self, title: str) -> list[int]:
        user_ids = await self._client.smembers(f"title:{title}")
        return [int(user_id) for user_id in user_ids]
