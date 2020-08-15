# Example training call
papermill train.ipynb complete.ipynb -p data data_train.csv -p output_model model.joblib -p svm_gamma 0.1 -p svm_C 100