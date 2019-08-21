import requests
import creds
import imaplib
import base64
import os
import email
import datetime
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
        A function to retrieve all new webform requests.
        Constructs a list of HTML email bodies.

        Parameters: None

        Returns: None
        """
        mail = self.mail
        mail.login(self.user, self.password)
        mail.select('Webform_Inquiries')

        type, data = mail.search(None, '(UNSEEN)')

        messages = []

        for num in data[0].split():
            typ, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)

            if "Response from Amuneal" in email_message['subject']:
                """
                if email_message.is_multipart():
                    for part in email_message.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get('Content-Disposition'))

                        if ctype == 'text/plain' and 'attachment' not in cdispo:
                            messages.append(part.get_payload(decode=True))
                            break
                else:
                    messages.append(email_message.get_payload(decode=True))
                """
                messages.append(email_message.get_payload(decode=True))

        self.messages = messages

    def parse(self):
        """
        A function to extract the relevant fields from incoming messages.

        Parameters: None

        Returns:
            submissions (list): All new webform inquiries converted into a list
            of dicts, each containing the extracted fields from the original
            webform inquiry.
        """

        def field_list(input, type):
            """
            A function which extracts different elements of the email.

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
        self.date = str(datetime.datetime.now())

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

        query = """
            mutation($board_id : Int!, $item_name : String!, $columns: JSON!) {
                create_item (board_id: $board_id,
                             item_name: $item_name,
                             column_values: $columns) {
                    name
                }
            }
            """

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
    incoming = incEmail()
    incoming.get_messages()
    submissions = incoming.parse()

    to_monday = gqlQuery()

    for submission in submissions:
        to_monday.mutate(submission)
        try:
            status = to_monday.post_query()
            print(status)
        except RuntimeError as e:
            print(e)

if __name__ == '__main__':
    main()
