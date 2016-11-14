import glob
from .step import Step


def load_steps(steps_dir=None, step_file=None):
    if steps_dir is not None:
        step_files = glob.glob('{}/*.cwl'.format(steps_dir))
    elif step_file is not None:
        step_files = [step_file]
    else:
        step_files = []

    steps = {}
    for f in step_files:
        s = Step(f)
        steps[s.name] = s
    return steps
