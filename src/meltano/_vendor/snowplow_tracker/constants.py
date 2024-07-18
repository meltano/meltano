# """
#     constants.py

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
from typing import List
from meltano._vendor.snowplow_tracker import _version, SelfDescribingJson

VERSION = "py-%s" % _version.__version__
DEFAULT_ENCODE_BASE64 = True
BASE_SCHEMA_PATH = "iglu:com.snowplowanalytics.snowplow"
MOBILE_SCHEMA_PATH = "iglu:com.snowplowanalytics.mobile"
SCHEMA_TAG = "jsonschema"
CONTEXT_SCHEMA = "%s/contexts/%s/1-0-1" % (BASE_SCHEMA_PATH, SCHEMA_TAG)
UNSTRUCT_EVENT_SCHEMA = "%s/unstruct_event/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG)
ContextArray = List[SelfDescribingJson]
