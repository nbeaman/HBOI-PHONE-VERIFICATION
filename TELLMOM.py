from datetime import datetime
import sys
import smtplib

from GLOBAL import GLOBAL_TELLMOM_WHO_TO_ALERT, GLOBAL_PVEMAIL_MAILBOX_USERNAME, GLOBAL_PVEMAIL_MAILBOX_PASSWORD

#GLOBAL_PVEMAIL_MAILBOX_USERNAME = "hboi@mail.com"
#GLOBAL_PVEMAIL_MAILBOX_PASSWORD = "5eaF00d!@"

from email.message import EmailMessage

# for debugging.  This is used to display that something went wrong
# The "*" before the argument 'e' means it's optional
def TELLMOM(FromWhere, What, *e):
    print("=====================================================================")
    print(datetime.now())
    print("TELLMOM   : From(" + FromWhere + ")")
    print("WHAT      : >>" + What + "<<")
    if len(e) > 0:
        print("EXCEPTION : >>" + str(e) + "<<")
    print("=====================================================================")

    # Sends an email if there's an error with the PhoneVer script
    # Sender's user credentials
    EmailText = ""
    EmailText = '=======================[ ' + str(datetime.now()) + ' ]=================================\n\nTarpon Server\n\nThere was an error with the PhoneVer Python Script(s)\n\nFrom: ' + FromWhere + '\n\nWhat: ' + What + '\n\n'

    if len(e) > 0:
        EmailText = EmailText + "Exception: " + str(e)

    EmailText = EmailText + "===================================================================================\n\n"

    # Message composition
    msg = EmailMessage()
    msg['Subject'] = 'PhoneVer Error'  # Subject of email
    msg['From'] = GLOBAL_PVEMAIL_MAILBOX_USERNAME
    msg['To'] = GLOBAL_TELLMOM_WHO_TO_ALERT  # Receiver(s) of the email. Use a comma for more than one receiver
    msg.set_content(EmailText)

    # Sends the email
    with smtplib.SMTP_SSL('smtp.mail.com', 465) as smtp:
        smtp.login(GLOBAL_PVEMAIL_MAILBOX_USERNAME, GLOBAL_PVEMAIL_MAILBOX_PASSWORD)  # This command log ins to the SMTP Library
        smtp.send_message(msg)  # Sends the message

    sys.exit('Execution of code stopped by TELLMOM')
