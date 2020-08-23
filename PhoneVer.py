import os

from PDFOCR import PDFOCR_BillPeriod
from PVEMAIL import PVEMAIL_GetEmailForIndex, PVEMAIL_GetAllEmailsInINBOX, PVEMAIL_getSubject,\
   PVEMAIL_This_Is_A_Phone_Verification_Email, PVEMAIL_GetEmailBody, PVEMAIL_GetFileNameOfAttachment, PVEMAIL_GetEmailAttachment, PVEMAIL_getEmpFullNameFromBody,\
   PVEMAIL_getUsernameFromBody, PVEMAIL_AppendDateTimeToFileName, PVEMAIL_saveAttachment, PVEMAIL_Close_Connection_To_EmailServer, PVEMAIL_MoveEMailTo_ArchiveFolder_UnderInbox, PVEMAIL_MoveEMailTo_NotPhoneVerEmails_UnderInbox,\
   PVEMAIL_VAR_SAVEFORMROOTDIR

from TELLMOM import TELLMOM

DBUG = 1

# get ALL emails in the inbox and put them in an array (messages[])
status, messages = PVEMAIL_GetAllEmailsInINBOX()

# Just get the last three emails
N = 3
# total number of emails (What does this do?????)
messages = int(messages[0])


# check to see if the directory passed in (dir) exists, if it does not it is created
def checkDirectory(dir):
    if not os.path.isdir(dir):
        # make a folder
        os.mkdir(dir)


# loops through each email in the array (messages) starting from the most recent message (counts backwards from N down to 1)
# the variable "i" is esentially the email Unique Identifier (UID) **********************
for i in range(messages, messages-N, -1): # DOES THIS N TIMES
    
    # fetch the email message by index in the array (messages) starting from highest "N" index
    EMail = PVEMAIL_GetEmailForIndex(i)

    if (EMail == 'NONE'): 
        if DBUG: print('NO MORE EMAILS FOUND IN INBOX')
        break         # EXIT out of for i loop

    # Get the current EMail's "Subject"
    SUBJECT = PVEMAIL_getSubject(EMail)
    
    # If the SUBJECT does not contain the text in PVEMAIL_TEXT_IN_SUBJECT_MUST_CONTAIN_TXT, then it is not a phone verification email
    if PVEMAIL_This_Is_A_Phone_Verification_Email(SUBJECT):
        
        BODY = PVEMAIL_GetEmailBody(EMail)
        filename = PVEMAIL_GetFileNameOfAttachment(EMail)
        AttachedFilePayload = PVEMAIL_GetEmailAttachment(EMail)

        print("FILENAME=>" + filename + "<")
        FULLNAME = PVEMAIL_getEmpFullNameFromBody(BODY)
        USERNAME = PVEMAIL_getUsernameFromBody( BODY, FULLNAME)
        BILLPERIOD = PDFOCR_BillPeriod(filename, AttachedFilePayload)
        print("BILLPERIOD = >" + BILLPERIOD + "<")
        PERMINENTsaveDir = PVEMAIL_VAR_SAVEFORMROOTDIR + '\\' + BILLPERIOD
        checkDirectory(PERMINENTsaveDir)
        PVEMAIL_saveAttachment(PERMINENTsaveDir, PVEMAIL_AppendDateTimeToFileName(filename), AttachedFilePayload)

        PVEMAIL_MoveEMailTo_ArchiveFolder_UnderInbox(i)

    else:
        # This EMail is not a phone verification email, Move it, then delete it from the Inbox
        if DBUG: print("MAIN: Not A Phone Verification Email: Moved to NotPhoneVerEmails folder under Inbox, then Deleted from Inbox")
        PVEMAIL_MoveEMailTo_NotPhoneVerEmails_UnderInbox(i)
    
    # prints a devider b/t messages/emails
    if DBUG: print("="*100)

PVEMAIL_Close_Connection_To_EmailServer()


