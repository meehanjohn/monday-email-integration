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

    def __init__(self):
        self.user = creds.email
        self.password = creds.password
        self.host = creds.server
        self.port = creds.imap_port
        self.mail = imaplib.IMAP4_SSL(self.host, self.port)

    def get_messages(self):
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
                if email_message.is_multipart():
                    for part in email_message.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get('Content-Disposition'))

                        if ctype == 'text/plain' and 'attachment' not in cdispo:
                            messages.append(part.get_payload(decode=True))
                            break
                else:
                    messages.append(email_message.get_payload(decode=True))

        self.messages = messages

    def parse(self):
        submissions = []

        for message in self.messages:

            soup = BeautifulSoup(message, 'lxml')
            elements = soup.find_all('td',
                {'style':"color:#555555;padding-top: 3px;padding-bottom: 20px;"})

            elements = list(map(lambda x: x.get_text().strip(), elements))

            if len(elements) < 5:
                pass

            else:
                submission = {'cust_name': elements.pop(0),
                              'cust_email': elements.pop(0),
                              'cust_phone': elements.pop(0),
                              'int_cat': elements.pop(0),
                              'comments': elements.pop(-1),
                              'interests': elements}

            submissions.append(submission)

        return submissions

class gqlQuery:

    def __init__(self):
        self.token = creds.api_token
        self.url = creds.monday_url
        self.date = str(datetime.datetime.now())

    def post_query(self):

        headers = {"Authorization" : self.token}

        request = requests.post(self.url,
                                json=self.req_data,
                                headers=headers)

        if request.status_code == 200:
            return request.json()
        else:
            raise Exception(
            """
            Query failed to run by returning code of {}. {}
            """.format(request.status_code, self.req_data))

    def mutate(self, submission):
        columns = {
            "cust_name" : submission['cust_name'],
            "cust_email" : submission['cust_email'],
            "cust_phone" : submission['cust_phone'],
            "int_cat" : submission['int_cat'],
            "comments" : submission['comments']
        }

        query = """
        mutation($board_id : Int!, $item_name : String!, $date : String! $columns: JSON!) {\
                    create_item (board_id: $board_id, item_name: $item_name, column_values: $columns) {\
                        board {id}
        }
        """

        variables = {
            "board_id" : 297351387,
            "item_name" : "New Inquiry: " + str(self.date),
            "date" : str(self.date),
            "columns" : json.dumps(columns)
        }

        self.req_data = {'query' : query, 'variables' : variables}

def main():
    incoming = incEmail()
    incoming.get_messages()
    submissions = incoming.parse()

    to_monday = gqlQuery()

    for submission in submissions:
        to_monday.mutate(submission)
        try:
            to_monday.post_query()
        except Exception as e:
            print(e)
        finally:
            break

if __name__ == '__main__':
    main()
