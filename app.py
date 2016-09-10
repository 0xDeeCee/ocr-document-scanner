from flask import Flask
from flask import g
from flask import Response
from flask import request
from flask import jsonify
from flaskext.mysql import MySQL
from utils import s3_upload
from aadharExtract import aadhar
from voterIdExtract import voter_id
from panCardExtract import pan_card
import cStringIO
import datetime

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'ocr_scanner'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
ALLOWED_DOCTYPE = set(['aadhar', 'pan_card', 'voter_id'])


@app.before_request
def db_connect():
  g.conn = mysql.connect()
  g.cursor = g.conn.cursor()

@app.after_request
def db_disconnect(response):
  g.cursor.close()
  g.conn.close()
  return response

def query_db(query, args=(), one=False):
  g.cursor.execute(query, args)
  rv = [dict((g.cursor.description[idx][0], value)
  for idx, value in enumerate(row)) for row in g.cursor.fetchall()]
  return (rv[0] if rv else None) if one else rv

def email_exists(email_id):
  result = g.cursor.execute("SELECT id FROM users where email= %s",email_id)
  if(result>0):
    return True
  else:
    return False

@app.route("/")
def hello():
  return "hello"

@app.route("/register", methods=['POST'])
def register():
  if(request.data):
    req_json = request.get_json()
    if(email_exists(req_json['email'])):
     resp = jsonify({"message":"Email already exist"})
    else:
      g.cursor.execute("INSERT INTO users (name, email) VALUES (%s,%s)", (req_json['name'], req_json['email']))
      g.conn.commit()
      id = g.cursor.lastrowid
      resp = jsonify({"message":"User Registered Successfully","id":id})
  else:
    resp = jsonify({"message":"No Post data found"})
  return resp

@app.route("/user/<user_id>", methods=['GET'])
def userInfo(user_id):
  result = query_db("SELECT * FROM users where id =%s",user_id)
  return jsonify(result)

def user_exist(user_id):
  result = g.cursor.execute("SELECT id FROM users where id= %s", user_id)
  if (result > 0):
    return True
  else:
    return False

def file_exist(user_id,file_type):
  if(file_type=="aadhar"):
    result = g.cursor.execute("SELECT id FROM users where id=%s AND gender IS NOT NULL AND aadhar_uid IS NOT NULL ", user_id)
  if(file_type=="pan_card"):
    result = g.cursor.execute("SELECT id FROM users where id=%s AND dob IS NOT NULL AND pan_number IS NOT NULL ", user_id)
  if(file_type=="voter_id"):
    result = g.cursor.execute("SELECT id FROM users where id=%s AND voter_id IS NOT NULL", user_id)

  if (result > 0):
    return True
  else:
    return False

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/upload/<user_id>/<doc_type>", methods=['POST'])
def add(user_id,doc_type):
  status = False

  if user_exist(user_id) and doc_type in ALLOWED_DOCTYPE:

    if file_exist(user_id,doc_type):
      return jsonify('Document already uploaded')

    if 'file' not in request.files:
      return jsonify('No file part')

    file = request.files['file']

    if file.filename == '':
      return jsonify('No selected file')

    if file and allowed_file(file.filename):

      file_contents = cStringIO.StringIO(file.read())
      if(doc_type=="aadhar"):
        uid, gender = aadhar(file_contents)
        if uid is not None and gender is not None:
          g.cursor.execute("""UPDATE users SET aadhar_uid=%s,gender=%s WHERE id=%s""", (uid, gender,user_id))
          g.conn.commit()
          status = True

      if(doc_type=="pan_card"):
        dob, pan = pan_card(file_contents)
        if dob is not None and pan is not None:
          dob= datetime.datetime.strptime(dob, "%d/%m/%Y").strftime("%Y-%m-%d")
          g.cursor.execute("""UPDATE users SET dob=%s,pan_number=%s WHERE id=%s""", (dob, pan,user_id))
          g.conn.commit()
          status = True

      if(doc_type=="voter_id"):
        v_id = voter_id(file_contents)
        if v_id is not None:
          g.cursor.execute("""UPDATE users SET voter_id=%s  WHERE id=%s""", (v_id,user_id))
          g.conn.commit()
          status = True

      if(status):
        result = query_db("SELECT access_key,secret_key FROM aws_credentials")
        s3_upload(result[0]['access_key'],result[0]['secret_key'],file,user_id,doc_type)
        return jsonify('Document Uploaded Successfully')

      else:
        return jsonify('Unable to extract information from document. Please upload another high resolution picture.')


  else:
    return jsonify("Incorrect user id or document type")



if __name__ == "__main__":
  app.run()