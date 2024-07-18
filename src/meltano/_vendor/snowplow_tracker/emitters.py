# """
#     emitters.py

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

import logging
import time
import threading
import requests
import random
from typing import Optional, Union, Tuple, Dict
from queue import Queue

from meltano._vendor.snowplow_tracker.self_describing_json import SelfDescribingJson
from meltano._vendor.snowplow_tracker.typing import (
    PayloadDict,
    PayloadDictList,
    HttpProtocol,
    Method,
    SuccessCallback,
    FailureCallback,
)
from meltano._vendor.snowplow_tracker.contracts import one_of
from meltano._vendor.snowplow_tracker.event_store import EventStore, InMemoryEventStore

# logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_MAX_LENGTH = 10
PAYLOAD_DATA_SCHEMA = (
    "iglu:com.snowplowanalytics.snowplow/payload_data/jsonschema/1-0-4"
)
PROTOCOLS = {"http", "https"}
METHODS = {"get", "post"}


class Emitter(object):
    """
    Synchronously send Snowplow events to a Snowplow collector
    Supports both GET and POST requests
    """

    def __init__(
        self,
        endpoint: str,
        protocol: HttpProtocol = "https",
        port: Optional[int] = None,
        method: Method = "post",
        batch_size: Optional[int] = None,
        on_success: Optional[SuccessCallback] = None,
        on_failure: Optional[FailureCallback] = None,
        byte_limit: Optional[int] = None,
        request_timeout: Optional[Union[float, Tuple[float, float]]] = None,
        max_retry_delay_seconds: int = 60,
        buffer_capacity: Optional[int] = None,
        custom_retry_codes: Dict[int, bool] = {},
        event_store: Optional[EventStore] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        """
        :param endpoint:    The collector URL. If protocol is not set in endpoint it will automatically set to "https://" - this is done automatically.
        :type  endpoint:    string
        :param protocol:    The protocol to use - http or https. Defaults to https.
        :type  protocol:    protocol
        :param port:        The collector port to connect to
        :type  port:        int | None
        :param method:      The HTTP request method. Defaults to post.
        :type  method:      method
        :param batch_size:  The maximum number of queued events before the buffer is flushed. Default is 10.
        :type  batch_size:  int | None
        :param on_success:  Callback executed after every HTTP request in a flush has status code 200
                            Gets passed the number of events flushed.
        :type  on_success:  function | None
        :param on_failure:  Callback executed if at least one HTTP request in a flush has status code other than 200
                            Gets passed two arguments:
                            1) The number of events which were successfully sent
                            2) If method is "post": The unsent data in string form;
                               If method is "get":  An array of dictionaries corresponding to the unsent events' payloads
        :type  on_failure:  function | None
        :param byte_limit:  The size event list after reaching which queued events will be flushed
        :type  byte_limit:  int | None
        :param request_timeout: Timeout for the HTTP requests. Can be set either as single float value which
                                 applies to both "connect" AND "read" timeout, or as tuple with two float values
                                 which specify the "connect" and "read" timeouts separately
        :type request_timeout:  float | tuple | None
        :param max_retry_delay_seconds:     Set the maximum time between attempts to send failed events to the collector. Default 60 seconds
        :type max_retry_delay_seconds:      int
        :param buffer_capacity: The maximum capacity of the event buffer.
                                When the buffer is full new events are lost.
        :type buffer_capacity: int
        :param  custom_retry_codes: Set custom retry rules for HTTP status codes received in emit responses from the Collector.
                                    By default, retry will not occur for status codes 400, 401, 403, 410 or 422. This can be overridden here.
                                    Note that 2xx codes will never retry as they are considered successful.
        :type   custom_retry_codes: dict
        :param  event_store:    Stores the event buffer and buffer capacity. Default is an InMemoryEventStore object with buffer_capacity of 10,000 events.
        :type   event_store:    EventStore | None
        :param  session:    Persist parameters across requests by using a session object
        :type   session:    requests.Session | None
        """
        one_of(protocol, PROTOCOLS)
        one_of(method, METHODS)

        self.endpoint = Emitter.as_collector_uri(endpoint, protocol, port, method)

        self.method = method

        if event_store is None:
            if buffer_capacity is None:
                event_store = InMemoryEventStore(logger=logger)
            else:
                event_store = InMemoryEventStore(
                    buffer_capacity=buffer_capacity, logger=logger
                )

        self.event_store = event_store

        if batch_size is None:
            if method == "post":
                batch_size = DEFAULT_MAX_LENGTH
            else:
                batch_size = 1

        if buffer_capacity is not None and batch_size > buffer_capacity:
            batch_size = buffer_capacity

        self.batch_size = batch_size
        self.byte_limit = byte_limit
        self.bytes_queued = None if byte_limit is None else 0
        self.request_timeout = request_timeout

        self.on_success = on_success
        self.on_failure = on_failure

        self.lock = threading.RLock()

        self.timer = FlushTimer(emitter=self, repeating=True)
        self.retry_timer = FlushTimer(emitter=self, repeating=False)

        self.max_retry_delay_seconds = max_retry_delay_seconds
        self.retry_delay = 0

        self.custom_retry_codes = custom_retry_codes
        logger.info("Emitter initialized with endpoint " + self.endpoint)

        self.request_method = requests if session is None else session

    @staticmethod
    def as_collector_uri(
        endpoint: str,
        protocol: HttpProtocol = "https",
        port: Optional[int] = None,
        method: Method = "post",
    ) -> str:
        """
        :param endpoint:  The raw endpoint provided by the user
        :type  endpoint:  string
        :param protocol:  The protocol to use - http or https
        :type  protocol:  protocol
        :param port:      The collector port to connect to
        :type  port:      int | None
        :param method:    Either `get` or `post` HTTP method
        :type  method:    method
        :rtype:           string
        """
        if len(endpoint) < 1:
            raise ValueError("No endpoint provided.")

        endpoint = endpoint.rstrip("/")

        if endpoint.split("://")[0] in PROTOCOLS:
            endpoint_arr = endpoint.split("://")
            protocol = endpoint_arr[0]
            endpoint = endpoint_arr[1]

        if method == "get":
            path = "/i"
        else:
            path = "/com.snowplowanalytics.snowplow/tp2"
        if port is None:
            return protocol + "://" + endpoint + path
        else:
            return protocol + "://" + endpoint + ":" + str(port) + path

    def input(self, payload: PayloadDict) -> None:
        """
        Adds an event to the buffer.
        If the maximum size has been reached, flushes the buffer.

        :param payload:   The name-value pairs for the event
        :type  payload:   dict(string:\\*)
        """
        with self.lock:
            if self.bytes_queued is not None:
                self.bytes_queued += len(str(payload))

            if self.method == "post":
                self.event_store.add_event({key: str(payload[key]) for key in payload})
            else:
                self.event_store.add_event(payload)

            if self.reached_limit():
                self.flush()

    def reached_limit(self) -> bool:
        """
        Checks if event-size or bytes limit are reached

        :rtype: bool
        """
        if self.byte_limit is None:
            return self.event_store.size() >= self.batch_size
        else:
            return (
                self.bytes_queued or 0
            ) >= self.byte_limit or self.event_store.size() >= self.batch_size

    def flush(self) -> None:
        """
        Sends all events in the buffer to the collector.
        """
        with self.lock:
            if self.retry_timer.is_active():
                return
            send_events = self.event_store.get_events_batch()
            self.send_events(send_events)
            if self.bytes_queued is not None:
                self.bytes_queued = 0

    def http_post(self, data: str) -> int:
        """
        :param data:  The array of JSONs to be sent
        :type  data:  string
        """
        logger.info("Sending POST request to %s..." % self.endpoint)
        logger.debug("Payload: %s" % data)
        try:
            r = self.request_method.post(
                self.endpoint,
                data=data,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=self.request_timeout,
            )
        except requests.RequestException as e:
            logger.warning(e)
            return -1

        return r.status_code

    def http_get(self, payload: PayloadDict) -> int:
        """
        :param payload:  The event properties
        :type  payload:  dict(string:\\*)
        """
        logger.info("Sending GET request to %s..." % self.endpoint)
        logger.debug("Payload: %s" % payload)
        try:
            r = self.request_method.get(
                self.endpoint, params=payload, timeout=self.request_timeout
            )
        except requests.RequestException as e:
            logger.warning(e)
            return -1

        return r.status_code

    def sync_flush(self) -> None:
        """
        Calls the flush method of the base Emitter class.
        This is guaranteed to be blocking, not asynchronous.
        """
        logger.debug("Starting synchronous flush...")
        self.flush()
        logger.info("Finished synchronous flush")

    @staticmethod
    def is_good_status_code(status_code: int) -> bool:
        """
        :param status_code:  HTTP status code
        :type  status_code:  int
        :rtype:              bool
        """
        return 200 <= status_code < 300

    def send_events(self, evts: PayloadDictList) -> None:
        """
        :param evts: Array of events to be sent
        :type  evts: list(dict(string:\\*))
        """
        if len(evts) > 0:
            logger.info("Attempting to send %s events" % len(evts))

            Emitter.attach_sent_timestamp(evts)
            success_events = []
            failure_events = []

            if self.method == "post":
                data = SelfDescribingJson(PAYLOAD_DATA_SCHEMA, evts).to_string()
                status_code = self.http_post(data)
                request_succeeded = Emitter.is_good_status_code(status_code)
                if request_succeeded:
                    success_events += evts
                else:
                    failure_events += evts

            elif self.method == "get":
                for evt in evts:
                    status_code = self.http_get(evt)
                    request_succeeded = Emitter.is_good_status_code(status_code)

                    if request_succeeded:
                        success_events += [evt]
                    else:
                        failure_events += [evt]

            if self.on_success is not None and len(success_events) > 0:
                self.on_success(success_events)
            if self.on_failure is not None and len(failure_events) > 0:
                self.on_failure(len(success_events), failure_events)

            if self._should_retry(status_code):
                self._set_retry_delay()
                self._retry_failed_events(failure_events)
            else:
                self.event_store.cleanup(success_events, False)
                self._reset_retry_delay()
        else:
            logger.info("Skipping flush since buffer is empty")

    def _set_retry_timer(self, timeout: float) -> None:
        """
        Set an interval at which failed events will be retried

        :param timeout:   interval in seconds
        :type  timeout:   int | float
        """
        self.retry_timer.start(timeout=timeout)

    def set_flush_timer(self, timeout: float) -> None:
        """
        Set an interval at which the buffer will be flushed
        :param timeout:   interval in seconds
        :type  timeout:   int | float
        """
        self.timer.start(timeout=timeout)

    def cancel_flush_timer(self) -> None:
        """
        Abort automatic async flushing
        """
        self.timer.cancel()

    @staticmethod
    def attach_sent_timestamp(events: PayloadDictList) -> None:
        """
        Attach (by mutating in-place) current timestamp in milliseconds
        as `stm` param

        :param events: Array of events to be sent
        :type  events: list(dict(string:\\*))
        :rtype: None
        """

        def update(e: PayloadDict) -> None:
            e.update({"stm": str(int(time.time()) * 1000)})

        for event in events:
            update(event)

    def _should_retry(self, status_code: int) -> bool:
        """
        Checks if a request should be retried

        :param  status_code: Response status code
        :type   status_code: int
        :rtype: bool
        """
        if Emitter.is_good_status_code(status_code):
            return False

        if status_code in self.custom_retry_codes.keys():
            return self.custom_retry_codes[status_code]

        return status_code not in [400, 401, 403, 410, 422]

    def _set_retry_delay(self) -> None:
        """
        Sets a delay to retry failed events
        """
        random_noise = random.random()
        self.retry_delay = min(
            self.retry_delay * 2 + random_noise, self.max_retry_delay_seconds
        )

    def _reset_retry_delay(self) -> None:
        """
        Resets retry delay to 0
        """
        self.retry_delay = 0

    def _retry_failed_events(self, failed_events) -> None:
        """
        Adds failed events back to the buffer to retry

        :param  failed_events: List of failed events
        :type   List
        """
        self.event_store.cleanup(failed_events, True)
        self._set_retry_timer(self.retry_delay)

    def _cancel_retry_timer(self) -> None:
        """
        Cancels a retry timer
        """
        self.retry_timer.cancel()


class AsyncEmitter(Emitter):
    """
    Uses threads to send HTTP requests asynchronously
    """

    def __init__(
        self,
        endpoint: str,
        protocol: HttpProtocol = "http",
        port: Optional[int] = None,
        method: Method = "post",
        batch_size: Optional[int] = None,
        on_success: Optional[SuccessCallback] = None,
        on_failure: Optional[FailureCallback] = None,
        thread_count: int = 1,
        byte_limit: Optional[int] = None,
        request_timeout: Optional[Union[float, Tuple[float, float]]] = None,
        max_retry_delay_seconds: int = 60,
        buffer_capacity: int = None,
        custom_retry_codes: Dict[int, bool] = {},
        event_store: Optional[EventStore] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        """
        :param endpoint:    The collector URL. If protocol is not set in endpoint it will automatically set to "https://" - this is done automatically.
        :type  endpoint:    string
        :param protocol:    The protocol to use - http or https. Defaults to http.
        :type  protocol:    protocol
        :param port:        The collector port to connect to
        :type  port:        int | None
        :param method:      The HTTP request method
        :type  method:      method
        :param batch_size: The maximum number of queued events before the buffer is flushed. Default is 10.
        :type  batch_size: int | None
        :param on_success:  Callback executed after every HTTP request in a flush has status code 200
                            Gets passed the number of events flushed.
        :type  on_success:  function | None
        :param on_failure:  Callback executed if at least one HTTP request in a flush has status code other than 200
                            Gets passed two arguments:
                            1) The number of events which were successfully sent
                            2) If method is "post": The unsent data in string form;
                               If method is "get":  An array of dictionaries corresponding to the unsent events' payloads
        :type  on_failure:  function | None
        :param thread_count: Number of worker threads to use for HTTP requests
        :type  thread_count: int
        :param byte_limit:  The size event list after reaching which queued events will be flushed
        :type  byte_limit:  int | None
        :param max_retry_delay_seconds:     Set the maximum time between attempts to send failed events to the collector. Default 60 seconds
        :type max_retry_delay_seconds:      int
        :param buffer_capacity: The maximum capacity of the event buffer.
                                When the buffer is full new events are lost.
        :type buffer_capacity: int
        :param  event_store:    Stores the event buffer and buffer capacity. Default is an InMemoryEventStore object with buffer_capacity of 10,000 events.
        :type   event_store:    EventStore
        :param  session:    Persist parameters across requests by using a session object
        :type   session:    requests.Session | None
        """
        super(AsyncEmitter, self).__init__(
            endpoint=endpoint,
            protocol=protocol,
            port=port,
            method=method,
            batch_size=batch_size,
            on_success=on_success,
            on_failure=on_failure,
            byte_limit=byte_limit,
            request_timeout=request_timeout,
            max_retry_delay_seconds=max_retry_delay_seconds,
            buffer_capacity=buffer_capacity,
            custom_retry_codes=custom_retry_codes,
            event_store=event_store,
            session=session,
        )
        self.queue = Queue()
        for i in range(thread_count):
            t = threading.Thread(target=self.consume)
            t.daemon = True
            t.start()

    def sync_flush(self) -> None:
        while True:
            self.flush()
            self.queue.join()
            if self.event_store.size() < 1:
                break

    def flush(self) -> None:
        """
        Removes all dead threads, then creates a new thread which
        executes the flush method of the base Emitter class
        """
        with self.lock:
            self.queue.put(self.event_store.get_events_batch())
            if self.bytes_queued is not None:
                self.bytes_queued = 0

    def consume(self) -> None:
        while True:
            evts = self.queue.get()
            self.send_events(evts)
            self.queue.task_done()


class FlushTimer(object):
    """
    Internal class used by the Emitter to schedule flush calls for later.
    """

    def __init__(self, emitter: Emitter, repeating: bool):
        self.emitter = emitter
        self.repeating = repeating
        self.timer: Optional[threading.Timer] = None
        self.lock = threading.RLock()

    def start(self, timeout: float) -> bool:
        with self.lock:
            if self.timer is not None:
                return False
            else:
                self._schedule_timer(timeout=timeout)
                return True

    def cancel(self) -> None:
        with self.lock:
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None

    def is_active(self) -> bool:
        with self.lock:
            return self.timer is not None

    def _fire(self, timeout: float) -> None:
        with self.lock:
            if self.repeating:
                self._schedule_timer(timeout)
            else:
                self.timer = None

        self.emitter.flush()

    def _schedule_timer(self, timeout: float) -> None:
        self.timer = threading.Timer(timeout, self._fire, [timeout])
        self.timer.daemon = True
        self.timer.start()
