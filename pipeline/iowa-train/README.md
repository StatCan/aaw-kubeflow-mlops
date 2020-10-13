# Iowa Alcohol Sales Demo Pipeline

This demonstration pipeline leverages GitHub actions CI/CD to train and serve an ML workflow in a way that preserves data lineage and allows for complete reproducibility.  

Features of this pipeline include:
* Hyperparameters set by a versioned input file (easy adjustment/tracking of hyperparameters through a PR)
* Pulling training/scoring data from MinIO data storage
* Training and scoring a model, storing the output model and metrics in MinIO
* Reporting important information (run link in Kubeflow, scoring metrics) to the GitHub PR thread that initiated the run
* Storing and versioning all input/output data, output models, and the pipelines and components that generate them

In particular, ensuring reproducibility is done by:
* Storing all data/model metadata in the Kubeflow Metadata store
    * Input data (e.g. training data) is versioned by URI **and md5sum**, ensuring when looking back later we can be confident that data is the same as was used during training/scoring. 
    * Inputs (training/scoring data), executions (training run, scoring run, ...), and outputs (models, results) are linked in Kubeflow Metadata to be easily browsed in the Kubeflow Artifact Lineage Explorer
* Any components built specifically for this pipeline (e.g. the `train.py` component) are pushed as docker images to the container repository **tagged with the commit SHA**.  The pipelines built here then use these versioned components, ensuring we can later trace from the `pipeline.yaml` the exact code used during the run (rather than just `someContainer:latest`)
