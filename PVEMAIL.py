import imaplib
import email
from email.header import decode_header
import os
#import time
from datetime import datetime

# TELLMOM is a function that will alert us that somthing went wrong with the code and it has stopped.
# it can be set to any alert you would like by coding the function (E.g. email, text, etc..)
from TELLMOM import TELLMOM

#=================================[ FOR DEBUGGING ONLY APPLIES TO PVEMAIL CODE ]===================
#  DBUG = False     : No Debugging
#  DBUG = 1 or True : First (or low) level debugging
#  DBUG = 2         : Medium debugging level
#  DBUG = 3         : High - debug everything
DBUG = False

#==================================================================================================

#=================================[ VARIABLES USED ONLY IN THE FUNCTIONS BELOW ]===================
# PVEMAIL_TEXT_BEGINING_OF_ORIGIONAL_BODY is used to find the correct area of the text in the email Body we need.  For example, if a Phone Verification
# email was passed arround and forwarded many times there will be many "<b>Sent:</b>" and "<b>To:</b>" texts in the email body.
# We need the 'To:' portion from the origional email message.  To find this, find the first part of the origional Body using
# the function PVEMAIL_GetPortionOfBodyWeNeed( body ) to return the correct text used to find the username, full name, and email date.

# the "GLOBAL.py" file holds username and passwords.  It is seperate due to version repo (GitHub.com)
# do not upload this file to GitHub as it is public and we do not want people to see this information

from GLOBAL import GLOBAL_PVEMAIL_MAILBOX_USERNAME, GLOBAL_PVEMAIL_MAILBOX_PASSWORD, GLOBAL_IMAP4_SERVER_NAME, GLOBAL_IMAP4_PORT_NUMBER, GLOBAL_PVEMAIL_VAR_ARCHIVE_EMAIL_FOLDER_NAME,\
   GLOBAL_PVEMAIL_VAR_NOT_PHONEVER_EMAIL_FOLDER_NAME, GLOBAL_PVEMAIL_TEXT_IN_SUBJECT_MUST_CONTAIN_TXT,GLOBAL_PVEMAIL_TEXT_BEGINING_OF_ORIGIONAL_BODY, GLOBAL_PVEMAIL_STR_BEFORE_DATE_SENT,\
   GLOBAL_PVEMAIL_STR_AFTER_DATE_SENT, GLOBAL_PVEMAIL_STR_BEFORE_FULLNAME, GLOBAL_PVEMAIL_STR_AFTER_FULLNAME, GLOBAL_PVEMAIL_STR_BEFORE_USERNAME,GLOBAL_PVEMAIL_STR_AFTER_USERNAME

# create an IMAP4 class with SSL. 'imap' is used by most of the functions below (global within this file)
try:
    imap = imaplib.IMAP4_SSL(GLOBAL_IMAP4_SERVER_NAME, GLOBAL_IMAP4_PORT_NUMBER)
except:
    TELLMOM("PVEMAIL MAIN: (PROBLEM CREATING imap FOR SERVER NAME: " + GLOBAL_IMAP4_SERVER_NAME + " ON PORT: " + str(GLOBAL_IMAP4_PORT_NUMBER) + ")","imaplib.IMAP4_SSL")

#imap = imaplib.IMAP4_SSL(GLOBAL_IMAP4_SERVER_NAME)

# authenticate to email server (global within this file) uses the information in "GLOBAL.py"
try:
    imap.login(GLOBAL_PVEMAIL_MAILBOX_USERNAME, GLOBAL_PVEMAIL_MAILBOX_PASSWORD)

except Exception as e:
    TELLMOM("PVEMAIL MAIN: imap.login", "PROBLEM AUTHENTICATING TO SERVER NAME: " + GLOBAL_IMAP4_SERVER_NAME + " ON PORT: " + str(GLOBAL_IMAP4_PORT_NUMBER) + ") Check GLOBAL.py file", e)

#===================================================================================================

#=================================[ VARIABLES USED IN MAIN PROGRAM (program that imports PVEMAIL]===
PVEMAIL_VAR_SAVEFORMROOTDIR                 = r"C:\app\PHONEVER\SAVEDFORMS"
#===================================================================================================

def PVEMAIL_GetEmailForIndex(i):
    # Using "try" b/c if there are no more emails in the Inbox, this would throw an error
    # if 'fetch' does cuase an error, it will go to 'except:' instead - returning 'NONE' to
    # the main program so that it may deal with it
    # Remember that 'imap' is a global variable in this file
    try:
        # retreive the email into the variable 'msg'
        res, msg = imap.fetch(str(i), "(RFC822)")

        # loop through 'msg' to find the actual email
        for response in msg:
            # Is msg in this format (text1, text2, text3, etc..) which is a "tuple" in python
            # Then this is the email part of msg
            if isinstance(response, tuple):
                vReturn = email.message_from_bytes(response[1])
        return vReturn
    except Exception as e:      #loads the last exception in variable e (tuplet)

        if str(e) == "FETCH command error: BAD [b'number 0']":
            # No more emails found, send 'NONE' to calling program
            return 'NONE'
        else:
            # somthing else went wrong
            TELLMOM("PVEMAIL_GetEmailForIndex(" + str(i) + ")","imap.fetch",e)

