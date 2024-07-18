# """
#     contracts.py

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

import traceback
import re
from typing import Any, Dict, Iterable, Callable, Sized
from meltano._vendor.snowplow_tracker.typing import FORM_TYPES, FORM_NODE_NAMES

_CONTRACTS_ENABLED = True
_MATCH_FIRST_PARAMETER_REGEX = re.compile(r"\(([\w.]+)[,)]")


def disable_contracts() -> None:
    global _CONTRACTS_ENABLED
    _CONTRACTS_ENABLED = False


def enable_contracts() -> None:
    global _CONTRACTS_ENABLED
    _CONTRACTS_ENABLED = True


def contracts_enabled() -> bool:
    global _CONTRACTS_ENABLED
    return _CONTRACTS_ENABLED


def greater_than(value: float, compared_to: float) -> None:
    if contracts_enabled() and value <= compared_to:
        raise ValueError(
            "{0} must be greater than {1}.".format(_get_parameter_name(), compared_to)
        )


def non_empty(seq: Sized) -> None:
    if contracts_enabled() and len(seq) == 0:
        raise ValueError("{0} is empty.".format(_get_parameter_name()))


def non_empty_string(s: str) -> None:
    if contracts_enabled() and type(s) is not str or not s:
        raise ValueError("{0} is empty.".format(_get_parameter_name()))


def one_of(value: Any, supported: Iterable) -> None:
    if contracts_enabled() and value not in supported:
        raise ValueError("{0} is not supported.".format(_get_parameter_name()))


def satisfies(value: Any, check: Callable[[Any], bool]) -> None:
    if contracts_enabled() and not check(value):
        raise ValueError("{0} is not allowed.".format(_get_parameter_name()))


def form_element(element: Dict[str, Any]) -> None:
    satisfies(element, lambda x: _check_form_element(x))


def _get_parameter_name() -> str:
    stack = traceback.extract_stack()
    _, _, _, code = stack[-3]

    match = _MATCH_FIRST_PARAMETER_REGEX.search(code)
    if not match:
        return "Unnamed parameter"
    return match.groups(0)[0]


def _check_form_element(element: Dict[str, Any]) -> bool:
    """
    Helper method to check that dictionary conforms element
    in sumbit_form and change_form schemas
    """
    all_present = (
        isinstance(element, dict)
        and "name" in element
        and "value" in element
        and "nodeName" in element
    )
    try:
        if element["type"] in FORM_TYPES:
            type_valid = True
        else:
            type_valid = False
    except KeyError:
        type_valid = True
    return all_present and element["nodeName"] in FORM_NODE_NAMES and type_valid
