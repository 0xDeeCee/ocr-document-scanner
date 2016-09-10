from PIL import Image
import pytesseract
import re

def voter_id(file):
    text = pytesseract.image_to_string(Image.open(file))
    voter_id = None
    for line in text.split('\n'):
        words = line.split()
        for word in words:
            if(re.search('[A-Za-z]{3}\d{7}',word)):
                voter_id = word
                break

    return voter_id