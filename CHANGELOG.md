# Change Log

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
