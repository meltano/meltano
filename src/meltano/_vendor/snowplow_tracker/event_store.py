# """
#     event_store.py

#     Copyright (c) 2013-2023 Snowplow Analytics Ltd. All rights reserved.

#     This program is licensed to you under the Apache License Version 2.0,
#     and you may not use this file except in compliance with the Apache License
#     Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
#     http://www.apache.org/licenses/LICENSE-2.0.

#     Unless required by applicable law or agreed to in writing,
#     software distributed under the Apache License Version 2.0 is distributed on
#     an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#     express or implied. See the Apache License Version 2.0 for the specific
#     language governing permissions and limitations there under.
# """

from typing_extensions import Protocol
from meltano._vendor.snowplow_tracker.typing import PayloadDict, PayloadDictList
from logging import Logger


class EventStore(Protocol):
    """
    EventStore protocol. For buffering events in the Emitter.
    """

    def add_event(payload: PayloadDict) -> bool:
        """
        Add PayloadDict to buffer. Returns True if successful.

        :param payload: The payload to add
        :type  payload: PayloadDict
        :rtype  bool
        """
        ...

    def get_events_batch() -> PayloadDictList:
        """
        Get a list of all the PayloadDicts in the buffer.

        :rtype  PayloadDictList
        """
        ...

    def cleanup(batch: PayloadDictList, need_retry: bool) -> None:
        """
        Removes sent events from the event store. If events need to be retried they are re-added to the buffer.

        :param  batch:  The events to be removed from the buffer
        :type   batch:  PayloadDictList
        :param  need_retry  Whether the events should be re-sent or not
        :type   need_retry  bool
        """
        ...

    def size() -> int:
        """
        Returns the number of events in the buffer

        :rtype  int
        """
        ...


class InMemoryEventStore(EventStore):
    """
    Create a InMemoryEventStore object with custom buffer capacity. The default is 10,000 events.
    """

    def __init__(self, logger: Logger, buffer_capacity: int = 10000) -> None:
        """
        :param  logger: Logging module
        :type   logger: Logger
        :param  buffer_capacity:    The maximum capacity of the event buffer.
                                    When the buffer is full new events are lost.
        :type   buffer_capacity     int
        """
        self.event_buffer = []
        self.buffer_capacity = buffer_capacity
        self.logger = logger

    def add_event(self, payload: PayloadDict) -> bool:
        """
        Add PayloadDict to buffer.

        :param payload: The payload to add
        :type  payload: PayloadDict
        """
        if self._buffer_capacity_reached():
            self.logger.error("Event buffer is full, dropping event.")
            return False

        self.event_buffer.append(payload)
        return True

    def get_events_batch(self) -> PayloadDictList:
        """
        Get a list of all the PayloadDicts in the in the buffer.

        :rtype  PayloadDictList
        """
        batch = self.event_buffer
        self.event_buffer = []
        return batch

    def cleanup(self, batch: PayloadDictList, need_retry: bool) -> None:
        """
        Removes sent events from the InMemoryEventStore buffer. If events need to be retried they are re-added to the buffer.

        :param  batch:  The events to be removed from the buffer
        :type   batch:  PayloadDictList
        :param  need_retry  Whether the events should be re-sent or not
        :type   need_retry  bool
        """
        if not need_retry:
            return

        for event in batch:
            if not event in self.event_buffer:
                if not self.add_event(event):
                    return

    def size(self) -> int:
        """
        Returns the number of events in the buffer

        :rtype  int
        """
        return len(self.event_buffer)

    def _buffer_capacity_reached(self) -> bool:
        """
        Returns true if buffer capacity is reached

        :rtype: bool
        """
        return self.size() >= self.buffer_capacity
