# Based on https://github.com/StatCan/jupyter-notebooks/blob/master/kfp-basics/average_with_docker_components.ipynb  # noqa: E501
from kfp import dsl
from kfp import compiler


AVERAGE_OP_CONTAINER = "k8scc01covidacr.azurecr.io/kfp-components/average:v1"


def average_op(*numbers):
    """
    Factory for average ContainerOps

    Accepts an arbitrary number of input numbers, returning a ContainerOp that
    passes those numbers to the underlying docker image for averaging

    Returns output collected from ./out.txt from inside the container
    """
    # Input validation
    if len(numbers) < 1:
        raise ValueError("Must specify at least one number to take the average"
                         " of")
        
    return dsl.ContainerOp(
        name="average",  # What will show up on the pipeline viewer
        image=AVERAGE_OP_CONTAINER,  # The image that KFP runs to do the work
        arguments=numbers,  # Passes each number as a separate (string) command
                            # line argument
        # Script inside container writes the result (as a string) to out.txt,
        # which KFP reads for us and brings back here as a string
        file_outputs={'data': './out.txt'},  
    )


@dsl.pipeline(
    name="my pipeline's name"
)
def my_pipeline(a, b, c, d, e):
    """
    Averaging pipeline which accepts five numbers and does things
    """
    # Compute averages for two groups
    avg_1 = average_op(a, b, c)
    avg_2 = average_op(d, e)
    
    # Use the results from _1 and _2 to compute an overall average
    average_result_overall = average_op(avg_1.output, avg_2.output)


if __name__ == "__main__":
    compiler.Compiler().compile(my_pipeline, __file__ + '.tar.gz')

# Leftovers from porting this.  To delete later
#
#
# pipeline_yaml = 'pipeline.yaml.zip'
# compiler.Compiler().compile(
#     my_pipeline,
#     pipeline_yaml
# )
# print(f"Exported pipeline definition to {pipeline_yaml}")
#
#
# experiment_name = "averaging-pipeline"
# client = kfp.Client()
# exp = client.create_experiment(name=experiment_name)
# pl_params = {
#     'a': 5,
#     'b': 5,
#     'c': 8,
#     'd': 10,
#     'e': 18,
# }
#
# run = client.run_pipeline(
#     exp.id,  # Run inside the above experiment
# Give our job a name with a timestamp so its unique
#     experiment_name + '-' + time.strftime("%Y%m%d-%H%M%S"),
# Pass the .yaml.zip we created above.  This defines the pipeline
#     pipeline_yaml,
# Pass our parameters we want to run the pipeline with
#     params=pl_params
# )
