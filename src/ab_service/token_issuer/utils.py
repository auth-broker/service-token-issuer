import asyncio
import contextlib
from collections.abc import AsyncGenerator, AsyncIterator, Generator, Iterator
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")
_SENTINEL = object()


def async_iter_from_sync_gen(
    gen: Iterator[T],
    *,
    maxsize: int = 16,
) -> AsyncIterator[T]:
    """Return an async generator that streams from a sync generator
    running in one background thread.
    """

    async def agen() -> AsyncIterator[T]:
        loop = asyncio.get_running_loop()
        q: asyncio.Queue[object] = asyncio.Queue(maxsize=maxsize)

        async def put(item: object) -> None:
            await q.put(item)

        def producer() -> None:
            try:
                for item in gen:
                    fut = asyncio.run_coroutine_threadsafe(put(item), loop)
                    fut.result()
            except BaseException as exc:
                fut = asyncio.run_coroutine_threadsafe(put(exc), loop)
                fut.result()
            finally:
                with contextlib.suppress(Exception):
                    close = getattr(gen, "close", None)
                    if callable(close):
                        close()
                fut = asyncio.run_coroutine_threadsafe(put(_SENTINEL), loop)
                fut.result()

        # kick off the producer thread and keep a handle to join later
        join_task = asyncio.create_task(asyncio.to_thread(producer))

        try:
            while True:
                item = await q.get()
                if item is _SENTINEL:
                    break
                if isinstance(item, BaseException):
                    raise item
                yield item  # type: ignore[misc]
        finally:
            with contextlib.suppress(Exception):
                await join_task

    return agen()


def sse_lines_from_models(models: Iterator[BaseModel]) -> Generator[str, None, None]:
    """Convert an async stream of BaseModels into SSE lines."""
    for m in models:
        yield f"data: {m.model_dump_json()}\n\n"


async def sse_lines_from_models_async(
    models: AsyncIterator[BaseModel],
) -> AsyncGenerator[str, None]:
    """Convert an async stream of BaseModels into SSE lines."""
    async for m in models:
        yield f"data: {m.model_dump_json()}\n\n"
