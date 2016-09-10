from PIL import Image
import pytesseract
import re

def aadhar(file):
    text = pytesseract.image_to_string(Image.open(file))
    gender = None
    uid = None

#get gender
    for line in text.split('\n'):
        words = line.split()
        for word in words:
                if(re.search('(Female|Male|emale|male|ale|FEMALE|MALE|EMALE)$',word)):
                  gender = word
                  break

#get aadhar number
    for line in text.split('\n'):
        if (re.search('\d{4}\s\d{4}\s\d{4}', line)):
            uid = line
            uid = uid.replace(" ", "")
            break

    return (uid,gender)
