import boto
from boto.s3.key import Key

Bucketname = 'bucketdocuments'

def s3_upload(access_key,secret_key,data_file,user_id,doc_type):

    conn = boto.connect_s3(access_key, secret_key,host='s3.ap-south-1.amazonaws.com')
    bucket = conn.get_bucket(Bucketname)
    k = Key(bucket)
    file_contents = data_file.read()

    # Use Boto to upload the file to the S3 bucket
    k.key = doc_type+"_"+user_id
    print "Uploading some data to " + Bucketname + " with key: " + k.key
    k.set_contents_from_string(file_contents)