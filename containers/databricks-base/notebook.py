import time

# Initially derived from https://github.com/kaizentm/kubemlops


argument_one = getArgument("argument_one")  # noqa: F821, E501
argument_two = getArgument("argument_two")  # noqa: F821, E501

print("Argument one {}".format(argument_one))
print("Argument two {}".format(argument_two))

time.sleep(20)
dbutils.fs.ls(".")  # noqa: F821
