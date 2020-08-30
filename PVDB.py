# importing the module
import pyodbc

DBUG = False

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\app\PHONEVER\phoneverifications.accdb;')

PVDB_DB_TEXT_RETURN_FOR_NULL_FIELD = 'None'

def PVDB_UserExists(vUsername):
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usernames WHERE Username = '" + vUsername + "';")
    rs = cursor.fetchall()

    if len(rs) == 0:
        return False
    else:
        return rs[0][0]     # return Username Record ID
    cursor.close()

def PVDB_AddUser(vUsername, vFullname):

    if PVDB_UserExists(vUsername):
        return False
    else:
        cursor = conn.cursor()
        vSQL = "INSERT INTO Usernames ( Username, FullName ) VALUES ('" + vUsername + "', '" + vFullname + "')"
        if DBUG: print("PVDB_AddUser: Added User: SQL ='" + vSQL + "'")
        cursor.execute(vSQL)
        conn.commit()
        return True

    cursor.close()

def PVDB_UserHasFullNameEntered(vUsername, vFullName):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usernames WHERE Username = '" + vUsername + "';")
    rs = cursor.fetchall()
    FullnameInDB = str(rs[0][2])

    if FullnameInDB == PVDB_DB_TEXT_RETURN_FOR_NULL_FIELD:
        return False
    else:
        return True
    cursor.close()

def PVDB_UpdateFullName(vUsername, vFullName):

    if not PVDB_UserExists(vUsername):
        return False
    else:
        cursor = conn.cursor()
        vSQL = "UPDATE Usernames SET FullName = '" + vFullName + "' WHERE Username = '" + vUsername + "';"
        if DBUG: print("PVDB_UpdateFullname: Updated Full Name: SQL ='" + vSQL + "'")
        cursor.execute(vSQL)
        conn.commit()
        return True

    cursor.close()

def PVDB_AddPhoneVerRecord(vUsername, vBillPeriod, vFileName, vFileLink):
    UsernameID = PVDB_UserExists(vUsername)
    if UsernameID == -1:
        return False
    else:
        cursor = conn.cursor()
        vSQL = "INSERT INTO PhoneVer (Username_id, billperiod, FileName, FileLink) VALUES (" + str(UsernameID) + ",'" + vBillPeriod + "', '" + vFileName + "', '" + vFileLink + "')"
        if DBUG: print("PVDB_AddPhoneVerRecord: Phone Verification Record added: SQL ='" + vSQL + "'")
        cursor.execute(vSQL)
        conn.commit()
        return True

    cursor.close()

def PVDB_PhoneVerRecordExists(vUsername, vBillPeriod):

    UsernameID = PVDB_UserExists(vUsername)

    cursor = conn.cursor()
    vSQL = "SELECT * FROM PhoneVer WHERE Username_id = " + str(UsernameID) + " AND billperiod = '" + vBillPeriod + "'"
    cursor.execute(vSQL)
    rs = cursor.fetchall()

    if len(rs) == 0:
        return False
    else:
        return rs[0][0]     # return Username Record ID
    cursor.close()

def PVDB_ErrorCount( vFieldName, vAction):

    cursor = conn.cursor()

    if vAction == "ADD":
         vSQL = "SELECT " + vFieldName + " FROM ErrorCount"
         cursor.execute(vSQL)
         rs = cursor.fetchall()
         vCount = res[0][0]
         vCount = vCount + 1
         vSQL = "UPDATE ErrorCount SET " + vFieldName + " = " + str(vCount)
         cursor.execute(vSQL)
         conn.commit()
         return vCount

    elif vAction == "RETURN":

         vSQL = "SELECT " + vFieldName + " FROM ErrorCount"
         cursor.execute(vSQL)
         rs = cursor.fetchall()
         vCount = res[0][0]
         return vCount

    elif vAction == "CLEAR":

         vSQL = "UPDATE ErrorCount SET " + vFieldName + " = 0"
         cursor.execute(vSQL)
         conn.commit()
         return 0

    cursor.close()

def PVDB_ErrorCountDetails( vWhat, vDetails):

    cursor = conn.cursor()
    vSQL = "INSERT INTO ErrorCountDetails ( what, details ) VALUES ('" + str(vWhat) + "', '" + str(vDetails) + "')"
    cursor.execute(vSQL)
    conn.commit()
    return True

 