def PVEMAIL_MoveEMailTo_ArchiveFolder_UnderInbox(i):
    # if you get a 'can't concat int to bytes' error, this means msgId needs to be a string
    # that is why the use of the 'str' function to convert it to a string.  

    resp = imap.copy(str(i), GLOBAL_PVEMAIL_VAR_ARCHIVE_EMAIL_FOLDER_NAME)
    if str(resp[0]) == 'NO':
        TELLMOM("PVEMAIL_MoveEMailTo_ArchiveFolder_UnderInbox",str(resp))

    # Mark email as 'Deleted'
    imap.store(str(i), '+FLAGS', '\\Deleted')
    # Delete all emails Marked as 'Deleted'
    imap.expunge()

def PVEMAIL_MoveEMailTo_NotPhoneVerEmails_UnderInbox(i):
    # If we find an email that is not a phone ver email, then this function is called. It
    # copies the email (i) to the folder under the Inbox called what ever the variable
    # GLOBAL_PVEMAIL_VAR_NOT_PHONEVER_EMAIL_FOLDER_NAME is set to. Then deletes the origional under Inbox

    resp = imap.copy(str(i), GLOBAL_PVEMAIL_VAR_NOT_PHONEVER_EMAIL_FOLDER_NAME)
    if str(resp[0]) == 'NO':
        TELLMOM("PVEMAIL_MoveEMailTo_NotPhoneVerEmails_UnderInbox",str(resp))

    # Mark email as 'Deleted'
    imap.store(str(i), '+FLAGS', '\\Deleted')
    # Delete all emails Marked as 'Deleted'
    imap.expunge()

def PVEMAIL_Close_Connection_To_EmailServer():
    imap.close()
    imap.logout()

def PVEMAIL_GetAllEmailsInINBOX():
    # get ALL emails in the inbox and puts them in an array (messages[])
    try:
        status, messages = imap.select("INBOX")
    except Exception as e:
        TELLMOM("PVEMAIL_GetAllEmailsInINBOX","imap.select",e)

    return status, messages

def PVEMAIL_getSubject(msg):
    # returns the subject from a message (msg) which is one email (i think it's called an "email collection")
    # decode the email subject to a string if needed

    subject = decode_header(msg["Subject"])[0][0]
    if isinstance(subject, bytes):
        # if it's a bytes, decode to str
        subject = subject.decode()
    if DBUG: print("SUBJECT: " + subject)
    return subject


def PVEMAIL_saveAttachment(SAVEFORMROOTDIR, filename, payload):
    # saves the file (payload) to the directory (SAVEFORMROOTDIR) with the filename (filename)

    filepath=os.path.join(SAVEFORMROOTDIR, filename)
    if DBUG: print("FILE PATH: " + filepath)
    # download attachment and save it
    open(filepath, "wb").write(payload)

def PVEMAIL_AppendDateTimeToFileName(filename):
    # takes the name of the file attachment and adds the data/time to the end (before the .PDF)

    now = datetime.now()
    StrDateTime = now.strftime("%m-%d-%Y(%H-%M-%S)")

    # find last occurrence of "." in filename
    DotInext = filename.rfind(".")
    # seperate them into "username.znumber.raw" and ".pdf"
    leftOfDot = filename[:DotInext]
    rightOfDot = filename[DotInext:]
    # insert Date & Time into filename
    newFileName = leftOfDot + "-" + StrDateTime + rightOfDot
    return newFileName

def PVEMAIL_This_Is_A_Phone_Verification_Email( EmailSubject ):
    # See if the Subject of the email contains the correct characters stored in  GLOBAL_PVEMAIL_TEXT_IN_SUBJECT_MUST_CONTAIN_TXT
    # If not then the email is NOT a Phone Verification email

    if EmailSubject.find(GLOBAL_PVEMAIL_TEXT_IN_SUBJECT_MUST_CONTAIN_TXT) > 0:
        return True
    else:
        return False

def PVEMAIL_GetEmailBody(EMail):
    body=""
    # run through each part of the email in this for loop
    for part in EMail.walk():     #usually has 5 parts to iterate through
        # extract content type of the current email "part"
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))
        if DBUG==2: print("content_type: " + content_type + " || " + "content_disposition: " + content_disposition)

        try:
            # get the email body if this "part" has it
            body = part.get_payload(decode=True).decode()
        except:
            pass

    if len(body) < 256:
        TELLMOM("PVEMAIL_GetEmailBody", "body is too short. body=>>" + str(body) + "<<")
    else:
        return (body)

