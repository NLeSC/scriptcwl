def __init__(self, wf_file=None, abspath=True, start=os.curdir,
             steps_dir=None):

if wf_file is not None:
    self.load_wf(wf_file, abspath, start)



def load_wf(self, fname, abspath, start):
    dirname = os.path.dirname(fname)
    steps = {}
    with open(fname) as f:
        w = yaml.load(f)
        self.wf_inputs = w['inputs']
        self.wf_outputs = w['outputs']
        for name, step in w['steps'].iteritems():
            path = os.path.join(dirname, step['run'])
            sf = os.path.normpath(path)
            if not abspath:
                sf = os.path.relpath(sf, start)
            s = Step(sf, abspath, start)
            steps[s.name] = s
            step['run'] = sf
            self.wf_steps[name] = step
