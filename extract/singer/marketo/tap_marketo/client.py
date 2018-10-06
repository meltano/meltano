import logging
from typing import Dict, List, Optional, Sequence, Any, Iterator
import sys

from fire import Fire
import pandas as pd
import requests


class MarketoClient(object):
    def __init__(self, config: Dict[str,str]) -> None:
        self.endpoint: str = config['endpoint']
        self.identity: str = config['identity']
        self.client_id: str = config['client_id']
        self.client_secret: str = config['client_secret']
        self.start_time: str = config['start_time']
        self.access_token: str = self.get_access_token()

    def chunker(self, full_list: List, chunk_size: int) -> Iterator[List]:
        """
        Generator that yields a chunk of the original list.
        """
        for i in range(0, len(full_list), chunk_size):
            yield full_list[i:i + chunk_size]

    def get_response(self, url: str, payload: Dict[str, Any]):
        """
        Boilerplate for GETting a request and returning the json.
        """

        # Try to get the access token, it may not exist yet
        try:
            auth = {'access_token': self.access_token}
        except:
            auth = {'access_token': 'None'}

        params = {**auth, **payload}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            logging.critical(response.status_code)
            logging.critical(response.text)
            sys.exit(1)
        else:
            return response.json()

    def check_response_success(self, response: Dict) -> Dict:
        """
        Marketo returns a 200 even if the request might have failed.
        Check the status in the object and return if truly successful.
        """

        if not response['success']:
            logging.critical('Request failed.')
            logging.critical(response['errors'])
            sys.exit(1)
        else:
            return response

    def get_access_token(self) -> str:
        """
        Hit the Marketo Identity endpoint to get a valid access token.
        """

        logging.info('Getting access token...')
        identity_url = '{}/oauth/token'.format(self.identity)
        payload = {'grant_type': 'client_credentials',
                   'client_id': self.client_id,
                   'client_secret': self.client_secret}

        return self.get_response(identity_url, payload)['access_token']

    def get_date_token(self) -> str:
        """
        Get a date-based paging token from Marketo for use in other calls.
        """

        token_url = '{}/v1/activities/pagingtoken.json'.format(self.endpoint)
        payload = {'sinceDatetime': self.start_time}
        response = self.get_response(token_url, payload)
        return response['nextPageToken']

    def get_activities(self, activity_type_ids: List[int]) -> List[Dict]:
        """
        Get a list of activities based on a datetime nextPageToken.
        """

        logging.info('Getting activities...')
        chunk_size = 10 # This is the limit for the API
        date_token = self.get_date_token()
        activities_url = '{}/v1/activities.json'.format(self.endpoint)

        results: List = []
        # GET response filtered by activity type ids
        for type_chunk in self.chunker(activity_type_ids, chunk_size):

            # Loop until there are no more results
            while True:
                payload = {'nextPageToken': date_token,
                           'activityTypeIds': type_chunk}

                response = (self.check_response_success(
                                self.get_response(activities_url, payload)))
                try:
                    results += response['result']
                    logging.info('Retrieved {} records total...'.format(len(results)))
                except:
                    pass
                if response['moreResult']:
                    date_token = response['nextPageToken']
                else:
                    break
        return results

    def get_activity_types(self) -> List[Dict]:
        """
        Get the full list of activity types.
        """

        logging.info('Getting activity types...')
        ## TODO: Deal with the case that there are over 300 activity types
        activity_type_url = '{}/v1/activities/types.json'.format(self.endpoint)
        payload: Dict =  {}

        response = (self.check_response_success(
                        self.get_response(activity_type_url, payload)))
        result = response['result']

        logging.info('Retrieved {} records'.format(len(result)))
        return result

    def get_leads(self, activity_lead_ids: List[str]) -> List[Dict]:
        """
        Get lead data based on leads pulled in by the activities endpoint.
        """

        logging.info('Getting leads...')
        chunk_size = 300 # This is the limit for the API
        leads_url = '{}/v1/leads.json'.format(self.endpoint)

        results: List = []
        # GET response filtered by activity type ids
        for id_chunk in self.chunker(activity_lead_ids, chunk_size):

            payload = {'filterType': 'id',
                       'filterValues': id_chunk}

            response = (self.check_response_success(
                            self.get_response(leads_url, payload)))
            results += response['result']
            logging.info('Retrieved {} records total...'.format(len(results)))

        return results

    def get_data(self) -> Dict[str,List[Dict]]:
        """
        Get leads, activities and activity_types.
        """

        logging.info('Starting API Calls...')

        # Retrieve all activity types
        activity_types = self.get_activity_types()
        activity_type_ids = list({record['id'] for record in activity_types})
        logging.info('Retrieved {} total activity_type_ids...'.format(len(activity_type_ids)))

        # Retrieve all related activities
        activities = self.get_activities(activity_type_ids)
        activity_lead_ids = list({record['leadId'] for record in activities})
        logging.info('Retrieved {} total activities...'.format(len(activities)))

        # Retrieve leads that are related to retrieved activities
        leads = self.get_leads(activity_lead_ids)
        logging.info('Retrieved {} total leads...'.format(len(leads)))

        data_dict = {'activity_types': activity_types,
                     'activities': activities,
                     'leads': leads}

        return data_dict

