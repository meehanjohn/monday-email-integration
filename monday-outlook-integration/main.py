import requests
import creds
import imaplib
import base64
import os
import email
from bs4 import BeautifulSoup

def get_email():
    email_user = creds.email
    email_pw = creds.password
    host = creds.server
    port = creds.imap_port

    mail = imaplib.IMAP4_SSL(host, port)
    mail.login(email_user, email_pw)

    mail.select('Inbox')
    type, data = mail.search(None, 'ALL')

    convert_emails = {}

    for num in data[0].split():
        typ, data = mail.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        subject = email_message['subject']

        if "Response from Amuneal" in subject:
            if email_message.is_multipart():
                for part in email_message.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))

                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        body = part.get_payload(decode=True)
                        break
            else:
                body = email_message.get_payload(decode=True)

            convert_emails[int(num)] = body

    soup = BeautifulSoup(body, 'lxml')

    elements = soup.find_all('p','MsoNormal')

    cust_phone = ""
    cust_email = ""
    cust_name = ""
    int_cat = ""
    comments = ""

    for element in elements:
        if "PHONE" in element.get_text():
            cust_phone = list(element.next_elements)[8].get_text().strip()
        elif "EMAIL" in element.get_text():
            cust_email = list(element.next_elements)[8].get_text().strip()
        elif "FULL NAME" in element.get_text():
            cust_name = list(element.next_elements)[8].get_text().strip()
        elif "Choose Interest Category" in element.get_text():
            int_cat = list(element.next_elements)[8].get_text().strip()
        elif "COMMENTS OR ADDITIONAL INFORMATION" in element.get_text():
            comments = list(element.next_elements)[8].get_text().strip()

    submission = {'Customer Name': cust_name,
                  'Customer Email': cust_email,
                  'Customer Phone': cust_phone,
                  'Interest Category': int_cat,
                  'Comments': comments}

    return submission


def run_query():

    query = "{account{id, name}}"

    headers = {"Authorization" : creds.api_token}

    request = requests.post(creds.monday_api_url,
                            json={"query": query},
                            headers=headers)

    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
        """
        Query failed to run by returning code of {}. {}
        """.format(request.status_code, query))



def main():
    email_contents = get_email()

    run_query(email_contents)

if __name__ == '__main__':
    main()
