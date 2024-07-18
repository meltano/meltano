# """
#     typing.py

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

from typing import Dict, List, Callable, Any, Optional, Union, Tuple
from typing_extensions import Protocol, Literal

PayloadDict = Dict[str, Any]
PayloadDictList = List[PayloadDict]
JsonEncoderFunction = Callable[[Any], Any]

# tracker
FORM_NODE_NAMES = {"INPUT", "TEXTAREA", "SELECT"}
FORM_TYPES = {
    "button",
    "checkbox",
    "color",
    "date",
    "datetime",
    "datetime-local",
    "email",
    "file",
    "hidden",
    "image",
    "month",
    "number",
    "password",
    "radio",
    "range",
    "reset",
    "search",
    "submit",
    "tel",
    "text",
    "time",
    "url",
    "week",
}
FormNodeName = Literal["INPUT", "TEXTAREA", "SELECT"]
ElementClasses = Union[List[str], Tuple[str, Any]]
FormClasses = Union[List[str], Tuple[str, Any]]

# emitters
HttpProtocol = Literal["http", "https"]
Method = Literal["get", "post"]
SuccessCallback = Callable[[PayloadDictList], None]
FailureCallback = Callable[[int, PayloadDictList], None]

# subject
SUPPORTED_PLATFORMS = {"pc", "tv", "mob", "cnsl", "iot", "web", "srv", "app"}
SupportedPlatform = Literal["pc", "tv", "mob", "cnsl", "iot", "web", "srv", "app"]


class EmitterProtocol(Protocol):
    def input(self, payload: PayloadDict) -> None:
        ...
