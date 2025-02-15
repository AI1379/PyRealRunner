#
# Created by Renatus Madrigal on 02/15/2025
#

import asyncio
import threading
from typing import Coroutine, Generator, Any, Callable, AsyncGenerator, Dict
from contextlib import contextmanager
from queue import Queue
from concurrent.futures import Future


def singleton(cls):
    instances = {}

    def _singleton(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton


@singleton
class EventBridge:
    def __init__(self):
        self._events: Dict[str, asyncio.Event] = {}

    async def wait_signal(self, message: str):
        await self._events[message].wait()

    def register(self, message: str):
        self._events[message] = asyncio.Event()

    def set_signal(self, message):
        self._events[message].set()


def loop_set_debug(loop: asyncio.AbstractEventLoop):
    loop.set_debug(True)
    loop.set_task_factory(
        lambda loop, coro: asyncio.Task(
            coro,
            loop=loop,
            name=coro.__name__
        )
    )


def async_run_in_thread(coro: Coroutine, name: str = None):
    def _thread_main():
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
        finally:
            loop.close()

    thread = threading.Thread(target=_thread_main, name=name)
    thread.start()
    return thread


def thread_run_with_future(coro: Coroutine, name: str = None) -> Future:
    future = Future()

    async def _wrap():
        try:
            result = await coro
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)

    async_run_in_thread(_wrap(), name)
    return future


def run_in_thread(name: str = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            coro = func(*args, **kwargs)
            return async_run_in_thread(coro, name)
        return wrapper
    return decorator


def thread_with_future(name: str = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            coro = func(*args, **kwargs)
            return thread_run_with_future(coro, name)
        return wrapper
    return decorator
