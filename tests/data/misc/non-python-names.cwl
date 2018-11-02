#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  first-message:
    type: string
    inputBinding:
      position: 1
  optional-message:
      type: string?
      inputBinding:
        position: 2

outputs:
  echo-out:
    type: stdout
