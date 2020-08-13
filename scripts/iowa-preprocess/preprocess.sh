# Ex call: bash preprocess.sh andrew-scribner/iowa/raw/2020-08-12_18:15:52.csv andrew-scribner/iowa/processed/
# $1 is bucket/key to raw data file from minio
# $2 is bucket/key to where train/test/validation csv's will be placed in minio 
#   (it will be bucket/key{train/filename}, so end with a / if you want the destination to 
#   be a directory)

# Using large testr test and validation size because the sample problem is too easy
# and we don't want 100% accuracy all the time
VALIDATION_SIZE="0.4"
TEST_SIZE="0.4"

source /vault/secrets/minio-minimal-tenant1 
mc config host add minio-minimal $MINIO_URL $MINIO_ACCESS_KEY $MINIO_SECRET_KEY

mc cp minio-minimal/$1 ./raw_data

prefix=$(date +"%F_%T")
ipython kernel install --user
papermill preprocess.ipynb preprocess_complete.ipynb \
    -p filename_raw raw_data \
    -p filename_processed $prefix \
    -p validation_size $VALIDATION_SIZE \
    -p test_size $TEST_SIZE

echo "Writing files to minio"
destination=minio-minimal/${2}train/${prefix}_train.csv
echo "  $destination"
mc cp ${prefix}_train.csv $destination
destination=minio-minimal/${2}test/${prefix}_test.csv
echo "  $destination"
mc cp ${prefix}_test.csv minio-minimal/${2}test/
destination=minio-minimal/${2}validation/${prefix}_validation.csv
echo "  $destination"
mc cp ${prefix}_validation.csv minio-minimal/${2}validation/
