import logging
from typing import Dict, List, Optional, Sequence, Any, Iterator

from fire import Fire
import pandas as pd
import requests


class MarketoClient(object):
    def __init__(self, config: Dict[str, str]) -> None:
        self.endpoint: str = config["endpoint"]
        self.identity: str = config["identity"]
        self.client_id: str = config["client_id"]
        self.client_secret: str = config["client_secret"]
        self.start_time: str = config["start_time"]
        self.access_token: Optional[str] = self.get_access_token()
        self.start_time_token: str = self.get_date_token()

    def chunker(self, full_list: List, chunk_size: int) -> Iterator[List]:
        """
        Generator that yields a chunk of the original list.
        """
        for i in range(0, len(full_list), chunk_size):
            yield full_list[i : i + chunk_size]

    def get_response_json(self, url: str, payload: Dict[str, Any]):
        """
        Boilerplate for GETting a request and returning the json.
        """

        auth = {"access_token": self.access_token}
        params = {**auth, **payload}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def check_response_success(self, response: Dict) -> Dict:
        """
        Marketo returns a 200 even if the request might have failed.
        Check the status in the object and return if truly successful.
        """

        if not response["success"]:
            logging.error(f"Request failed. Errors {response['errors']}")
            raise Exception
        else:
            return response

    def get_access_token(self) -> str:
        """
        Hit the Marketo Identity endpoint to get a valid access token.
        """

        self.access_token = None
        logging.info("Getting access token...")
        identity_url = f"{self.identity}/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        return self.get_response_json(identity_url, payload)["access_token"]

    def get_date_token(self) -> str:
        """
        Get a date-based paging token from Marketo for use in other calls.
        """

        token_url = f"{self.endpoint}/v1/activities/pagingtoken.json"
        payload = {"sinceDatetime": self.start_time}
        response = self.get_response_json(token_url, payload)
        return response["nextPageToken"]

    def get_activities(self, activity_type_ids: List[int]) -> List[Dict]:
        """
        Get a list of activities based on a datetime nextPageToken.
        """

        logging.info("Getting activities...")
        chunk_size = 10  # This is the limit for the API
        date_token = self.start_time_token
        activities_url = f"{self.endpoint}/v1/activities.json"

        results: List = []
        # GET response filtered by activity type ids
        for type_chunk in self.chunker(activity_type_ids, chunk_size):

            # Loop until there are no more results
            while True:
                payload = {"nextPageToken": date_token, "activityTypeIds": type_chunk}

                response = self.check_response_success(
                    self.get_response_json(activities_url, payload)
                )
                if response.get("result"):
                    results += response["result"]
                    logging.info(f"Retrieved {len(results)} records total...")

                if response["moreResult"]:
                    date_token = response["nextPageToken"]
                else:
                    break
        return results

    def get_activity_types(self) -> List[Dict]:
        """
        Get the full list of activity types.
        """

        logging.info("Getting activity types...")
        ## TODO: Deal with the case that there are over 300 activity types
        activity_type_url = f"{self.endpoint}/v1/activities/types.json"
        payload: Dict = {}

        response = self.check_response_success(
            self.get_response_json(activity_type_url, payload)
        )
        result = response["result"]

        logging.info(f"Retrieved {len(result)} records")
        return result

    def get_leads(self, activity_lead_ids: List[str]) -> List[Dict]:
        """
        Get lead data based on leads pulled in by the activities endpoint.
        """

        logging.info("Getting leads...")
        chunk_size = 300  # This is the limit for the API
        leads_url = f"{self.endpoint}/v1/leads.json"

        results: List = []
        # GET response filtered by activity type ids
        for id_chunk in self.chunker(activity_lead_ids, chunk_size):
            payload = {"filterType": "id", "filterValues": id_chunk}
            response = self.check_response_success(
                self.get_response_json(leads_url, payload)
            )
            results += response["result"]
            logging.info(f"Retrieved {len(results)} records total...")

        return results

    def get_all(self) -> Dict[str, List[Dict]]:
        """
        Get leads, activities and activity_types.
        """

        logging.info("Starting API Calls...")

        # Retrieve all activity types
        activity_types = self.get_activity_types()
        activity_type_ids = list({record["id"] for record in activity_types})
        logging.info(f"Retrieved {len(activity_type_ids)} total activity_type_ids...")

        # Retrieve all related activities
        activities = self.get_activities(activity_type_ids)
        activity_lead_ids = list({record["leadId"] for record in activities})
        logging.info(f"Retrieved {len(activities)} total activities...")

        # Retrieve leads that are related to retrieved activities
        leads = self.get_leads(activity_lead_ids)
        logging.info(f"Retrieved {len(leads)} total leads...")

        data_dict = {
            "activity_types": pd.io.json.json_normalize(activity_types),
            "activities": pd.io.json.json_normalize(activities),
            "leads": pd.io.json.json_normalize(leads),
        }

        return data_dict