def PVEMAIL_GetFileNameOfAttachment(EMail):
    # run through each "part" of the email in this for loop
    for part in EMail.walk():     #usually has 5 parts to iterate through
        # extract content type of the current email "part"
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))
        if DBUG==2: print("content_type: " + content_type + " || " + "content_disposition: " + content_disposition)

        if "attachment" in content_disposition:
            # get filename
            filename = part.get_filename()

    return filename

def PVEMAIL_GetEmailAttachment(EMail):
    # run through each "part" of the email in this for loop
    for part in EMail.walk():     #usually has 5 parts to iterate through
        # extract content type of the current email "part"
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))
        if DBUG: print("content_type: " + content_type + " || " + "content_disposition: " + content_disposition)

        if "attachment" in content_disposition:
            # get filename
            filename = part.get_filename()
            AttachedFilePayload = part.get_payload(decode=True)

    if len(AttachedFilePayload) <256:
        TELLMOM:("PVEMAIL_GetEmailAttachment:", "No Attachment Found")
    else:
        return filename, AttachedFilePayload


#------------------------------------------------------------------
#---------------[ PARSING BODY TEXT FUNCTIONS ]--------------------
# NOTE: for splitting up a string : StringName[StartIndex:EndIndex]
#------------------------------------------------------------------

def PVEMAIL_GetPortionOfBodyWeNeed( body):   
    EndIndex = body.find(GLOBAL_PVEMAIL_TEXT_BEGINING_OF_ORIGIONAL_BODY)
    StartIndex = EndIndex - 400
    tempTXT = body[StartIndex:EndIndex]
    return tempTXT

def PVEMAIL_GetOrigionalEmailSentOnDate( body):
    DateTime = ""

    body = PVEMAIL_GetPortionOfBodyWeNeed( body)

    StartIndex = body.find(GLOBAL_PVEMAIL_STR_BEFORE_DATE_SENT)
    StartIndex = StartIndex + len(GLOBAL_PVEMAIL_STR_BEFORE_DATE_SENT)

    textTMP = body[StartIndex:StartIndex+50]
    EndIndex = textTMP.find(GLOBAL_PVEMAIL_STR_AFTER_DATE_SENT)
    textTMP = textTMP[0:EndIndex]
    textTMP = textTMP.strip()

    #textTMP = 'Thursday, July 23, 2020 1:37 PM'

    try:
         DateTime = datetime.strptime(textTMP,'%A, %B %d, %Y %I:%M %p')
         return str(DateTime)

    except Exception as e:
        TELLMOM:("PVEMAIL_GetOrigionalEmailSentOnDate:", "Could not get date time from email Body of origional email", e)


    #GLOBAL_PVEMAIL_STR_BEFORE_DATE_SENT                = "<b>Sent:</b>"
    #GLOBAL_PVEMAIL_STR_AFTER_DATE_SENT                 = "<br>"

