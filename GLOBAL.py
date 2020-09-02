# Email account credentials
GLOBAL_PVEMAIL_MAILBOX_USERNAME = "email@address.com"
GLOBAL_PVEMAIL_MAILBOX_PASSWORD = "mailboxPassword"

GLOBAL_FOLDER_WHERE_FORMS_ARE_SAVED					= "SAVEDFORMS"
GLOBAL_PVDB_CONN									= r'C:\myapp\database\databaseName.accdb'

GLOBAL_PDFOCR_TEMPFOLDER							= r"C:\myapp\TEMP"
GLOBAL_PDFOCR_TESSERACT_FILE_LOCATION				= r'C:\Program Files\Tesseract-OCR\tesseract.exe'

GLOBAL_IMAP4_SERVER_NAME                           = "imap.mailServer.com"
GLOBAL_IMAP4_PORT_NUMBER                           = 993

GLOBAL_PVEMAIL_VAR_ARCHIVE_EMAIL_FOLDER_NAME       = "OldPhoneVerEmails"
GLOBAL_PVEMAIL_VAR_NOT_PHONEVER_EMAIL_FOLDER_NAME  = "NotPhoneVerEmails"

GLOBAL_PVEMAIL_TEXT_IN_SUBJECT_MUST_CONTAIN_TXT    = "Telephone and Wireless Usage"
# PVEMAIL_TEXT_BEGINING_OF_ORIGIONAL_BODY is used to find the correct area of the text in the email Body we need.  For example, if a Phone Verification
# email was passed arround and forwarded many times there will be many "<b>Sent:</b>" and "<b>To:</b>" texts in the email body.
# We need the 'To:' portion from the origional email message.  To find this, find the first part of the origional Body using
# the function PVEMAIL_GetPortionOfBodyWeNeed( body ) to return the correct text used to find the username, full name, and email date.
GLOBAL_PVEMAIL_TEXT_BEGINING_OF_ORIGIONAL_BODY     = "A wired and wireless usage verification form has been submitted"
GLOBAL_PVEMAIL_STR_BEFORE_DATE_SENT                = "<b>Sent:</b>"
GLOBAL_PVEMAIL_STR_AFTER_DATE_SENT                 = "<br>"
GLOBAL_PVEMAIL_STR_BEFORE_FULLNAME                 = "<b>To:</b>"
GLOBAL_PVEMAIL_STR_AFTER_FULLNAME                  = "&lt;"
GLOBAL_PVEMAIL_STR_BEFORE_USERNAME                 = " &lt;"
GLOBAL_PVEMAIL_STR_AFTER_USERNAME                  = "@fau.edu"