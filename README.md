# monday-email-integration

A program to automate tracking of customer web-queries using monday.com.

The user drags incoming web request emails into a designated folder, which
will be scanned intermittently. Emails are parsed for relevant information,
which is then used to create new board items on [Monday](monday.com) using
their GraphQL API.

# Installation

# Use

## Create `creds.py` in project folder
email = 'youremail@example.com'
password = 'XXXXXX'
server = 'email.provider.server'
account_type = '[IMAP/POP/ETC]'
imap_port = 'XXX'
api_token = [How to get an access token](https://monday.com/developers/v2#authentication-section-accessing-tokens)
monday_url = 'https://api.monday.com/v2'

# TODO
