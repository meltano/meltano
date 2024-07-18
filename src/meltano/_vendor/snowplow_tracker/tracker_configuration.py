# """
#     tracker_configuration.py

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

from typing import Optional
from meltano._vendor.snowplow_tracker.typing import JsonEncoderFunction


class TrackerConfiguration(object):
    def __init__(
        self,
        encode_base64: Optional[bool] = None,
        json_encoder: Optional[JsonEncoderFunction] = None,
    ) -> None:
        """
        Configuration for additional tracker configuration options.
        :param encode_base64:     Whether JSONs in the payload should be base-64 encoded. Default is True.
        :type  encode_base64:     bool
        :param json_encoder:      Custom JSON serializer that gets called on non-serializable object.
        :type  json_encoder:      function | None
        """

        self.encode_base64 = encode_base64
        self.json_encoder = json_encoder

    @property
    def encode_base64(self) -> Optional[bool]:
        """
        Whether JSONs in the payload should be base-64 encoded. Default is True.
        """
        return self._encode_base64

    @encode_base64.setter
    def encode_base64(self, value: Optional[bool]):
        if isinstance(value, bool) or value is None:
            self._encode_base64 = value
        else:
            raise ValueError("encode_base64 must be True or False")

    @property
    def json_encoder(self) -> Optional[JsonEncoderFunction]:
        """
        Custom JSON serializer that gets called on non-serializable object.
        """
        return self._json_encoder

    @json_encoder.setter
    def json_encoder(self, value: Optional[JsonEncoderFunction]):
        self._json_encoder = value
