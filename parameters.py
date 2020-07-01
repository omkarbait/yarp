import yaml

def read(param_file):
	with open(param_file) as file:
    		# The FullLoader parameter handles the conversion from YAML
    		# scalar values to Python the dictionary format
    		params = yaml.safe_load(file)
	return params

def write(params, outfile='parameter.yaml'):
    with open(outfile, 'w') as file:
        parameters = yaml.safe_dump(params, file)

