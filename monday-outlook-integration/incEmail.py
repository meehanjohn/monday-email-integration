import creds                    # Use-specific credentials file
import params                   # Exposed parameters file
import imaplib                  # To connect to IMAP email port
import email                    # To search & read emails
from bs4 import BeautifulSoup   # To parse email content

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
