# $1 is bucket/key to file in minio

source /vault/secrets/minio-minimal-tenant1 
mc config host add minio-minimal $MINIO_URL $MINIO_ACCESS_KEY $MINIO_SECRET_KEY

mc cp minio-minimal/$1 ./raw_data

prefix=$(date +"%F_%T")
ipython kernel install --user
papermill preprocess.ipynb preprocess_complete.ipynb -p filename_raw raw_data -p filename_processed $prefix

mc cp ${prefix}_train.csv minio-minimal/andrew-scribner/iowa/processed/train/
mc cp ${prefix}_test.csv minio-minimal/andrew-scribner/iowa/processed/test/
mc cp ${prefix}_validation.csv minio-minimal/andrew-scribner/iowa/processed/validation/
