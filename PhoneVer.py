import imaplib
import email
from email.header import decode_header
import os

DBUG = False
saveDir = "TEST"


# returns the subject from a message
def getSubject(msg):
    # decode the email subject
    subject = decode_header(msg["Subject"])[0][0]
    if isinstance(subject, bytes):
        # if it's a bytes, decode to str
        subject = subject.decode()
    return subject

# check to see if the directory passed in (dir) exists, if it does not it is created
def checkDirectory(dir):
    if not os.path.isdir(dir):
        # make a folder
        os.mkdir(dir)

# saves the file (payload) to the directory (saveDir) with the filename (filename)
def saveAttachment(saveDir, filename, payload):
    filepath=os.path.join(saveDir, filename)
    print("FILE PATH: " + filepath)
    # download attachment and save it
    open(filepath, "wb").write(payload)



def getEmpFullNameFromBody( body ):

    body = str(body)

    StringBeforeFullName = "<b>To:</b>"
    StringAfterFullName = "&lt;"

    StringBeforeFullNameINDEX = body.find(StringBeforeFullName)
    tempTxt = body[StringBeforeFullNameINDEX + len(StringBeforeFullName) :StringBeforeFullNameINDEX + 50]
    if DBUG: print("getEmpFullNameFromBody: StringBeforeFullname is '" + StringBeforeFullName + "' located at " + str(StringBeforeFullNameINDEX) + " characters in of Body. tempTxt=>" + tempTxt + "<")

    StringAfterFullNameINDEX = tempTxt.find(StringAfterFullName)
    EmpFullName = tempTxt[0:StringAfterFullNameINDEX-1]

    EmpFullName = EmpFullName.strip()

    if DBUG: print("getEmpFullNameFromBody: StringAfterFullName is '" + StringAfterFullName + "' located at " + str(StringAfterFullNameINDEX) + " characters in of Body. EmpFullName=>" + EmpFullName + "<")

    if len(EmpFullName) < 2:
        return False
    else:
        return (EmpFullName)

def getUsernameFromBody( body, EmpName):

    StringBeforeUsername = EmpName + " &lt;"
    StringAfterUsername = "@fau.edu"

    StringBeforeINDEX = body.find(StringBeforeUsername)
    tempTxt = body[StringBeforeINDEX + len(StringBeforeUsername) :StringBeforeINDEX + 50]
    print("getUsernameFromBody: StringBeforeUsername is '" + StringBeforeUsername + "' located at " + str(StringBeforeINDEX) + " characters in of Body. tempTxt=>" + tempTxt + "<")

    StringAfterINDEX = tempTxt.find(StringAfterUsername)
    EmpUsername = tempTxt[0:StringAfterINDEX]

    EmpUsername = EmpUsername.strip()

    print("getUsernameFromBody: StringAfterUsername is '" + StringAfterUsername + "' located at " + str(StringAfterINDEX) + " characters in of Body. EmpUsername=>" + EmpUsername + "<")

    if len(EmpUsername) < 2:
        return False
    else:
        return (EmpUsername)

# for debugging.  This is used to display that something went wrong
def TELLMOM(subject, what):
    print("I AM TELLING! This is not a Phone Verification Email." + " SUBJECT: " + subject + " >>" + what + "<<")

# account credentials
username = "nbeaman@mail.com"
password = "5eaF00d!@"

# create an IMAP4 class with SSL 
imap = imaplib.IMAP4_SSL("imap.mail.com")
# authenticate
imap.login(username, password)

# get ALL emails in the inbox and put them in an array (messages[])
status, messages = imap.select("INBOX")
# for testing, just get the last three emails
N = 3
# total number of emails (What does this do?????)
messages = int(messages[0])

# loops through each email in the array (messages) starting from the most recent message (counts backwards down to 1)
for i in range(messages, messages-N, -1):
    
    # fetch the email message by index in the array (messages) starting from last/highest index
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        # Is msg in this format (text1, text2, text3, etc..) wich is a "tuple" in python
        # for example (email format, subject and body, attachment)
        # If it's not, then this is not a phone verification email, so TELLMOM()
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])

            # LATER: IF THE SUBJECT DOES NOT CONTAIN "Telephone and Wireless Usage" THEN DELETE IT FROM THE INBOX
            SUBJECT = getSubject(msg)
            if DBUG: print("SUBJECT: " + SUBJECT)

            # if the email message is multipart (NOT SURE WHAT THAT MEANS?), if no
            # then this is not a phone verification email, so TELLMOM()
            if msg.is_multipart():
                # iterate over email parts
                filename = ""
                BODY = ""
                # run through each part of the email in this for loop
                for part in msg.walk():     #usually has 5 parts to iterate through
                    # extract content type of the current email "part"
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if DBUG: print("content_type: " + content_type + " || " + "content_disposition: " + content_disposition)

                    try:
                        # get the email body if this part has it
                        body = part.get_payload(decode=True).decode()
                        BODY = body
                    except:
                        pass

                    if "attachment" in content_disposition:
                        # get filename
                        filename = part.get_filename()

            else:
                TELLMOM(SUBJECT, "NOT MULTIPART MSG")
                # THIS REALLY SHOULD BE REMOVE THE EMAIL FROM THE INBOX IF THE SUBJECT DOES NOT SAY IT IS A PHONE VERIFICATION EMAIL

            if filename:
                # if there is an attachment in the email
                checkDirectory(saveDir)
                saveAttachment(saveDir, filename, part.get_payload(decode=True))

            else:
                TELLMOM(SUBJECT, "NO ATTACHMENT")

            #print(BODY)

            if filename:
                FULLNAME = getEmpFullNameFromBody(BODY)
                USERNAME = getUsernameFromBody( BODY, FULLNAME)
                #if DBUG: print("Full Name from email body: " + FULLNAME + "  Username from email body: " + USERNAME)


            # prints a devider b/t messages/emails
            if DBUG: print("="*100)

imap.close()
imap.logout()
