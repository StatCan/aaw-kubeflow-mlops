TEMP_FILE=$(mktemp -p ./)
python get-data.py $TEMP_FILE

source /vault/secrets/minio-minimal-tenant1 
mc config host add minio-minimal $MINIO_URL $MINIO_ACCESS_KEY $MINIO_SECRET_KEY

datetime=$(date +"%F_%T")
mc cp $TEMP_FILE minio-minimal/andrew-scribner/iowa/raw/${datetime}.csv