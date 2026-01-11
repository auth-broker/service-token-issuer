import asyncio
import contextlib
import json
from collections.abc import AsyncGenerator, AsyncIterator, Generator, Iterator
from typing import TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, SecretStr

T = TypeVar("T")
_SENTINEL = object()


def async_iter_from_sync_gen(
    gen: Iterator[T],
    *,
    maxsize: int = 16,
) -> AsyncIterator[T]:
    """Return an async generator that streams from a sync generator running in one background thread."""

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


def sse_data_from_model(
    model: BaseModel,
    *,
    expose_secrets: bool = False,
):
    if expose_secrets:
        payload = jsonable_encoder(
            model.model_dump(mode="python"),
            custom_encoder={SecretStr: lambda s: s.get_secret_value()},
        )
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    return model.model_dump_json()


def sse_lines_from_models(
    models: Iterator[BaseModel],
    *,
    expose_secrets: bool = False,
) -> Generator[str, None, None]:
    """Convert an async stream of BaseModels into SSE lines."""
    for m in models:
        data = sse_data_from_model(m, expose_secrets=expose_secrets)
        yield f"data: {data}\n\n"


async def sse_lines_from_models_async(
    models: AsyncIterator[BaseModel],
    *,
    expose_secrets: bool = False,
) -> AsyncGenerator[str, None]:
    """Convert an async stream of BaseModels into SSE lines."""
    async for m in models:
        data = sse_data_from_model(m, expose_secrets=expose_secrets)
        yield f"data: {data}\n\n"
