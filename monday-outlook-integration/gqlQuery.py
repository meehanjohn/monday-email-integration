import creds                    # Use-specific credentials file
import params                   # Exposed parameters file
import requests                 # To post GraphQL query
from datetime import datetime   # To get timestamp of when program is run
import json                     # For formatting GraphQL queries

class gqlQuery:
    """
    This is a class for posting queries and mutations to the monday.com
    GraphQL API.

    Attributes:
        submission (dict):
    """

    def __init__(self):
        """
        The constructor of the gqlQuery class.
        """
        self.token = creds.api_token
        self.url = creds.monday_url
        self.date = str(datetime.now().isoformat(' ', timespec='minutes'))

    def post_query(self):
        """
        TODO
        """

        headers = {"Authorization" : self.token}

        request = requests.post(self.url,
                                json=self.req_data,
                                headers=headers)

        if request.status_code == 200:
            return request.json()
        else:
            raise RuntimeError("Query Failed.")

    def mutate(self, submission):
        """
        TODO
        """

        def key_verify(key, dict=submission):
            """ Checks if an element of the webform is absent """
            if key in dict:
                return dict[key]
            else:
                return None

        columns = {
            "text" : key_verify('FULL NAME'),
            "text0" : key_verify('EMAIL'),
            "text5" : key_verify('PHONE'),
            "text2" : key_verify('CHOOSE INTEREST CATEGORY'),
            "comments_or_additional_information7" : key_verify('COMMENTS OR ADDITIONAL INFORMATION'),
            "text7" : key_verify('Interested in:'),
            "date7" : str(self.date)
        }

        # https://monday.com/developers/v2#mutations-section
        query = """
            mutation($board_id : Int!, $item_name : String!, $columns: JSON!) {
                create_item (board_id: $board_id,
                             item_name: $item_name,
                             column_values: $columns) {
                    name
                }
            }
            """
        # https://monday.com/developers/v2#using-grpahql-section-variables
        variables = {
            "board_id" : 297351387,
            "item_name" : "New Inquiry: " + str(self.date),
            "columns" : json.dumps(columns)
        }

        self.req_data = {'query' : query, 'variables' : variables}
