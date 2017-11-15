#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: Workflow

requirements:
- class: ScatterFeatureRequirement

inputs:
  wfmessages: string[]

outputs:
  out_files:
    outputSource: echo/echoed
    type:
      items: File
      type: array

steps:
  echo:
    run: tools/echo.cwl
    in:
      message: wfmessages
    out:
    - echoed
    scatter: [message]
    scatterMethod: nested_crossproduct
