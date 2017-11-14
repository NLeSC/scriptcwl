from six import text_type


class Reference:
    """Represents a reference to a source of data.

    A Reference can refer to an input, or to the output of a step.

    Either `input_name` must be given, or both `step_name` and
    `output_name` must be given.

    Args:
        input_name (str): The name of a workflow input.
        step_name (str): The name of a step whose output to refer to.
        output_name (str): The name of the output to refer to.
    """
    def __init__(self, input_name=None, step_name=None, output_name=None):
        self.input_name = input_name
        self.step_name = step_name
        self.output_name = output_name
        if input_name:
            self.target_str = input_name
        elif step_name and output_name:
            self.target_str = ''.join([step_name, '/', output_name])
        else:
            raise RuntimeError('Invalid input when constructing Reference')

    def __repr__(self):
        return self.target_str

    def refers_to_wf_input(self):
        return self.input_name is not None

    def refers_to_step_output(self):
        return self.step_name is not None


def reference_presenter(dmpr, data):
    return dmpr.represent_scalar('tag:yaml.org,2002:str', text_type(data))
