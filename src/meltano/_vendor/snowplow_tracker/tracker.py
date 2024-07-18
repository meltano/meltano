# """
#     tracker.py

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

import time
import uuid
from typing import Any, Optional, Union, List, Dict, Sequence
from warnings import warn

from meltano._vendor.snowplow_tracker import payload, SelfDescribingJson
from meltano._vendor.snowplow_tracker.subject import Subject
from meltano._vendor.snowplow_tracker.contracts import non_empty_string, one_of, non_empty, form_element
from meltano._vendor.snowplow_tracker.constants import (
    VERSION,
    DEFAULT_ENCODE_BASE64,
    BASE_SCHEMA_PATH,
    SCHEMA_TAG,
)

from meltano._vendor.snowplow_tracker.events import (
    Event,
    PagePing,
    PageView,
    SelfDescribing,
    StructuredEvent,
    ScreenView,
)
from meltano._vendor.snowplow_tracker.typing import (
    JsonEncoderFunction,
    EmitterProtocol,
    FORM_NODE_NAMES,
    FORM_TYPES,
    FormNodeName,
    ElementClasses,
    FormClasses,
)

"""
Tracker class
"""


class Tracker:
    def __init__(
        self,
        namespace: str,
        emitters: Union[List[EmitterProtocol], EmitterProtocol],
        subject: Optional[Subject] = None,
        app_id: Optional[str] = None,
        encode_base64: bool = DEFAULT_ENCODE_BASE64,
        json_encoder: Optional[JsonEncoderFunction] = None,
    ) -> None:
        """
        :param namespace:        Identifier for the Tracker instance
        :type  namespace:        string
        :param emitters:         Emitters to which events will be sent
        :type  emitters:         list[>0](emitter) | emitter
        :param subject:          Subject to be tracked
        :type  subject:          subject | None
        :param app_id:           Application ID
        :type  app_id:           string_or_none
        :param encode_base64:    Whether JSONs in the payload should be base-64 encoded
        :type  encode_base64:    bool
        :param json_encoder:     Custom JSON serializer that gets called on non-serializable object
        :type  json_encoder:     function | None
        """
        if subject is None:
            subject = Subject()

        if type(emitters) is list:
            non_empty(emitters)
            self.emitters = emitters
        else:
            self.emitters = [emitters]

        self.subject = subject
        self.encode_base64 = encode_base64
        self.json_encoder = json_encoder

        self.standard_nv_pairs = {"tv": VERSION, "tna": namespace, "aid": app_id}
        self.timer = None

    @staticmethod
    def get_uuid() -> str:
        """
        Set transaction ID for the payload once during the lifetime of the
        event.

        :rtype:           string
        """
        return str(uuid.uuid4())

    @staticmethod
    def get_timestamp(tstamp: Optional[float] = None) -> int:
        """
        :param tstamp:    User-input timestamp or None
        :type  tstamp:    int | float | None
        :rtype:           int
        """
        if isinstance(
            tstamp,
            (
                int,
                float,
            ),
        ):
            return int(tstamp)
        return int(time.time() * 1000)

    """
    Tracking methods
    """

    def track(
        self,
        event: Event,
    ) -> Optional[str]:
        """
        Send the event payload to a emitter. Returns the tracked event ID.
        :param  event:           Event
        :type   event:           events.Event
        :rtype:                  String
        """

        payload = self.complete_payload(
            event=event,
        )

        for emitter in self.emitters:
            emitter.input(payload.nv_pairs)

        if "eid" in payload.nv_pairs.keys():
            return payload.nv_pairs["eid"]

    def complete_payload(
        self,
        event: Event,
    ) -> payload.Payload:
        payload = event.build_payload(
            encode_base64=self.encode_base64,
            json_encoder=self.json_encoder,
            subject=self.subject,
        )

        payload.add("eid", Tracker.get_uuid())
        payload.add("dtm", Tracker.get_timestamp())
        payload.add_dict(self.standard_nv_pairs)

        return payload

    def track_page_view(
        self,
        page_url: str,
        page_title: Optional[str] = None,
        referrer: Optional[str] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  page_url:       URL of the viewed page
        :type   page_url:       non_empty_string
        :param  page_title:     Title of the viewed page
        :type   page_title:     string_or_none
        :param  referrer:       Referrer of the page
        :type   referrer:       string_or_none
        :param  context:        Custom context for the event
        :type   context:        context_array | None
        :param  tstamp:         Optional event timestamp in milliseconds
        :type   tstamp:         int | float | None
        :param  event_subject:  Optional per event subject
        :type   event_subject:  subject | None
        :rtype:                 Tracker
        """
        warn(
            "track_page_view will be removed in future versions. Please use the new PageView class to track the event.",
            DeprecationWarning,
            stacklevel=2,
        )

        pv = PageView(
            page_url=page_url,
            page_title=page_title,
            referrer=referrer,
            event_subject=event_subject,
            context=context,
            true_timestamp=tstamp,
        )

        self.track(event=pv)
        return self

    def track_page_ping(
        self,
        page_url: str,
        page_title: Optional[str] = None,
        referrer: Optional[str] = None,
        min_x: Optional[int] = None,
        max_x: Optional[int] = None,
        min_y: Optional[int] = None,
        max_y: Optional[int] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  page_url:       URL of the viewed page
        :type   page_url:       non_empty_string
        :param  page_title:     Title of the viewed page
        :type   page_title:     string_or_none
        :param  referrer:       Referrer of the page
        :type   referrer:       string_or_none
        :param  min_x:          Minimum page x offset seen in the last ping period
        :type   min_x:          int | None
        :param  max_x:          Maximum page x offset seen in the last ping period
        :type   max_x:          int | None
        :param  min_y:          Minimum page y offset seen in the last ping period
        :type   min_y:          int | None
        :param  max_y:          Maximum page y offset seen in the last ping period
        :type   max_y:          int | None
        :param  context:        Custom context for the event
        :type   context:        context_array | None
        :param  tstamp:         Optional event timestamp in milliseconds
        :type   tstamp:         int | float | None
        :param  event_subject:  Optional per event subject
        :type   event_subject:  subject | None
        :rtype:                 Tracker
        """
        warn(
            "track_page_ping will be removed in future versions. Please use the new PagePing class to track the event.",
            DeprecationWarning,
            stacklevel=2,
        )

        pp = PagePing(
            page_url=page_url,
            page_title=page_title,
            referrer=referrer,
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            context=context,
            true_timestamp=tstamp,
            event_subject=event_subject,
        )

        self.track(event=pp)
        return self

    def track_link_click(
        self,
        target_url: str,
        element_id: Optional[str] = None,
        element_classes: Optional[ElementClasses] = None,
        element_target: Optional[str] = None,
        element_content: Optional[str] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  target_url:         Target URL of the link
        :type   target_url:         non_empty_string
        :param  element_id:         ID attribute of the HTML element
        :type   element_id:         string_or_none
        :param  element_classes:    Classes of the HTML element
        :type   element_classes:    list(str) | tuple(str,\\*) | None
        :param  element_target:     ID attribute of the HTML element
        :type   element_target:     string_or_none
        :param  element_content:    The content of the HTML element
        :type   element_content:    string_or_none
        :param  context:            Custom context for the event
        :type   context:            context_array | None
        :param  tstamp:             Optional event timestamp in milliseconds
        :type   tstamp:             int | float | None
        :param  event_subject:      Optional per event subject
        :type   event_subject:      subject | None
        :rtype:                     Tracker
        """
        warn(
            "track_link_click will be removed in future versions. Please use the new SelfDescribing class to track the event.",
            DeprecationWarning,
            stacklevel=2,
        )
        non_empty_string(target_url)

        properties = {}
        properties["targetUrl"] = target_url
        if element_id is not None:
            properties["elementId"] = element_id
        if element_classes is not None:
            properties["elementClasses"] = element_classes
        if element_target is not None:
            properties["elementTarget"] = element_target
        if element_content is not None:
            properties["elementContent"] = element_content

        event_json = SelfDescribingJson(
            "%s/link_click/%s/1-0-1" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties
        )

        self.track_self_describing_event(
            event_json=event_json,
            context=context,
            tstamp=tstamp,
            event_subject=event_subject,
        )
        return self

    def track_add_to_cart(
        self,
        sku: str,
        quantity: int,
        name: Optional[str] = None,
        category: Optional[str] = None,
        unit_price: Optional[float] = None,
        currency: Optional[str] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  sku:            Item SKU or ID
        :type   sku:            non_empty_string
        :param  quantity:       Number added to cart
        :type   quantity:       int
        :param  name:           Item's name
        :type   name:           string_or_none
        :param  category:       Item's category
        :type   category:       string_or_none
        :param  unit_price:     Item's price
        :type   unit_price:     int | float | None
        :param  currency:       Type of currency the price is in
        :type   currency:       string_or_none
        :param  context:        Custom context for the event
        :type   context:        context_array | None
        :param  tstamp:         Optional event timestamp in milliseconds
        :type   tstamp:         int | float | None
        :param  event_subject:  Optional per event subject
        :type   event_subject:  subject | None
        :rtype:                 Tracker
        """
        warn(
            "track_add_to_cart will be deprecated in future versions.",
            DeprecationWarning,
            stacklevel=2,
        )
        non_empty_string(sku)

        properties = {}
        properties["sku"] = sku
        properties["quantity"] = quantity
        if name is not None:
            properties["name"] = name
        if category is not None:
            properties["category"] = category
        if unit_price is not None:
            properties["unitPrice"] = unit_price
        if currency is not None:
            properties["currency"] = currency

        event_json = SelfDescribingJson(
            "%s/add_to_cart/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties
        )

        self.track_self_describing_event(
            event_json=event_json,
            context=context,
            tstamp=tstamp,
            event_subject=event_subject,
        )
        return self

    def track_remove_from_cart(
        self,
        sku: str,
        quantity: int,
        name: Optional[str] = None,
        category: Optional[str] = None,
        unit_price: Optional[float] = None,
        currency: Optional[str] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  sku:            Item SKU or ID
        :type   sku:            non_empty_string
        :param  quantity:       Number added to cart
        :type   quantity:       int
        :param  name:           Item's name
        :type   name:           string_or_none
        :param  category:       Item's category
        :type   category:       string_or_none
        :param  unit_price:     Item's price
        :type   unit_price:     int | float | None
        :param  currency:       Type of currency the price is in
        :type   currency:       string_or_none
        :param  context:        Custom context for the event
        :type   context:        context_array | None
        :param  tstamp:         Optional event timestamp in milliseconds
        :type   tstamp:         int | float | None
        :param  event_subject:  Optional per event subject
        :type   event_subject:  subject | None
        :rtype:                 Tracker
        """
        warn(
            "track_remove_from_cart will be deprecated in future versions.",
            DeprecationWarning,
            stacklevel=2,
        )
        non_empty_string(sku)

        properties = {}
        properties["sku"] = sku
        properties["quantity"] = quantity
        if name is not None:
            properties["name"] = name
        if category is not None:
            properties["category"] = category
        if unit_price is not None:
            properties["unitPrice"] = unit_price
        if currency is not None:
            properties["currency"] = currency

        event_json = SelfDescribingJson(
            "%s/remove_from_cart/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties
        )

        self.track_self_describing_event(
            event_json=event_json,
            context=context,
            tstamp=tstamp,
            event_subject=event_subject,
        )
        return self

    def track_form_change(
        self,
        form_id: str,
        element_id: Optional[str],
        node_name: FormNodeName,
        value: Optional[str],
        type_: Optional[str] = None,
        element_classes: Optional[ElementClasses] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  form_id:            ID attribute of the HTML form
        :type   form_id:            non_empty_string
        :param  element_id:         ID attribute of the HTML element
        :type   element_id:         string_or_none
        :param  node_name:          Type of input element
        :type   node_name:          form_node_name
        :param  value:              Value of the input element
        :type   value:              string_or_none
        :param  type_:              Type of data the element represents
        :type   type_:              non_empty_string, form_type
        :param  element_classes:    Classes of the HTML element
        :type   element_classes:    list(str) | tuple(str,\\*) | None
        :param  context:            Custom context for the event
        :type   context:            context_array | None
        :param  tstamp:             Optional event timestamp in milliseconds
        :type   tstamp:             int | float | None
        :param  event_subject:      Optional per event subject
        :type   event_subject:      subject | None
        :rtype:                     Tracker
        """
        warn(
            "track_form_change will be removed in future versions. Please use the new SelfDescribing class to track the event.",
            DeprecationWarning,
            stacklevel=2,
        )

        non_empty_string(form_id)
        one_of(node_name, FORM_NODE_NAMES)
        if type_ is not None:
            one_of(type_.lower(), FORM_TYPES)

        properties = dict()
        properties["formId"] = form_id
        properties["elementId"] = element_id
        properties["nodeName"] = node_name
        properties["value"] = value
        if type_ is not None:
            properties["type"] = type_
        if element_classes is not None:
            properties["elementClasses"] = element_classes

        event_json = SelfDescribingJson(
            "%s/change_form/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties
        )

        self.track_self_describing_event(
            event_json=event_json,
            context=context,
            tstamp=tstamp,
            event_subject=event_subject,
        )
        return self

    def track_form_submit(
        self,
        form_id: str,
        form_classes: Optional[FormClasses] = None,
        elements: Optional[List[Dict[str, Any]]] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  form_id:        ID attribute of the HTML form
        :type   form_id:        non_empty_string
        :param  form_classes:   Classes of the HTML form
        :type   form_classes:   list(str) | tuple(str,\\*) | None
        :param  elements:       Classes of the HTML form
        :type   elements:       list(form_element) | None
        :param  context:        Custom context for the event
        :type   context:        context_array | None
        :param  tstamp:         Optional event timestamp in milliseconds
        :type   tstamp:         int | float | None
        :param  event_subject:  Optional per event subject
        :type   event_subject:  subject | None
        :rtype:                 Tracker
        """
        warn(
            "track_form_submit will be removed in future versions. Please use the new SelfDescribing class to track the event.",
            DeprecationWarning,
            stacklevel=2,
        )
        non_empty_string(form_id)

        for element in elements or []:
            form_element(element)

        properties = dict()
        properties["formId"] = form_id
        if form_classes is not None:
            properties["formClasses"] = form_classes
        if elements is not None and len(elements) > 0:
            properties["elements"] = elements

        event_json = SelfDescribingJson(
            "%s/submit_form/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties
        )

        self.track_self_describing_event(
            event_json=event_json,
            context=context,
            tstamp=tstamp,
            event_subject=event_subject,
        )
        return self

    def track_site_search(
        self,
        terms: Sequence[str],
        filters: Optional[Dict[str, Union[str, bool]]] = None,
        total_results: Optional[int] = None,
        page_results: Optional[int] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  terms:          Search terms
        :type   terms:          seq[>=1](str)
        :param  filters:        Filters applied to the search
        :type   filters:        dict(str:str|bool) | None
        :param  total_results:  Total number of results returned
        :type   total_results:  int | None
        :param  page_results:   Total number of pages of results
        :type   page_results:   int | None
        :param  context:        Custom context for the event
        :type   context:        context_array | None
        :param  tstamp:         Optional event timestamp in milliseconds
        :type   tstamp:         int | float | None
        :param  event_subject:  Optional per event subject
        :type   event_subject:  subject | None
        :rtype:                 Tracker
        """
        warn(
            "track_site_search will be removed in future versions. Please use the new SelfDescribing class to track the event.",
            DeprecationWarning,
            stacklevel=2,
        )
        non_empty(terms)

        properties = {}
        properties["terms"] = terms
        if filters is not None:
            properties["filters"] = filters
        if total_results is not None:
            properties["totalResults"] = total_results
        if page_results is not None:
            properties["pageResults"] = page_results

        event_json = SelfDescribingJson(
            "%s/site_search/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG), properties
        )

        self.track_self_describing_event(
            event_json=event_json,
            context=context,
            tstamp=tstamp,
            event_subject=event_subject,
        )
        return self

    def track_ecommerce_transaction_item(
        self,
        order_id: str,
        sku: str,
        price: float,
        quantity: int,
        name: Optional[str] = None,
        category: Optional[str] = None,
        currency: Optional[str] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        This is an internal method called by track_ecommerce_transaction.
        It is not for public use.

        :param  order_id:       Order ID
        :type   order_id:       non_empty_string
        :param  sku:            Item SKU
        :type   sku:            non_empty_string
        :param  price:          Item price
        :type   price:          int | float
        :param  quantity:       Item quantity
        :type   quantity:       int
        :param  name:           Item name
        :type   name:           string_or_none
        :param  category:       Item category
        :type   category:       string_or_none
        :param  currency:       The currency the price is expressed in
        :type   currency:       string_or_none
        :param  context:        Custom context for the event
        :type   context:        context_array | None
        :param  tstamp:         Optional event timestamp in milliseconds
        :type   tstamp:         int | float | None
        :param  event_subject:  Optional per event subject
        :type   event_subject:  subject | None
        :rtype:                 Tracker
        """
        warn(
            "track_ecommerce_transaction_item will be deprecated in future versions.",
            DeprecationWarning,
            stacklevel=2,
        )
        non_empty_string(order_id)
        non_empty_string(sku)

        event = Event(
            event_subject=event_subject, context=context, true_timestamp=tstamp
        )
        event.payload.add("e", "ti")
        event.payload.add("ti_id", order_id)
        event.payload.add("ti_sk", sku)
        event.payload.add("ti_nm", name)
        event.payload.add("ti_ca", category)
        event.payload.add("ti_pr", price)
        event.payload.add("ti_qu", quantity)
        event.payload.add("ti_cu", currency)

        self.track(event=event)
        return self

    def track_ecommerce_transaction(
        self,
        order_id: str,
        total_value: float,
        affiliation: Optional[str] = None,
        tax_value: Optional[float] = None,
        shipping: Optional[float] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        currency: Optional[str] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  order_id:       ID of the eCommerce transaction
        :type   order_id:       non_empty_string
        :param  total_value:    Total transaction value
        :type   total_value:    int | float
        :param  affiliation:    Transaction affiliation
        :type   affiliation:    string_or_none
        :param  tax_value:      Transaction tax value
        :type   tax_value:      int | float | None
        :param  shipping:       Delivery cost charged
        :type   shipping:       int | float | None
        :param  city:           Delivery address city
        :type   city:           string_or_none
        :param  state:          Delivery address state
        :type   state:          string_or_none
        :param  country:        Delivery address country
        :type   country:        string_or_none
        :param  currency:       The currency the price is expressed in
        :type   currency:       string_or_none
        :param  items:          The items in the transaction
        :type   items:          list(dict(str:\\*)) | None
        :param  context:        Custom context for the event
        :type   context:        context_array | None
        :param  tstamp:         Optional event timestamp in milliseconds
        :type   tstamp:         int | float | None
        :param  event_subject:  Optional per event subject
        :type   event_subject:  subject | None
        :rtype:                 Tracker
        """
        warn(
            "track_ecommerce_transaction will be deprecated in future versions.",
            DeprecationWarning,
            stacklevel=2,
        )
        non_empty_string(order_id)

        event = Event(
            event_subject=event_subject, context=context, true_timestamp=tstamp
        )
        event.payload.add("e", "tr")
        event.payload.add("tr_id", order_id)
        event.payload.add("tr_tt", total_value)
        event.payload.add("tr_af", affiliation)
        event.payload.add("tr_tx", tax_value)
        event.payload.add("tr_sh", shipping)
        event.payload.add("tr_ci", city)
        event.payload.add("tr_st", state)
        event.payload.add("tr_co", country)
        event.payload.add("tr_cu", currency)

        tstamp = Tracker.get_timestamp(tstamp)

        self.track(event=event)

        if items is None:
            items = []
        for item in items:
            item["order_id"] = order_id
            item["currency"] = currency
            item["tstamp"] = tstamp
            item["event_subject"] = event_subject
            item["context"] = context
            self.track_ecommerce_transaction_item(**item)

        return self

    def track_screen_view(
        self,
        name: Optional[str] = None,
        id_: Optional[str] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  name:           The name of the screen view event
        :type   name:           string_or_none
        :param  id_:            Screen view ID
        :type   id_:            string_or_none
        :param  context:        Custom context for the event
        :type   context:        context_array | None
        :param  tstamp:         Optional event timestamp in milliseconds
        :type   tstamp:         int | float | None
        :param  event_subject:  Optional per event subject
        :type   event_subject:  subject | None
        :rtype:                 Tracker
        """
        warn(
            "track_screen_view will be removed in future versions. Please use the new ScreenView class to track the event.",
            DeprecationWarning,
            stacklevel=2,
        )
        screen_view_properties = {}
        if name is not None:
            screen_view_properties["name"] = name
        if id_ is not None:
            screen_view_properties["id"] = id_

        event_json = SelfDescribingJson(
            "%s/screen_view/%s/1-0-0" % (BASE_SCHEMA_PATH, SCHEMA_TAG),
            screen_view_properties,
        )

        self.track_self_describing_event(
            event_json=event_json,
            context=context,
            tstamp=tstamp,
            event_subject=event_subject,
        )
        return self

    def track_mobile_screen_view(
        self,
        name: str,
        id_: Optional[str] = None,
        type: Optional[str] = None,
        previous_name: Optional[str] = None,
        previous_id: Optional[str] = None,
        previous_type: Optional[str] = None,
        transition_type: Optional[str] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  name:           The name of the screen view event
        :type   name:           string_or_none
        :param  id_:            Screen view ID. This must be of type UUID.
        :type   id_:            string | None
        :param  type:           The type of screen that was viewed e.g feed / carousel.
        :type   type:           string | None
        :param  previous_name:  The name of the previous screen.
        :type   previous_name:  string | None
        :param  previous_id:    The screenview ID of the previous screenview.
        :type   previous_id:    string | None
        :param  previous_type   The screen type of the previous screenview
        :type   previous_type   string | None
        :param  transition_type The type of transition that led to the screen being viewed.
        :type   transition_type string | None
        :param  context:        Custom context for the event
        :type   context:        context_array | None
        :param  tstamp:         Optional event timestamp in milliseconds
        :type   tstamp:         int | float | None
        :param  event_subject:  Optional per event subject
        :type   event_subject:  subject | None
        :rtype:                 Tracker
        """
        warn(
            "track_mobile_screen_view will be removed in future versions. Please use the new ScreenView class to track the event.",
            DeprecationWarning,
            stacklevel=2,
        )
        if id_ is None:
            id_ = self.get_uuid()

        sv = ScreenView(
            name=name,
            id_=id_,
            type=type,
            previous_name=previous_name,
            previous_id=previous_id,
            previous_type=previous_type,
            transition_type=transition_type,
            event_subject=event_subject,
            context=context,
            true_timestamp=tstamp,
        )

        self.track(event=sv)
        return self

    def track_struct_event(
        self,
        category: str,
        action: str,
        label: Optional[str] = None,
        property_: Optional[str] = None,
        value: Optional[float] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  category:       Category of the event
        :type   category:       non_empty_string
        :param  action:         The event itself
        :type   action:         non_empty_string
        :param  label:          Refer to the object the action is
                                performed on
        :type   label:          string_or_none
        :param  property_:      Property associated with either the action
                                or the object
        :type   property_:      string_or_none
        :param  value:          A value associated with the user action
        :type   value:          int | float | None
        :param  context:        Custom context for the event
        :type   context:        context_array | None
        :param  tstamp:         Optional event timestamp in milliseconds
        :type   tstamp:         int | float | None
        :param  event_subject:  Optional per event subject
        :type   event_subject:  subject | None
        :rtype:                 Tracker
        """
        warn(
            "track_struct_event will be removed in future versions. Please use the new Structured class to track the event.",
            DeprecationWarning,
            stacklevel=2,
        )
        se = StructuredEvent(
            category=category,
            action=action,
            label=label,
            property_=property_,
            value=value,
            context=context,
            true_timestamp=tstamp,
            event_subject=event_subject,
        )

        self.track(
            event=se,
        )
        return self

    def track_self_describing_event(
        self,
        event_json: SelfDescribingJson,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  event_json:      The properties of the event. Has two field:
                                 A "data" field containing the event properties and
                                 A "schema" field identifying the schema against which the data is validated
        :type   event_json:      self_describing_json
        :param  context:         Custom context for the event
        :type   context:         context_array | None
        :param  tstamp:          Optional event timestamp in milliseconds
        :type   tstamp:          int | float | None
        :param  event_subject:   Optional per event subject
        :type   event_subject:   subject | None
        :rtype:                  Tracker
        """
        warn(
            "track_self_describing_event will be removed in future versions. Please use the new SelfDescribing class to track the event.",
            DeprecationWarning,
            stacklevel=2,
        )

        sd = SelfDescribing(
            event_json=event_json,
            context=context,
            true_timestamp=tstamp,
            event_subject=event_subject,
        )
        self.track(
            event=sd,
        )
        return self

    # Alias
    def track_unstruct_event(
        self,
        event_json: SelfDescribingJson,
        context: Optional[List[SelfDescribingJson]] = None,
        tstamp: Optional[float] = None,
        event_subject: Optional[Subject] = None,
    ) -> "Tracker":
        """
        :param  event_json:      The properties of the event. Has two field:
                                 A "data" field containing the event properties and
                                 A "schema" field identifying the schema against which the data is validated
        :type   event_json:      self_describing_json
        :param  context:         Custom context for the event
        :type   context:         context_array | None
        :param  tstamp:          Optional event timestamp in milliseconds
        :type   tstamp:          int | float | None
        :param  event_subject:   Optional per event subject
        :type   event_subject:   subject | None
        :rtype:                  Tracker
        """
        warn(
            "track_unstruct_event will be deprecated in future versions. Please use track_self_describing_event.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.track_self_describing_event(
            event_json=event_json,
            context=context,
            tstamp=tstamp,
            event_subject=event_subject,
        )
        return self

    def flush(self, is_async: bool = False) -> "Tracker":
        """
        Flush the emitter

        :param  is_async:  Whether the flush is done asynchronously. Default is False
        :type   is_async:  bool
        :rtype:         tracker
        """
        for emitter in self.emitters:
            if is_async:
                if hasattr(emitter, "flush"):
                    emitter.flush()
            else:
                if hasattr(emitter, "sync_flush"):
                    emitter.sync_flush()
        return self

    def set_subject(self, subject: Optional[Subject]) -> "Tracker":
        """
        Set the subject of the events fired by the tracker

        :param subject: Subject to be tracked
        :type  subject: subject | None
        :rtype:         tracker
        """
        self.subject = subject
        return self

    def add_emitter(self, emitter: EmitterProtocol) -> "Tracker":
        """
        Add a new emitter to which events should be passed

        :param emitter: New emitter
        :type  emitter: emitter
        :rtype:         tracker
        """
        self.emitters.append(emitter)
        return self

    def get_namespace(self) -> str:
        return self.standard_nv_pairs["tna"]
