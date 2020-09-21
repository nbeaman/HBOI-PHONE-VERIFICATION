import os
from datetime import datetime

from PDFOCR import PDFOCR_GetBillPeriodAndFullName
from PVEMAIL import PVEMAIL_GetEmailForIndex, PVEMAIL_GetAllEmailsInINBOX, PVEMAIL_getSubject,\
   PVEMAIL_This_Is_A_Phone_Verification_Email, PVEMAIL_GetEmailBody, PVEMAIL_GetFileNameOfAttachment, PVEMAIL_GetEmailAttachment, PVEMAIL_getEmpFullNameFromBody,PVEMAIL_GetOrigionalEmailSentOnDate,\
   PVEMAIL_getUsernameFromBody, PVEMAIL_AppendDateTimeToFileName, PVEMAIL_saveAttachment, PVEMAIL_Close_Connection_To_EmailServer, PVEMAIL_SET_FLAG_Delete_PhoneVerification_Email,\
   PVEMAIL_MoveEMailTo_NotPhoneVerEmails_UnderInbox, PVEMAIL_Expunge_FLAGGED_Emails, PVEMAIL_Empty_Trash_Folder, PVEMAIL_GetUsernameFromAttachedFileName

from PVDB import PVDB_UserExists, PVDB_AddUser, PVDB_UpdateFullName, PVDB_AddPhoneVerRecord, PVDB_PhoneVerRecordExists, PVDB_UserHasFullNameEntered
from TELLMOM import TELLMOM

#=================================[ FOR DEBUGGING ONLY APPLYS TO MAIN CODE ]=======================
#  DBUG = False     : No Debugging
#  DBUG = 1 or True : First (or low) level debugging
#  DBUG = 2         : Medium debugging level
#  DBUG = 3         : High - debug everything
DBUG = False

#===============================[ LOCAL VARS ]======================================
from GLOBAL import GLOBAL_FOLDER_WHERE_FORMS_ARE_SAVED, GLOBAL_APP_ROOT_DIRECTORY

#===============================[ LOCAL FUNCTIONS ]=================================
# check to see if the directory passed in (dir) exists, if it does not it is created
def checkDirectory(dir):
    if not os.path.isdir(dir):
        # make a folder
        os.mkdir(dir)

def AddPhoneVerificationRecord(vUSERNAME, vFullname, vBILLPERIOD, vfilename, vOrigDateTime, vOrigAttachedFileName):

    if PVDB_UserExists(vUSERNAME) == False:
        if DBUG: print("ADDING USER TO DB")
        PVDB_AddUser(vUSERNAME, vFullname)

    if PVDB_UserHasFullNameEntered(vUSERNAME, vFullname) == False:
        PVDB_UpdateFullName(vUSERNAME, vFullname)

    LinkToFile = GLOBAL_FOLDER_WHERE_FORMS_ARE_SAVED + "\\" + vBILLPERIOD + "\\" + vfilename + "#" + GLOBAL_FOLDER_WHERE_FORMS_ARE_SAVED + "\\" + vBILLPERIOD + "\\" + vfilename + "#"

    PVDB_AddPhoneVerRecord(vUSERNAME, vBILLPERIOD, vfilename, LinkToFile, vOrigDateTime, vOrigAttachedFileName)

#==================================================================================
#==================================[ MAIN CODE ]===================================
#==================================================================================

# get ALL emails in the inbox and put them in an array (messages[])
status, messages = PVEMAIL_GetAllEmailsInINBOX()
if status != 'OK':
    TELLMOM("MAIN: PVEMAIL_GetAllEmailsInINBOX: ", "status=>>" + status + "<<")

# Just get the last three emails.  The code moves the emails and runs offten so it will eventually clear the Inbox
N = 3
# get the total number of emails in the Inbox stored in the array 'messages' - this is ALL emails in the Inbox
# **** Not sure how messages turns from an array of all emails to an integer of the number of how many indexes in the array of itself? *****
messages = int(messages[0])

print("="*23 + "[ " + str(datetime.now()) + " ]" + "="*23)