def PVEMAIL_getEmpFullNameFromBody( body ):
    #--------------------------------------------------------------------------------------------------
    # THIS FUNCTION ONLY WORKS IF THE EMPLOYEE'S FULL NAME IS IN THE BODY JUST AFTER GLOBAL_PVEMAIL_STR_BEFORE_FULLNAME
    # Example: "<b>To:</b> Nelson Beaman &lt;nbeaman@fau.edu&gt;<br>"
    #--------------------------------------------------------------------------------------------------
    # Parses "body" to find the employee's full name within the text

    # body is already the text from the email body.  Used str to make sure
    body = str(body)

    body = PVEMAIL_GetPortionOfBodyWeNeed( body)

    # find the string stored in GLOBAL_PVEMAIL_STR_BEFORE_FULLNAME, and set tempTXT to "Nelson Beaman ..... rest of body)
    GLOBAL_PVEMAIL_STR_BEFORE_FULLNAMEINDEX = body.find(GLOBAL_PVEMAIL_STR_BEFORE_FULLNAME)
    tempTxt = body[GLOBAL_PVEMAIL_STR_BEFORE_FULLNAMEINDEX + len(GLOBAL_PVEMAIL_STR_BEFORE_FULLNAME) :GLOBAL_PVEMAIL_STR_BEFORE_FULLNAMEINDEX + 256]
    if DBUG == 2: print("getEmpFullNameFromBody: GLOBAL_PVEMAIL_STR_BEFORE_FULLNAME is '" + GLOBAL_PVEMAIL_STR_BEFORE_FULLNAME + "' located at " + str(GLOBAL_PVEMAIL_STR_BEFORE_FULLNAMEINDEX) + " characters in of Body. tempTxt=>" + tempTxt + "<")
    
    # find the string in tempTXT stored in GLOBAL_PVEMAIL_STR_AFTER_FULLNAME, and set EmpFullName to somthing like "Nelson Beaman  "
    GLOBAL_PVEMAIL_STR_AFTER_FULLNAMEINDEX = tempTxt.find(GLOBAL_PVEMAIL_STR_AFTER_FULLNAME)
    EmpFullName = tempTxt[0:GLOBAL_PVEMAIL_STR_AFTER_FULLNAMEINDEX-1]

    # remove any space from the beginning and end of EmpFullName
    EmpFullName = EmpFullName.strip()

    # make sure there are no CL or LF (a return) in the name
    EmpFullName = EmpFullName.replace(chr(10),"")
    EmpFullName = EmpFullName.replace(chr(13),"")

    if DBUG == 2: print("PVEMAIL_getEmpFullNameFromBody: GLOBAL_PVEMAIL_STR_AFTER_FULLNAME is '" + GLOBAL_PVEMAIL_STR_AFTER_FULLNAME + "' located at " + str(GLOBAL_PVEMAIL_STR_AFTER_FULLNAMEINDEX) + " characters in of Body. EmpFullName=>" + EmpFullName + "<")
    if DBUG: print("PVEMAIL_getEmpFullNameFromBody: Full Name from email body: >" + EmpFullName + "<")

    if len(EmpFullName) < 2:
        TELLMOM("PVEMAIL_getEmpFullNameFromBody", "FULLNAME from body is too short (may not be a name). FULLNAME=>>" + EmpFullName + "<<")
    elif EmpFullName.find(" ") == -1:
        TELLMOM("PVEMAIL_getEmpFullNameFromBody", "FULLNAME from body has no spaces in it (may not be a name). FULLNAME=>>" + EmpFullName + "<<")
    else:
        return (EmpFullName)


def PVEMAIL_getUsernameFromBody( body, EmpName):
    #--------------------------------------------------------------------------------------------------
    # THIS FUNCTION ONLY WORKS IF THE EMPLOYEE'S FULL NAME IS BEFORE THE USERNAME WITHIN 256 CHARACTERS
    # Example: "<b>To:</b> Nelson Beaman &lt;nbeaman@fau.edu&gt;<br>"
    #--------------------------------------------------------------------------------------------------
    # Add Employee's Full Name to the begining of the string stored in GLOBAL_PVEMAIL_STR_BEFORE_USERNAME
    # for example "Nelson Beaman &lt;"
    StringBeforeUsername = EmpName + GLOBAL_PVEMAIL_STR_BEFORE_USERNAME

    body = PVEMAIL_GetPortionOfBodyWeNeed( body)

    # Find the text StringBeforeUsername, then set tempTXT to all the text after that
    # because we know the username is found just after the employee's full name in the body of the email
    StringBeforeINDEX = body.find(StringBeforeUsername)
    tempTxt = body[StringBeforeINDEX + len(StringBeforeUsername) :StringBeforeINDEX + 256]

    if DBUG == 2: print("getUsernameFromBody: StringBeforeUsername is '" + StringBeforeUsername + "' located at " + str(StringBeforeINDEX) + " characters in of Body. tempTxt=>" + tempTxt + "<")

    # find the string stored in GLOBAL_PVEMAIL_STR_AFTER_USERNAME, then return all of the text BEFORE this text
    StringAfterINDEX = tempTxt.find(GLOBAL_PVEMAIL_STR_AFTER_USERNAME)
    EmpUsername = tempTxt[0:StringAfterINDEX]

    EmpUsername = EmpUsername.strip()

    # make sure there are no CL or LF (a return) in the username
    EmpUsername = EmpUsername.replace(chr(10),"")
    EmpUsername = EmpUsername.replace(chr(13),"")

    if DBUG == 2: print("getUsernameFromBody: GLOBAL_PVEMAIL_STR_AFTER_USERNAME is '" + GLOBAL_PVEMAIL_STR_AFTER_USERNAME + "' located at " + str(StringAfterINDEX) + " characters in of Body. EmpUsername=>" + EmpUsername + "<")

    if len(EmpUsername) < 2:
        TELLMOM("PVEMAIL_getUsernameFromBody", "USERNAME from body is too short (may not be a username). EmpUsername=>>" + EmpUsername + "<<")
    else:
        return (EmpUsername)

#------------------------------------------------------------------
#---------------[ END OF: PARSING BODY TEXT FUNCTIONS ]------------
# NOTE: for splitting up a string : StringName[StartIndex:EndIndex]
#------------------------------------------------------------------