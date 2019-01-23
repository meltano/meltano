import logging
import requests
import uuid

from typing import Dict

REQUEST_TIMEOUT = 2.0
MELTANO_TRACKING_ID = "UA-132758957-3"
MEASUREMENT_PROTOCOL_URI = "https://www.google-analytics.com/collect"
DEBUG_MEASUREMENT_PROTOCOL_URI = "https://www.google-analytics.com/debug/collect"


class GoogleAnalyticsTracker:
    def __init__(
        self,
        tracking_id: str = None,
        client_id: str = None,
        request_timeout: float = None,
    ) -> None:
        self.tracking_id = tracking_id or MELTANO_TRACKING_ID
        self.client_id = client_id or uuid.uuid4()
        self.request_timeout = request_timeout or REQUEST_TIMEOUT

    def event(self, category: str, action: str) -> Dict:
        event = {
            "v": "1",
            "tid": self.tracking_id,
            "cid": self.client_id,
            "ds": "meltano cli",
            "t": "event",
            "ec": category,
            "ea": action,
        }
        return event

    def track_data(self, data: Dict, debug: bool = False) -> None:
        if debug:
            tracking_uri = DEBUG_MEASUREMENT_PROTOCOL_URI
        else:
            tracking_uri = MEASUREMENT_PROTOCOL_URI

        try:
            r = requests.post(tracking_uri, data=data, timeout=self.request_timeout)

            if debug:
                logging.info(f"GoogleAnalyticsTracker.track_data:")
                logging.info(data)
                logging.info(f"Response:")
                logging.info(f"status_code: {r.status_code}")
                logging.info(r.text)
        except requests.exceptions.Timeout:
            logging.debug("GoogleAnalyticsTracker.track_data: Request Timed Out")
        except requests.exceptions.ConnectionError as e:
            logging.debug("GoogleAnalyticsTracker.track_data: ConnectionError")
            logging.debug(e)
        except requests.exceptions.RequestException as e:
            logging.debug("GoogleAnalyticsTracker.track_data: RequestException")
            logging.debug(e)

    def track_event(self, category: str, action: str, debug: bool = False) -> None:
        event = self.event(category, action)
        self.track_data(event, debug)

    def track_meltano_init(self, project_name: str, debug: bool = False) -> None:
        event = self.track_event(
            category="meltano init", action=f"meltano init {project_name}", debug=debug
        )

    def track_meltano_add(
        self, plugin_type: str, plugin_name: str, debug: bool = False
    ) -> None:
        event = self.track_event(
            category=f"meltano add {plugin_type}",
            action=f"meltano add {plugin_type} {plugin_name}",
            debug=debug,
        )

    def track_meltano_discover(self, plugin_type: str, debug: bool = False) -> None:
        event = self.track_event(
            category="meltano discover",
            action=f"meltano discover {plugin_type}",
            debug=debug,
        )

    def track_meltano_elt(
        self, extractor: str, loader: str, transform: str, debug: bool = False
    ) -> None:
        event = self.track_event(
            category="meltano elt",
            action=f"meltano elt {extractor} {loader} --transform {transform}",
            debug=debug,
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    tracker = GoogleAnalyticsTracker()

    debug = True
    tracker.track_meltano_init(project_name="my-test-project", debug=debug)
    tracker.track_meltano_add(
        plugin_type="extractor", plugin_name="tap-carbon-intensity", debug=debug
    )
    tracker.track_meltano_add(
        plugin_type="loader", plugin_name="target-postgres", debug=debug
    )
    tracker.track_meltano_add(plugin_type="transformer", plugin_name="dbt", debug=debug)
    tracker.track_meltano_add(
        plugin_type="transform", plugin_name="tap-carbon-intensity", debug=debug
    )
    tracker.track_meltano_discover(plugin_type="extractors", debug=debug)
    tracker.track_meltano_elt(
        extractor="tap-carbon-intensity",
        loader="target-sqlite",
        transform="skip",
        debug=debug,
    )
    tracker.track_meltano_elt(
        extractor="tap-carbon-intensity",
        loader="target-postgres",
        transform="run",
        debug=debug,
    )
