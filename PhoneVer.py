import os

from PDFOCR import PDFOCR_BillPeriod
from PVEMAIL import PVEMAIL_GetEmailForIndex, PVEMAIL_GetAllEmailsInINBOX, PVEMAIL_getSubject,\
   PVEMAIL_This_Is_A_Phone_Verification_Email, PVEMAIL_GetEmailBody, PVEMAIL_GetFileNameOfAttachment, PVEMAIL_GetEmailAttachment, PVEMAIL_getEmpFullNameFromBody,\
   PVEMAIL_getUsernameFromBody, PVEMAIL_AppendDateTimeToFileName, PVEMAIL_saveAttachment, PVEMAIL_Close_Connection_To_EmailServer, PVEMAIL_MoveEMailToArchiveFolder,\
   PVEMAIL_VAR_SAVEFORMROOTDIR,\
   PVEMAIL_VAR_SARCHIVE_EMAIL_FOLDER_NAME



DBUG = 1

# check to see if the directory passed in (dir) exists, if it does not it is created
def checkDirectory(dir):
    if not os.path.isdir(dir):
        # make a folder
        os.mkdir(dir)

#===============================================================================
# for debugging.  This is used to display that something went wrong
def TELLMOM(subject, what):
    print("I AM TELLING! This is not a Phone Verification Email." + " SUBJECT: " + subject + " >>" + what + "<<")
#===============================================================================

# account credentials
username = "nbeaman@mail.com"
password = "5eaF00d!@"

# create an IMAP4 class with SSL 
#imap = PVEMAIL_CreateAnIMAP4Class
# authenticate
#AuthenticateResponse = PVEMAIL_UsernamePasswordAuthenticateEmailServer
#print("AuthenticateResponse: " + str(AuthenticateResponse))

status, messages = PVEMAIL_GetAllEmailsInINBOX()

# get ALL emails in the inbox and put them in an array (messages[])
#status, messages = imap.select("INBOX")
# for testing, just get the last three emails
N = 3
# total number of emails (What does this do?????)
messages = int(messages[0])





# loops through each email in the array (messages) starting from the most recent message (counts backwards down to 1)
for i in range(messages, messages-N, -1): # DOES THIS N TIMES
    
    # fetch the email message by index in the array (messages) starting from last/highest index
    #res, msg = imap.fetch(str(i), "(RFC822)")

    EMail = PVEMAIL_GetEmailForIndex(i)

    # LATER: IF THE SUBJECT DOES NOT CONTAIN "Telephone and Wireless Usage" THEN DELETE IT FROM THE INBOX
    SUBJECT = PVEMAIL_getSubject(EMail)
    

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

        PVEMAIL_MoveEMailToArchiveFolder(i)

        # prints a devider b/t messages/emails
        if DBUG: print("="*100)
    
    else:

        if DBUG: print("MAIN: Not A Phone Verification Email: Should Delete")
        # prints a devider b/t messages/emails
        if DBUG: print("="*100)

PVEMAIL_Close_Connection_To_EmailServer()


