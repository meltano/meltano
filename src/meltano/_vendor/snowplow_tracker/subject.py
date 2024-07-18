# """
#     subject.py

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
from meltano._vendor.snowplow_tracker.contracts import one_of, greater_than
from meltano._vendor.snowplow_tracker.typing import SupportedPlatform, SUPPORTED_PLATFORMS, PayloadDict

DEFAULT_PLATFORM = "pc"


class Subject(object):
    """
    Class for an event subject, where we view events as of the form

    (Subject) -> (Verb) -> (Object)
    """

    def __init__(self) -> None:
        self.standard_nv_pairs = {"p": DEFAULT_PLATFORM}

    def set_platform(self, value: SupportedPlatform) -> "Subject":
        """
        :param  value:          One of ["pc", "tv", "mob", "cnsl", "iot", "web", "srv", "app"]
        :type   value:          supported_platform
        :rtype:                 subject
        """
        one_of(value, SUPPORTED_PLATFORMS)

        self.standard_nv_pairs["p"] = value
        return self

    def set_user_id(self, user_id: str) -> "Subject":
        """
        :param  user_id:        User ID
        :type   user_id:        string
        :rtype:                 subject
        """
        self.standard_nv_pairs["uid"] = user_id
        return self

    def set_screen_resolution(self, width: int, height: int) -> "Subject":
        """
        :param  width:          Width of the screen
        :param  height:         Height of the screen
        :type   width:          int,>0
        :type   height:         int,>0
        :rtype:                 subject
        """
        greater_than(width, 0)
        greater_than(height, 0)

        self.standard_nv_pairs["res"] = "".join([str(width), "x", str(height)])
        return self

    def set_viewport(self, width: int, height: int) -> "Subject":
        """
        :param  width:          Width of the viewport
        :param  height:         Height of the viewport
        :type   width:          int,>0
        :type   height:         int,>0
        :rtype:                 subject
        """
        greater_than(width, 0)
        greater_than(height, 0)

        self.standard_nv_pairs["vp"] = "".join([str(width), "x", str(height)])
        return self

    def set_color_depth(self, depth: int) -> "Subject":
        """
        :param  depth:          Depth of the color on the screen
        :type   depth:          int
        :rtype:                 subject
        """
        self.standard_nv_pairs["cd"] = depth
        return self

    def set_timezone(self, timezone: str) -> "Subject":
        """
        :param  timezone:       Timezone as a string
        :type   timezone:       string
        :rtype:                 subject
        """
        self.standard_nv_pairs["tz"] = timezone
        return self

    def set_lang(self, lang: str) -> "Subject":
        """
        Set language.

        :param  lang:           Language the application is set to
        :type   lang:           string
        :rtype:                 subject
        """
        self.standard_nv_pairs["lang"] = lang
        return self

    def set_domain_user_id(self, duid: str) -> "Subject":
        """
        Set the domain user ID

        :param duid:            Domain user ID
        :type  duid:            string
        :rtype:                 subject
        """
        self.standard_nv_pairs["duid"] = duid
        return self

    def set_domain_session_id(self, sid: str) -> "Subject":
        """
        Set the domain session ID
        :param sid:             Domain session ID
        :type  sid:             string
        :rtype:                 subject
        """
        self.standard_nv_pairs["sid"] = sid
        return self

    def set_domain_session_index(self, vid: int) -> "Subject":
        """
        Set the domain session Index
        :param vid:             Domain session Index
        :type vid:              int
        :rtype:                 subject
        """
        self.standard_nv_pairs["vid"] = vid
        return self

    def set_ip_address(self, ip: str) -> "Subject":
        """
        Set the domain user ID

        :param ip:              IP address
        :type  ip:              string
        :rtype:                 subject
        """
        self.standard_nv_pairs["ip"] = ip
        return self

    def set_useragent(self, ua: str) -> "Subject":
        """
        Set the user agent

        :param ua:              User agent
        :type  ua:              string
        :rtype:                 subject
        """
        self.standard_nv_pairs["ua"] = ua
        return self

    def set_network_user_id(self, nuid: str) -> "Subject":
        """
        Set the network user ID field
        This overwrites the nuid field set by the collector

        :param nuid:            Network user ID
        :type  nuid:            string
        :rtype:                 subject
        """
        self.standard_nv_pairs["tnuid"] = nuid
        return self

    def combine_subject(self, subject: Optional["Subject"]) -> PayloadDict:
        """
        Merges another instance of Subject, with self taking priority
        :param  subject     Subject to update
        :type   subject     subject
        :rtype              PayloadDict

        """
        if subject is not None:
            return {**subject.standard_nv_pairs, **self.standard_nv_pairs}

        return self.standard_nv_pairs
