# Kubeflow MLOps

This repository contains examples of completely integrated Kubeflow End-to-End Pipelines (KFP) using GitHub actions. Focus is on the creation of pluggable components that can make it easier to build your own pipelines enabling more advanced machine learning projects.

The architecture of the sample is shown in the following diagram:

![Kubeflow MLOps Architecture Diagram](./docs/diagrams/kubeflow-mlops.png)

The current pipelines that have been created provide the following pluggable components:

* [Default](pipeline/train/default.py)
* [Convolutional Neural Network (CNN)](pipeline/train/cnn.py)

## KubeFlow

* [List Pipelines](pipeline/list.py)
* [Publish Pipeline](pipeline/publish.py)
* [Run Pipeline](pipeline/run.py)

## Integrations

* [DataBricks](containers/databricks)

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

Extended with code and lessons learnt from the amazing work done by the Kaizen Team over at [KaizenTM](https://github.com/kaizentm/kubemlops)
