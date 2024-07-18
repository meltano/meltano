# """
#     __init__.py

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
from meltano._vendor.snowplow_tracker.events.event import Event
from meltano._vendor.snowplow_tracker.events.page_ping import PagePing
from meltano._vendor.snowplow_tracker.events.page_view import PageView
from meltano._vendor.snowplow_tracker.events.self_describing import SelfDescribing
from meltano._vendor.snowplow_tracker.events.structured_event import StructuredEvent
from meltano._vendor.snowplow_tracker.events.screen_view import ScreenView