# loops through each email in the array (messages) starting from the most recent message (counts backwards from N down to 1)
# the variable "i" is esentially the email Unique Identifier (UID) **********************
for i in range(messages, messages-N, -1): # DOES THIS N TIMES

    # fetch the email message by index in the array (messages) starting from highest "N" index
    EMail = PVEMAIL_GetEmailForIndex(i)

    if (EMail == 'NONE'): 
        print('NO MORE EMAILS FOUND IN INBOX')
        break         # EXIT out of for i loop

    # Get the current EMail's "Subject"
    SUBJECT = PVEMAIL_getSubject(EMail)
    
    # If the SUBJECT does not contain the text in PVEMAIL_TEXT_IN_SUBJECT_MUST_CONTAIN_TXT, then it is not a phone verification email
    if PVEMAIL_This_Is_A_Phone_Verification_Email(SUBJECT):
        
        BODY = PVEMAIL_GetEmailBody(EMail)

        SENTDATE = PVEMAIL_GetOrigionalEmailSentOnDate(BODY)

        #filename = PVEMAIL_GetFileNameOfAttachment(EMail)
        filename, AttachedFilePayload = PVEMAIL_GetEmailAttachment(EMail)

        OrigionalAttachedFileName = filename
        ORIGIONAL_EMAIL_DATE_TIME = PVEMAIL_GetOrigionalEmailSentOnDate( BODY )
        if ORIGIONAL_EMAIL_DATE_TIME == "None":
            TELLMOM("MAIN: ORIGIONAL_EMAIL_DATE_TIME: ", "Could Not Get Email Date")

        print("File: " + str(OrigionalAttachedFileName) + ", Email Date: " + str(ORIGIONAL_EMAIL_DATE_TIME))

        vIsAlreadyInDatabase = PVDB_PhoneVerRecordExists(OrigionalAttachedFileName, ORIGIONAL_EMAIL_DATE_TIME)

        if vIsAlreadyInDatabase == False:
            if DBUG: print("FILENAME=>" + filename + "<")
            # this FULLNAME is used to find the username in the body b/c it comes before the username in the body of the email
            FULLNAME = PVEMAIL_getEmpFullNameFromBody(BODY)
            # now that we know the full name from the body, use it to help find the username in the email body
            USERNAME = PVEMAIL_getUsernameFromBody( BODY, FULLNAME)
            if len(USERNAME)<2:
                USERNAME = PVEMAIL_GetUsernameFromAttachedFileName(filename)
            if len(USERNAME)<2:
                TELLMOM("MAIN: USERNAME: ", "Could Not Get USERNAME")

            print(">>" + USERNAME + "<<")

            # get the bill period and employee full name from the PDF using OCR
            PDF_BILLPERIOD, PDF_FullName = PDFOCR_GetBillPeriodAndFullName(filename, AttachedFilePayload)

            #if FULLNAME != PDF_FullName:
               #PVDB_ErrorCount( "FullNamesAreDifferent", "ADD")
               #PVDB_ErrorCountDetails( "FullNamesAreDifferent", "FULLNAME>" + FULLNAME + "< != PDF_FullName:>" + PDF_FullName + "<")

            if DBUG: print("MAIN: PDF_BILLPERIOD = >" + PDF_BILLPERIOD + "<")
            # set where to save the PDF (the directory)
            PERMINENTsaveDir = GLOBAL_APP_ROOT_DIRECTORY + "\\" + GLOBAL_FOLDER_WHERE_FORMS_ARE_SAVED + "\\" + PDF_BILLPERIOD

            # check to see if the directory already exists, if not, create it
            checkDirectory(PERMINENTsaveDir)
            # add the current date and time to the end of the file attachment before the "."
            FileNameWithDateTime = PVEMAIL_AppendDateTimeToFileName(filename)
            # save the attachment with the new name in the directory named after the "Bill Period"
            PVEMAIL_saveAttachment(PERMINENTsaveDir, FileNameWithDateTime, AttachedFilePayload)

            # put the relivent information into the database (username, PDFFileName, Bill Period, and filename that will be turned
            # into a clickable link within the database.  The date added will also be recorded in the database.
            AddPhoneVerificationRecord(USERNAME, PDF_FullName, PDF_BILLPERIOD, FileNameWithDateTime, ORIGIONAL_EMAIL_DATE_TIME, OrigionalAttachedFileName)

            # moved the processed Phone Verification email to the archive folder specified in the variable PVEMAIL_VAR_ARCHIVE_EMAIL_FOLDER_NAME
            PVEMAIL_SET_FLAG_Delete_PhoneVerification_Email(i)

            print("SUCCESS: PROCESSED AND STORED")

        else:

            PVEMAIL_SET_FLAG_Delete_PhoneVerification_Email(i)
            print("SKIPPED: ALREADY IN DATABASE")


    else:
        # This EMail is not a phone verification email, Move it to the email folder specified in the variable 
        # PVEMAIL_VAR_NOT_PHONEVER_EMAIL_FOLDER_NAME, then delete it from the Inbox
        print("Not A Phone Verification Email: Moved to NotPhoneVerEmails folder under Inbox")
        PVEMAIL_MoveEMailTo_NotPhoneVerEmails_UnderInbox(i)
    
    # prints a devider b/t messages/emails
    print("="*75)

PVEMAIL_Expunge_FLAGGED_Emails()
PVEMAIL_Empty_Trash_Folder()
PVEMAIL_Close_Connection_To_EmailServer()

#==================================================================================
#==================================================================================
#==================================================================================
