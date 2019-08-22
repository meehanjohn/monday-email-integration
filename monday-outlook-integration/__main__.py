import creds
import params
import requests
import imaplib
import base64
import os
import email
from datetime import datetime
import json
from bs4 import BeautifulSoup

class incEmail:
    """
    This is a class for retrieving and parsing incoming webform requests.
    """
    def __init__(self):
        """
        The constructor of the incEmail class.
        """
        self.user = creds.email
        self.password = creds.password
        self.host = creds.server
        self.port = creds.imap_port
        try:
            self.mail = imaplib.IMAP4_SSL(self.host, self.port)
        except Exception as e:
            print(e)
            print(self.mail)

    def get_messages(self):
        """
        Retrieves all new webform requests.
        Constructs a list of HTML email bodies.

        Parameters: None

        Returns: None
        """
        mail = self.mail
        mail.login(self.user, self.password)

        # Only focus on a specific subfolder
        # 'Webform_Inquiries' folder is set up with basic rules to move all
        # incoming web inquires directly from the Inbox
        mail.select('Webform_Inquiries')

        # No criteria for the mail search other than unread '(UNSEEN)'
        # This simply returns a list for fetch to use. Emails will be marked as
        # read as soon as they are read in by the fetch function
        type, data = mail.search(None, '(UNSEEN)')

        messages = []

        for num in data[0].split():
            typ, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)

            # Webform emails are never multi-part
            # Simply retrieve payload (body) for each email
            # Check for Email subject in case other emails get mixed in
            if "Response from Amuneal" in email_message['subject']:
                messages.append(email_message.get_payload(decode=True))

        # set messages parameter to be accessible by other functions
        self.messages = messages

    def parse(self):
        """
        Extracts the relevant fields from incoming messages.

        Parameters: None

        Returns:
            submissions (list): All new webform inquiries converted into a list
            of dicts, each containing the extracted fields from the original
            webform inquiry.
        """

        def field_list(input, type):
            """
            Extracts different elements of the email.

            Parameters:
                input (str): parsed email HTML
                type (str): 'sub' or 'head', the two parts of the webform that
                contain relevant information

            Returns:
                elements (list): A list of strings containing the extracted
                and stripped email elements that are relevant to the webform
                inquiry.
            """
            tag = 'td'

            if type == 'sub':
                style = "color:#555555;padding-top: 3px;padding-bottom: 20px;"
            elif type == 'head':
                style = 'color:#333333;padding-top: 20px;padding-bottom: 3px;'

            elements = list(map(lambda x: x.get_text().strip(),
                                input.find_all(tag, style=style)))
            return elements

        submissions = []

        for message in self.messages:

            soup = BeautifulSoup(message, 'lxml')
            sub_elements = field_list(soup, 'sub')
            head_elements = field_list(soup, 'head')

            submission = dict(zip(head_elements,sub_elements))

            submissions.append(submission)

        return submissions



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
            "text2" : key_verify('Choose Interest Category'),
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

def main():
    """
    TODO
    """

    # Instantiate incEmail object; pulls in credentials and attempts to
    # log into specified email account
    incoming = incEmail()
    # Fetch all messages meeting the specified criteria (unseen, subject line)
    incoming.get_messages()
    # Extract the relevant webform information, including the header and body
    # of each table cell
    submissions = incoming.parse()

    # Instantiate gqlQuery object; pulls in credentials and relevant info
    # needed to access the Monday.com GraphQL API
    to_monday = gqlQuery()

    # Cycle through all new, parsed web inquiries to add a new row in an
    # existing Monday.com board
    for submission in submissions:
        to_monday.mutate(submission)
        # Catch exceptions if API call fails
        try:
            status = to_monday.post_query()
            print(status)
        except RuntimeError as e:
            print(e)

if __name__ == '__main__':
    main()
