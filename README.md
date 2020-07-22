# Kubeflow MLOps

The repository contains a sample created from the Kubeflow End-to-End Pipeline Example on Azure. It builds a Kubeflow pipeline(KFP) with GitHub actions that trains a Tensorflow convolutional neural network model. The model is registered in Azure AML, Kubeflow, and MLFlow with a defined promotion process. The structure of this sample should make it easier to “bring your own code” and adopt the template for a real-life machine learning project.

## Registration

* [Azure Machine Learning](containers/register-aml)
* [Kubeflow Artifacts](containers/register-kubeflow-artifacts)
* [MLFlow](containers/register-mlflow)

## Scoring

* [Seldon](containers/seldon-score)
* [KFServing](containers/kfservin-score)

## TensorFlow

* [Preprocess](containers/tensorflow-preprocess)
* [Training](containers/tensorflow-training)

## Acknowledgements

Extended from the amazing work done by the Kaizen Team over at [KaizenTM](https://github.com/kaizentm/kubemlops)
