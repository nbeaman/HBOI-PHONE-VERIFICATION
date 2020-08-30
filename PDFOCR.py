import pdf2image
from PIL import Image
import time
import os
import shutil       # for deleting all files in PDFOCR_TEMPFOLDER

#=================================[ FOR DEBUGGING ONLY APPLIES TO PVEMAIL CODE ]===================
#  DBUG = False     : No Debugging
#  DBUG = 1 or True : First (or low) level debugging
#  DBUG = 2         : Medium debugging level
#  DBUG = 3         : High - debug everything
DBUG = False

#==================================================================================================

#=================================[ VARIABLES USED ONLY IN THE FUNCTIONS BELOW ]===================

PDFOCR_TEMPFOLDER = r"C:\app\PHONEVER\TEMP"
PDFOCR_TESSERACT_FILE_LOCATION = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Image to text conversion
# Second line looks up Tesseract executable saved on computer
import pytesseract as pt
pt.pytesseract.tesseract_cmd = PDFOCR_TESSERACT_FILE_LOCATION

#==================================================================================================

#=================================[ FUNCTIONS USED IN THIS FILE ONLY ]=============================
def pdftopil(PDFfileName):
    # This method reads a pdf and converts it into a sequence of images
    # PDF_PATH sets the path to the PDF file
    # dpi parameter assists in adjusting the resolution of the image
    # output_folder parameter sets the path to the folder to which the PIL images can be stored (optional)
    # first_page parameter allows you to set a first page to be processed by pdftoppm
    # last_page parameter allows you to set a last page to be processed by pdftoppm
    # fmt parameter allows to set the format of pdftoppm conversion (PpmImageFile, TIFF)
    # thread_count parameter allows you to set how many thread will be used for conversion.
    # userpw parameter allows you to set a password to unlock the converted PDF
    # use_cropbox parameter allows you to use the crop box instead of the media box when converting
    # strict parameter allows you to catch pdftoppm syntax error with a custom type PDFSyntaxError

    DPI = 100
    FORMAT = 'jpg'
    THREAD_COUNT = 1
    USERPWD = None
    USE_CROPBOX = False
    STRICT = False
    FIRST_PAGE = None
    LAST_PAGE = None
    PDF_PATH = os.path.join(PDFOCR_TEMPFOLDER, PDFfileName)

    start_time = time.time()
    pil_images = pdf2image.convert_from_path(PDF_PATH, dpi=DPI, output_folder=PDFOCR_TEMPFOLDER, first_page=FIRST_PAGE, last_page=LAST_PAGE, fmt=FORMAT, thread_count=THREAD_COUNT, userpw=USERPWD, use_cropbox=USE_CROPBOX, strict=STRICT)
    if DBUG: print("pdftopil: Time taken to convert PDF to jpg(s): " + str(time.time() - start_time))
    return pil_images


def save_images(pil_images, PDFfileName):
    # This method helps in converting the images in PIL Image file format to the required image format
    # Index used for multipage PDFs. Will save the image files with a number at the end of the file name, based on the PDF page number
    # Image files with be saved as Net ID and a number at the end
    index = 1
    FULLtext = ""

    PDF_PATH = os.path.join(PDFOCR_TEMPFOLDER, PDFfileName)

    for image in pil_images:
        image.save(str(PDF_PATH[:-4]) + str(index) + ".jpg")

        # Converts img to text and outputs it
        pdfimg = Image.open(str(PDF_PATH[:-4]) + str(index) + ".jpg")
        text = pt.image_to_string(pdfimg)
        FULLtext = FULLtext + text
        index += 1

    return FULLtext

def DeleteAllTempFiles(TEMPF):

    for filename in os.listdir(TEMPF):
        file_path = os.path.join(TEMPF, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('PDFOCR: Failed to delete %s. Reason: %s' % (file_path, e))

def saveAttachmentForOCR(saveDir, filename, payload):
    filepath=os.path.join(saveDir, filename)
    print("FILE: PDFOCR: FILE PATH: " + filepath)
    # download attachment and save it
    open(filepath, "wb").write(payload)

def GetPDF_TEXT(PDFFILENAME):

    pil_images = pdftopil(PDFFILENAME)
    pdfText = save_images(pil_images, PDFFILENAME)
    return pdfText

def Parse_BillPeriod(PDFFILENAME, pdfText):

    # find the location of "Bill Period" in pdfText
    BillPeriodIndex = pdfText.find("Bill Period")
    # set TempTxt to just "Bill Period   Device   Device Type.... to the end of text"
    TempTXT = pdfText[BillPeriodIndex : BillPeriodIndex + (len(pdfText) -BillPeriodIndex)]
    NewTXT = str(TempTXT)
    # find the location of " Device" in TempText
    QMarkIndex = NewTXT.find(" Device")
    # sets BillPeriod to "Bill Period  Jul 2020   "
    BillPeriod = NewTXT[0:QMarkIndex-3]
    # sets BillPeriod to "  Jul 2020   "
    BillPeriod = BillPeriod.replace("Bill Period","")
    # remove CR and LF from BillPeriod, just leaving "Jul 2020"
    BillPeriod = BillPeriod.replace(chr(10),"")
    BillPeriod = BillPeriod.replace(chr(13),"")

    return BillPeriod

def Parse_EmployeeFullName(PDFFILENAME, pdfText):

    # find the location of "Full Name" in pdfText
    FullNameIndex = pdfText.find("Full Name")
    # print(FullNameIndex)
    TempTXT = pdfText[FullNameIndex: FullNameIndex + (len(pdfText) - FullNameIndex)]
    NewTXT = str(TempTXT)
    # find the location of "Department Name" in TempText
    EndTXT = NewTXT.find("Department Name")
    # sets FullName to "Esther Guzman"
    FullName = NewTXT[0:EndTXT]
    # sets FullName to "Esther Guzman", removes "Full Name" text
    FullName = FullName.replace("Full Name", "")
    # remove CR and LF from BillPeriod, just leaving "Esther Guzman"
    FullName = FullName.replace(chr(10), "")
    FullName = FullName.replace(chr(13), "")
    if DBUG: print("OCRtoText_EmployeeName: >>" + str(FullName) + "<<")

    return FullName

#==================================================================================================

#=================================[ FUNCTION USED IN MAIN PROGRAME ]===============================
def PDFOCR_GetBillPeriodAndFullName(PDFFILENAME, PAYLOAD):

    saveAttachmentForOCR(PDFOCR_TEMPFOLDER, PDFFILENAME, PAYLOAD)
    TXT = GetPDF_TEXT(PDFFILENAME)
    vBillPeriod = Parse_BillPeriod(PDFFILENAME, TXT)
    vFullName = Parse_EmployeeFullName(PDFFILENAME, TXT)
    DeleteAllTempFiles(PDFOCR_TEMPFOLDER)

    return vBillPeriod, vFullName

#==================================================================================================