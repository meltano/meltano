# """
#     self_describing_json.py

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
from typing import Union

from meltano._vendor.snowplow_tracker.typing import PayloadDict, PayloadDictList
from meltano._vendor.snowplow_tracker.contracts import non_empty_string


class SelfDescribingJson(object):
    def __init__(self, schema: str, data: Union[PayloadDict, PayloadDictList]) -> None:
        self.schema = schema
        self.data = data

    @property
    def schema(self) -> str:
        return self._schema

    @schema.setter
    def schema(self, value: str):
        non_empty_string(value)
        self._schema = value

    def to_json(self) -> PayloadDict:
        return {"schema": self.schema, "data": self.data}

    def to_string(self) -> str:
        return json.dumps(self.to_json())
