columns = {
    "text" : key_verify('FULL NAME'),
    "text0" : key_verify('EMAIL'),
    "text5" : key_verify('PHONE'),
    "text2" : key_verify('Choose Interest Category'),
    "comments_or_additional_information7" : key_verify('COMMENTS OR ADDITIONAL INFORMATION'),
    "text7" : key_verify('Interested in:'),
    "date7" : str(self.date)
}

variables = {
    "board_id" : 297351387,
    "item_name" : "New Inquiry: " + str(self.date),
    "columns" : json.dumps(columns)
}

subject = "Response from Amuneal"
folder_name = "Webform_Inquiries"
