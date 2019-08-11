# Change Log

## 0.8.1

Released on August 11, 2019.

### Added

* Support even newer versions of cwltool (<=1.0.20190228155703)
* Support for Python 3.7

### Changed

* Ignore packed workflows when sorting for loading order

### Removed

* Support for Python 2
* Support for Python 3.4

## 0.8.0

### Added

* Add `MultipleInputFeatureRequirement` when a step gets a list of inputs (#105; see also #101)
* Convert input and output names with dashes (-) to underscores (\_), so they are valid Python names
* Allow printing of workflows (#86)
* Logging (for debugging)
* Support newer versions of cwltool (#108)

### Changed

* Using booleans to indicate how a workflow is saved is deprecated. Instead, a mode string should be used (e.g., `wf.save('wf.cwl', mode='rel')`) (#87)
* Inline saving of workflows is deprecated. When saving a workflow with `mode='inline'`, the workflow is saved as a packed workflow (#92)
* Make `scatter_method` optional when scattering over a single parameter (#103)

## 0.7.2

### Added

* Allow for list of step outputs/wf inputs as step input (#101)
* CFF files with citation metadata
* Link between a step's python name (i.e. how it is called on the WorkflowGenerator object) to step names (#100)
* Allow setting workflow labels
* Allow setting a label for a workflow input
* support for CommandInputEnumSchema as workflow input (#99)
* User manual in documentation

### Changed

* Ensure workflows without a requirements section are loaded into the steps library
* Raise real warning when duplicate cwl step (i.e. having the same file name as another step) is loaded

### Removed

* Method to convert a string to cwl file name

## 0.7.1

### Added

* Load tools before workflows when a working directory is used (#94)
* Make sure no duplicate workflow input names are used (#96)

### Changed

* Inputs with a default value are also recognized as optional

## 0.7.0

### Added

* Save packed workflows
* Save workflows using a working directory (a solution to the problem of dealing with paths to steps if steps are loaded from different local directories)

### Changed

* Prevent name clashes of embedded (sub)workflows (however, this doesn't work when a (sub)workflow is added multiple times)
* Use name of step in workflow to create unique ids when saving steps inline (#82)
* Allow saving workflows with inline steps for step files without shebang (#83)
* Document feature for adding documentation to a workflow (#81)
* Fix saving of relative paths for workflows with steps from urls
* By default, workflows are saved with absolute paths

## 0.6.0

### Added

* Make `WorkflowGenerator` into a context manager (#24)
* Type checking of input and output types (#22)
* Allow saving workflow with inline steps (#38)
* Allow saving workflow with relative paths (#25)
* Documentation on Read the Docs (#35)
* Allow loading of multiple CWL steps (from file, http url, and directory) at the same time

### Changed

* Rename `wf.add_inputs()` to `wf.add_input()` (#11)

### Removed

* Python 3.3 support (Sphinx needs Python 3.4)

## 0.5.1

### Added

* Allow addition of default values to workflow inputs (#32)
* List of steps and workflows in steps library is ordered alphabetically

## 0.5.0

### Added

* Python 3 compatibility (and testing with [tox](https://tox.readthedocs.io/en/latest/))

## 0.4.0

### Added

* Generate unique names for steps that are added to the workflow more than once (#31)
* Pass all outputs from a step, instead of just one (#27)
* Improve listing of workflow steps

## 0.3.1

### Added

* Load ExpressionTools as steps

### Changed

* Preserve the order in which steps were added to the workflow

## 0.3.0

### Changed

* Replace pyyaml by ruamel (fixes compatibility with cwltool)

## 0.2.0

### Added

* Documentation for WorkflowGenerator and Step (#15).
* Allow step to be scattered (#17)
* Tests (#9)
* Shebang to saved CWL file (#14)
* Preprocess shortcuts in CWL steps (#12)
* Allow workflows to be used as steps (subworkflows) (#4)
* Take into account optional arguments (#6)

### Removed

* Step.get_input() because it was not used (#21)

## 0.1.0

### Added

* WorkflowGenerator object that allows users to create CWL workflows. The WorkflowGenerator has functionality to
  * load CWL steps from a directory,
  * list available CWL steps
  * connect the inputs and outputs of CWL steps,
  * determine the types of a step's inputs
  * specify a workflow's inputs and outputs, and
  * add workflow documentation.
