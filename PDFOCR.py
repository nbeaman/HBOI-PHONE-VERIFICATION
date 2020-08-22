import pdf2image
from PIL import Image
import time
import os
import shutil       # for deleting all files in TEMPFOLDER

DBUG = True

# Image to text conversion
# Second line looks up Tesseract executable saved on computer
import pytesseract as pt
pt.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Declare constants
TEMPFOLDER = r"C:\app\PHONEVER\TEMP"

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
    PDF_PATH = os.path.join(TEMPFOLDER, PDFfileName)

    start_time = time.time()
    pil_images = pdf2image.convert_from_path(PDF_PATH, dpi=DPI, output_folder=TEMPFOLDER, first_page=FIRST_PAGE, last_page=LAST_PAGE, fmt=FORMAT, thread_count=THREAD_COUNT, userpw=USERPWD, use_cropbox=USE_CROPBOX, strict=STRICT)
    if DBUG: print("pdftopil: Time taken to convert PDF to jpg(s): " + str(time.time() - start_time))
    return pil_images


def save_images(pil_images, PDFfileName):
    # This method helps in converting the images in PIL Image file format to the required image format
    # Index used for multipage PDFs. Will save the image files with a number at the end of the file name, based on the PDF page number
    # Image files with be saved as Net ID and a number at the end
    index = 1
    FULLtext = ""

    PDF_PATH = os.path.join(TEMPFOLDER, PDFfileName)

    for image in pil_images:
        image.save(str(PDF_PATH[:-4]) + str(index) + ".jpg")

        # Converts img to text and outputs it
        pdfimg = Image.open(str(PDF_PATH[:-4]) + str(index) + ".jpg")
        text = pt.image_to_string(pdfimg)
        FULLtext = FULLtext + text
        index += 1

    return FULLtext

def PDFOCR_DeleteAllTempFiles(TEMPF):
    print("HERE")
    for filename in os.listdir(TEMPF):
        file_path = os.path.join(TEMPF, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('PDFOCR: Failed to delete %s. Reason: %s' % (file_path, e))

def PDFOCR_BillPeriod(PDFFILENAME):

    pil_images = pdftopil(PDFFILENAME)
    pdfText = save_images(pil_images, PDFFILENAME)
    #NeededInfo = ParsePDFtoGetNeededData(pdfText)

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

    PDFOCR_DeleteAllTempFiles
    return BillPeriod