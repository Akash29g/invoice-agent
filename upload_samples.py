import os, glob, boto3
s3 = boto3.client("s3", region_name="us-east-1")
B = os.environ["BUCKET"]
for f in glob.glob("samples/*.png"):
    s3.upload_file(f, B, "invoices/" + os.path.basename(f))
    print("uploaded", f)
s3.copy_object(Bucket=B, Key="invoices/clean_copy.jpg",
               CopySource={"Bucket": B, "Key": "invoices/clean.jpg"})
print("copied clean_copy.jpg")
