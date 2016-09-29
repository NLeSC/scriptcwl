import glob
from .step import Step


def load_steps(dir_in):
    step_files = glob.glob('{}/*.cwl'.format(dir_in))
    steps = {}
    for f in step_files:
        s = Step(f)
        steps[s.name] = s
    return steps
