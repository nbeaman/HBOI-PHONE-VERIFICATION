# importing the module
import pyodbc
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
        print(vSQL)
        cursor.execute(vSQL)
        conn.commit()
        return True

    cursor.close()

def PVDB_UserHasFullNameEntered(vUsername, vFullName):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usernames WHERE Username = '" + vUsername + "';")
    rs = cursor.fetchall()
    FullnameInDB = str(rs[0][2])
    print("DBDBDBDBDB>" + FullnameInDB + "DBDBDBDBDBDBDB")
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
        print(vSQL)
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
        print(vSQL)
        cursor.execute(vSQL)
        conn.commit()
        return True

    cursor.close()

def PVDB_PhoneVerRecordExists(vUsername, vBillPeriod):

    UsernameID = PVDB_UserExists(vUsername)

    cursor = conn.cursor()
    vSQL = "SELECT * FROM PhoneVer WHERE Username_id = " + str(UsernameID) + " AND billperiod = '" + vBillPeriod + "'"
    print(vSQL)
    cursor.execute(vSQL)
    rs = cursor.fetchall()

    if len(rs) == 0:
        return False
    else:
        return rs[0][0]     # return Username Record ID
    cursor.close()
