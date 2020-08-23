import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime

PVEMAIL_VAR_SAVEFORMROOTDIR = r"C:\app\PHONEVER\SAVEDFORMS"
IMAP4_SERVER_NAME = "imap.mail.com"
PVEMAIL_VAR_SARCHIVE_EMAIL_FOLDER_NAME = "OldPhoneVerEmails"
# account credentials
USERNAME = "nbeaman@mail.com"
PASSWORD = "5eaF00d!@"

DBUG = False

# create an IMAP4 class with SSL 
imap = imaplib.IMAP4_SSL(IMAP4_SERVER_NAME)

# authenticate
imap.login(USERNAME, PASSWORD)


def PVEMAIL_MoveEMailToArchiveFolder(msgId):
    # if you get an 'can't concat int to bytes' error, this means msgId needs to be a string **********
    imap.copy(str(msgId), PVEMAIL_VAR_SARCHIVE_EMAIL_FOLDER_NAME)
    imap.store(str(msgId), '+FLAGS', '\\Deleted')
    imap.expunge()


def PVEMAIL_Close_Connection_To_EmailServer():
    imap.close()
    imap.logout()

def PVEMAIL_GetAllEmailsInINBOX():

    # get ALL emails in the inbox and put them in an array (messages[])
    status, messages = imap.select("INBOX")
    return status, messages

# returns the subject from a message
def PVEMAIL_getSubject(msg):
    # decode the email subject
    subject = decode_header(msg["Subject"])[0][0]
    if isinstance(subject, bytes):
        # if it's a bytes, decode to str
        subject = subject.decode()
    if DBUG: print("SUBJECT: " + subject)
    return subject



# saves the file (payload) to the directory (SAVEFORMROOTDIR) with the filename (filename)
def PVEMAIL_saveAttachment(SAVEFORMROOTDIR, filename, payload):
    filepath=os.path.join(SAVEFORMROOTDIR, filename)
    if DBUG: print("FILE PATH: " + filepath)
    # download attachment and save it
    open(filepath, "wb").write(payload)

def PVEMAIL_AppendDateTimeToFileName(filename):
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

def PVEMAIL_getEmpFullNameFromBody( body ):

    body = str(body)

    StringBeforeFullName = "<b>To:</b>"
    StringAfterFullName = "&lt;"

    StringBeforeFullNameINDEX = body.find(StringBeforeFullName)
    tempTxt = body[StringBeforeFullNameINDEX + len(StringBeforeFullName) :StringBeforeFullNameINDEX + 50]
    if DBUG == 2: print("getEmpFullNameFromBody: StringBeforeFullname is '" + StringBeforeFullName + "' located at " + str(StringBeforeFullNameINDEX) + " characters in of Body. tempTxt=>" + tempTxt + "<")

    StringAfterFullNameINDEX = tempTxt.find(StringAfterFullName)
    EmpFullName = tempTxt[0:StringAfterFullNameINDEX-1]

    EmpFullName = EmpFullName.strip()

    if DBUG == 2: print("getEmpFullNameFromBody: StringAfterFullName is '" + StringAfterFullName + "' located at " + str(StringAfterFullNameINDEX) + " characters in of Body. EmpFullName=>" + EmpFullName + "<")

    if len(EmpFullName) < 2:
        return False
    else:
        return (EmpFullName)

    if DBUG: print("Full Name from email body: >" + FULLNAME + "<  Username from email body: >" + USERNAME + "<")


def PVEMAIL_getUsernameFromBody( body, EmpName):

    StringBeforeUsername = EmpName + " &lt;"
    StringAfterUsername = "@fau.edu"

    StringBeforeINDEX = body.find(StringBeforeUsername)
    tempTxt = body[StringBeforeINDEX + len(StringBeforeUsername) :StringBeforeINDEX + 50]
    if DBUG == 2: print("getUsernameFromBody: StringBeforeUsername is '" + StringBeforeUsername + "' located at " + str(StringBeforeINDEX) + " characters in of Body. tempTxt=>" + tempTxt + "<")

    StringAfterINDEX = tempTxt.find(StringAfterUsername)
    EmpUsername = tempTxt[0:StringAfterINDEX]

    EmpUsername = EmpUsername.strip()

    if DBUG == 2: print("getUsernameFromBody: StringAfterUsername is '" + StringAfterUsername + "' located at " + str(StringAfterINDEX) + " characters in of Body. EmpUsername=>" + EmpUsername + "<")

    if len(EmpUsername) < 2:
        return False
    else:
        return (EmpUsername)

def PVEMAIL_GetEmailForIndex(i):
    # Is msg in this format (text1, text2, text3, etc..) wich is a "tuple" in python
    # Then this is the email part of msg

    res, msg = imap.fetch(str(i), "(RFC822)")
    

    for response in msg:
        if isinstance(response, tuple):
            vReturn = email.message_from_bytes(response[1])

    return vReturn

def PVEMAIL_This_Is_A_Phone_Verification_Email( vEmail):
    # LATER: IF THE SUBJECT DOES NOT CONTAIN "Telephone and Wireless Usage" THEN IT IS NOT A PHONEVAR EMAIL
    if vEmail.find("Telephone and Wireless Usage") > 0:
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
        if DBUG: print("content_type: " + content_type + " || " + "content_disposition: " + content_disposition)

        try:
            # get the email body if this part has it
            body = part.get_payload(decode=True).decode()
        except:
            pass

    return body

def PVEMAIL_GetFileNameOfAttachment(EMail):
    # run through each part of the email in this for loop
    for part in EMail.walk():     #usually has 5 parts to iterate through
        # extract content type of the current email "part"
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))
        if DBUG: print("content_type: " + content_type + " || " + "content_disposition: " + content_disposition)

        if "attachment" in content_disposition:
            # get filename
            filename = part.get_filename()

    return filename

def PVEMAIL_GetEmailAttachment(EMail):
    # run through each part of the email in this for loop
    for part in EMail.walk():     #usually has 5 parts to iterate through
        # extract content type of the current email "part"
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))
        if DBUG: print("content_type: " + content_type + " || " + "content_disposition: " + content_disposition)

        if "attachment" in content_disposition:
            # get filename
            filename = part.get_filename()
            AttachedFilePayload = part.get_payload(decode=True)

    return AttachedFilePayload