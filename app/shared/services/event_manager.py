from asyncio import Queue, QueueFull
from collections import defaultdict
from collections.abc import AsyncGenerator, Callable
from contextlib import suppress
from typing import Any

from app.entities.schemas.events.event import SEvent


class EventManager:
    _subscribers: dict[type[SEvent], list[Callable[[Any], None] | Queue[Any]]] = (
        defaultdict(list)
    )

    @classmethod
    def subscribe[T: SEvent](
        cls, event_type: type[T], sub: Callable[[T], None] | Queue[T]
    ) -> None:
        cls._subscribers[event_type].append(sub)

    @classmethod
    def unsubscribe[T: SEvent](
        cls, event_type: type[T], sub: Callable[[T], None] | Queue[T]
    ) -> None:
        # if callable(sub):
        #     sig = signature(sub)
        #     param = next(iter(sig.parameters.values()), None)
        #     ann = param.annotation if param else None
        #     event_type = ann if isinstance(ann, type) else None
        #     if event_type is None:
        #         return
        # else:
        #     for etype, lst in list(cls._subscribers.items()):
        #         if sub in lst:
        #             lst.remove(sub)
        #             if not lst:
        #                 del cls._subscribers[etype]
        #     return
        # lst = cls._subscribers.get(event_type)
        # if lst and sub in lst:
        #     lst.remove(sub)
        #     if not lst:
        #         del cls._subscribers[event_type]

        lst = cls._subscribers[event_type]
        lst.remove(sub)
        if not lst:
            del cls._subscribers[event_type]

    @classmethod
    def notify(cls, event: SEvent) -> None:
        listeners = cls._subscribers.get(type(event))

        if not listeners:
            return

        for sub in listeners:
            if isinstance(sub, Queue):
                with suppress(QueueFull):
                    sub.put_nowait(event)
                continue
            sub(event)

    @classmethod
    def notify_no_data[T: SEvent](cls, event_type: type[T], event: SEvent) -> None:
        listeners = cls._subscribers.get(event_type)

        if not listeners:
            return

        for sub in listeners:
            if isinstance(sub, Queue):
                with suppress(QueueFull):
                    sub.put_nowait(event)
                continue
            sub(event)

    @classmethod
    def get_stream[T: SEvent](
        cls,
        event_type: type[T],
        filter: Callable[[T], bool],
    ) -> AsyncGenerator[str, Any]:
        queue = Queue[T]()
        cls.subscribe(event_type, queue)

        async def generator():
            try:
                while True:
                    log = await queue.get()
                    if filter(log):
                        yield f"data: {log.model_dump_json()}\n\n"
            finally:
                cls.unsubscribe(event_type, queue)

        return generator()