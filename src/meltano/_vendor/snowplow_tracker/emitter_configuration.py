# """
#     emitter_configuration.py

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

from typing import Optional, Union, Tuple, Dict
from meltano._vendor.snowplow_tracker.typing import SuccessCallback, FailureCallback
from meltano._vendor.snowplow_tracker.event_store import EventStore
import requests


class EmitterConfiguration(object):
    def __init__(
        self,
        batch_size: Optional[int] = None,
        on_success: Optional[SuccessCallback] = None,
        on_failure: Optional[FailureCallback] = None,
        byte_limit: Optional[int] = None,
        request_timeout: Optional[Union[float, Tuple[float, float]]] = None,
        buffer_capacity: Optional[int] = None,
        custom_retry_codes: Dict[int, bool] = {},
        event_store: Optional[EventStore] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        """
        Configuration for the emitter that sends events to the Snowplow collector.
        :param batch_size:     The maximum number of queued events before the buffer is flushed. Default is 10.
        :type  batch_size:     int | None
        :param on_success:      Callback executed after every HTTP request in a flush has status code 200
                                Gets passed the number of events flushed.
        :type  on_success:      function | None
        :param on_failure:      Callback executed if at least one HTTP request in a flush has status code other than 200
                                Gets passed two arguments:
                                1) The number of events which were successfully sent
                                2) If method is "post": The unsent data in string form;
                                   If method is "get":  An array of dictionaries corresponding to the unsent events' payloads
        :type  on_failure:      function | None
        :param byte_limit:      The size event list after reaching which queued events will be flushed
        :type  byte_limit:      int | None
        :param request_timeout: Timeout for the HTTP requests. Can be set either as single float value which
                                 applies to both "connect" AND "read" timeout, or as tuple with two float values
                                 which specify the "connect" and "read" timeouts separately
        :type request_timeout:  float | tuple | None
        :param  custom_retry_codes: Set custom retry rules for HTTP status codes received in emit responses from the Collector.
                                    By default, retry will not occur for status codes 400, 401, 403, 410 or 422. This can be overridden here.
                                    Note that 2xx codes will never retry as they are considered successful.
        :type   custom_retry_codes: dict
        :param  event_store:    Stores the event buffer and buffer capacity. Default is an InMemoryEventStore object with buffer_capacity of 10,000 events.
        :type   event_store:    EventStore | None
        :param  session:    Persist parameters across requests by using a session object
        :type   session:    request.Session | None
        """

        self.batch_size = batch_size
        self.on_success = on_success
        self.on_failure = on_failure
        self.byte_limit = byte_limit
        self.request_timeout = request_timeout
        self.buffer_capacity = buffer_capacity
        self.custom_retry_codes = custom_retry_codes
        self.event_store = event_store
        self.session = session

    @property
    def batch_size(self) -> Optional[int]:
        """
        The maximum number of queued events before the buffer is flushed. Default is 10.
        """
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value: Optional[int]):
        if isinstance(value, int) and value < 0:
            raise ValueError("batch_size must greater than 0")
        if not isinstance(value, int) and value is not None:
            raise ValueError("batch_size must be of type int")
        self._batch_size = value

    @property
    def on_success(self) -> Optional[SuccessCallback]:
        """
        Callback executed after every HTTP request in a flush has status code 200. Gets passed the number of events flushed.
        """
        return self._on_success

    @on_success.setter
    def on_success(self, value: Optional[SuccessCallback]):
        self._on_success = value

    @property
    def on_failure(self) -> Optional[FailureCallback]:
        """
        Callback executed if at least one HTTP request in a flush has status code other than 200
                                Gets passed two arguments:
                                1) The number of events which were successfully sent
                                2) If method is "post": The unsent data in string form;
                                   If method is "get":  An array of dictionaries corresponding to the unsent events' payloads
        """
        return self._on_failure

    @on_failure.setter
    def on_failure(self, value: Optional[FailureCallback]):
        self._on_failure = value

    @property
    def byte_limit(self) -> Optional[int]:
        """
        The size event list after reaching which queued events will be flushed
        """
        return self._byte_limit

    @byte_limit.setter
    def byte_limit(self, value: Optional[int]):
        if isinstance(value, int) and value < 0:
            raise ValueError("byte_limit must greater than 0")
        if not isinstance(value, int) and value is not None:
            raise ValueError("byte_limit must be of type int")
        self._byte_limit = value

    @property
    def request_timeout(self) -> Optional[Union[float, Tuple[float, float]]]:
        """
        Timeout for the HTTP requests. Can be set either as single float value which
                                     applies to both "connect" AND "read" timeout, or as tuple with two float values
                                     which specify the "connect" and "read" timeouts separately
        """
        return self._request_timeout

    @request_timeout.setter
    def request_timeout(self, value: Optional[Union[float, Tuple[float, float]]]):
        self._request_timeout = value

    @property
    def buffer_capacity(self) -> Optional[int]:
        """
        The maximum capacity of the event buffer. The default buffer capacity is 10 000 events.
                                When the buffer is full new events are lost.
        """
        return self._buffer_capacity

    @buffer_capacity.setter
    def buffer_capacity(self, value: Optional[int]):
        if isinstance(value, int) and value < 0:
            raise ValueError("buffer_capacity must greater than 0")
        if not isinstance(value, int) and value is not None:
            raise ValueError("buffer_capacity must be of type int")
        self._buffer_capacity = value

    @property
    def custom_retry_codes(self) -> Dict[int, bool]:
        """
        Custom retry rules for HTTP status codes received in emit responses from the Collector.
        """
        return self._custom_retry_codes

    @custom_retry_codes.setter
    def custom_retry_codes(self, value: Dict[int, bool]):
        self._custom_retry_codes = value

    def set_retry_code(self, status_code: int, retry=True) -> bool:
        """
        Add a retry rule for HTTP status code received from emit responses from the Collector.
        :param  status_code:    HTTP response code
        :type   status_code:    int
        :param  retry:  Set the status_code to retry (True) or not retry (False). Default is True
        :type   retry:  bool
        """
        if not isinstance(status_code, int):
            print("status_code must be of type int")
            return False

        if not isinstance(retry, bool):
            print("retry must be of type bool")
            return False

        if 200 <= status_code < 300:
            print(
                "custom_retry_codes should not include codes for succesful requests (2XX codes)"
            )
            return False

        self.custom_retry_codes[status_code] = retry

        return status_code in self.custom_retry_codes.keys()

    @property
    def event_store(self) -> Optional[EventStore]:
        return self._event_store

    @event_store.setter
    def event_store(self, value: Optional[EventStore]):
        self._event_store = value

    @property
    def session(self) -> Optional[requests.Session]:
        """
        Persist parameters across requests using a requests.Session object
        """
        return self._session

    @session.setter
    def session(self, value: Optional[requests.Session]):
        self._session = value
