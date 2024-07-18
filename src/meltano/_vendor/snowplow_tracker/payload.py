# """
#     payload.py

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

import json
import base64
from typing import Any, Optional
from meltano._vendor.snowplow_tracker.typing import PayloadDict, JsonEncoderFunction


class Payload:
    def __init__(self, dict_: Optional[PayloadDict] = None) -> None:
        """
        Constructor
        """

        self.nv_pairs = {}

        if dict_ is not None:
            for f in dict_:
                self.nv_pairs[f] = dict_[f]

    """
    Methods to add to the payload
    """

    def add(self, name: str, value: Any) -> None:
        """
        Add a name value pair to the Payload object
        """
        if not (value == "" or value is None):
            self.nv_pairs[name] = value

    def add_dict(self, dict_: PayloadDict, base64: bool = False) -> None:
        """
        Add a dict of name value pairs to the Payload object

        :param  dict_:          Dictionary to be added to the Payload
        :type   dict_:          dict(string:\\*)
        """
        for f in dict_:
            self.add(f, dict_[f])

    def add_json(
        self,
        dict_: Optional[PayloadDict],
        encode_base64: bool,
        type_when_encoded: str,
        type_when_not_encoded: str,
        json_encoder: Optional[JsonEncoderFunction] = None,
    ) -> None:
        """
        Add an encoded or unencoded JSON to the payload

        :param  dict_:                  Custom context for the event
        :type   dict_:                  dict(string:\\*) | None
        :param  encode_base64:          If the payload is base64 encoded
        :type   encode_base64:          bool
        :param  type_when_encoded:      Name of the field when encode_base64 is set
        :type   type_when_encoded:      string
        :param  type_when_not_encoded:  Name of the field when encode_base64 is not set
        :type   type_when_not_encoded:  string
        :param json_encoder:            Custom JSON serializer that gets called on non-serializable object
        :type  json_encoder:            function | None
        """

        if dict_ is not None and dict_ != {}:

            json_dict = json.dumps(dict_, ensure_ascii=False, default=json_encoder)

            if encode_base64:
                encoded_dict = base64.urlsafe_b64encode(json_dict.encode("utf-8"))
                if not isinstance(encoded_dict, str):
                    encoded_dict = encoded_dict.decode("utf-8")
                self.add(type_when_encoded, encoded_dict)

            else:
                self.add(type_when_not_encoded, json_dict)

    def get(self) -> PayloadDict:
        """
        Returns the context dictionary from the Payload object
        """
        return self.nv_pairs
