Installation:

1. Install Python and Pip

2. Install tesseract-ocr:
   sudo apt-get install tesseract-ocr

3. pip install -r requirements.txt

4 Import database and make necessary database configuration changes in app.py

5. Run service:
   ./app.py

APIs
1. Registration API:
   POST API URL: /register

   Curl Request:
   curl -X POST -H "Content-Type: application/json" -H "Cache-Control: no-cache" -d '{
    "name":"test",
    "email":"test@gmail.com"
    }' "http://127.0.0.1:5000/register"


2. User Information API:
    GET API URL: /user/:user_id

    Curl Request:
    curl -X GET -H "Cache-Control: no-cache" "http://127.0.0.1:5000/user/1"

3. Upload Document API:
    POST API URL: /upload/:user_id/:document_type     (Note: document_type value can only be aadhar, pan_card and voter_id)

    Curl Request:
    curl -X POST -H "Cache-Control: no-cache" -H "Content-Type: multipart/form-data" -F "file=@" "http://127.0.0.1:5000/upload/1/pan_card"