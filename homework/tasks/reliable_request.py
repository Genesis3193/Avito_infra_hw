import abc

import httpx


class ResultsObserver(abc.ABC):
    @abc.abstractmethod
    def observe(self, data: bytes) -> None: ...


class ResultsObserver(abc.ABC):
    @abc.abstractmethod
    def observe(self, data: bytes) -> None: ...


async def do_reliable_request(url: str, observer: ResultsObserver) -> None:
    """
    Одна из главных проблем распределённых систем - это ненадёжность связи.

    Ваша задача заключается в том, чтобы таким образом исправить этот код, чтобы он
    умел переживать возвраты ошибок и таймауты со стороны сервера, гарантируя
    успешный запрос (в реальной жизни такая гарантия невозможна, но мы чуть упростим себе задачу).

    Все успешно полученные результаты должны регистрироваться с помощью обсёрвера.
    """
    max_retries = 5
    timeout = httpx.Timeout(10.0, connect=60.0)  # Устанавливаем таймауты для запроса
    retries = 0

    while retries < max_retries:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.content
                observer.observe(data)
                return
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            print(f"Request failed: {exc}. Retrying...")
            retries += 1
            await asyncio.sleep(
                2**retries
            )  # Экспоненциальная задержка перед повторной попыткой

    raise Exception("Failed to complete the request after multiple retries")
