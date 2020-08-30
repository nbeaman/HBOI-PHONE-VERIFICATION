from datetime import datetime
import sys

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
    sys.exit('Execution of code stopped by TELLMOM')
