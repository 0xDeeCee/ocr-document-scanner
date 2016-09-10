from PIL import Image
import pytesseract
import re

def pan_card(file):
    text = pytesseract.image_to_string(Image.open(file))
    dob = None
    pan_number = None
    for line in text.split('\n'):
        line = line.replace(" ", "")

        if (re.search('(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[012])[\/\-]\d{4}', line)):
            dob = line

        if (re.search('[A-Za-z]{5}\d{4}[A-Za-z]{1}', line)):
            pan_number = line
            break

    return(dob,pan_number)
