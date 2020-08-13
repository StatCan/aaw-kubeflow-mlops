# Convenience function to get testing data

source /vault/secrets/minio-minimal-tenant1
mc config host add minio-minimal $MINIO_URL $MINIO_ACCESS_KEY $MINIO_SECRET_KEY

mc cp minio-minimal/andrew-scribner/iowa/processed/train/2020-08-13_18:02:01_train.csv ./data_train.csv
mc cp minio-minimal/andrew-scribner/iowa/processed/test/2020-08-13_18:02:01_test.csv ./data_test.csv