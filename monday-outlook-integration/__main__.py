from gqlQuery import gqlQuery
from incEmail import incEmail

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
