#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
requirements:
- class: SubworkflowFeatureRequirement
inputs:
  wfmessage: string
outputs:
  wfcount:
    type: File
    outputSource: echo-wc/wfcount
steps:
  echo-wc:
    run: ../workflows/echo-wc.cwl
    in:
      wfmessage: wfmessage
    out:
    - wfcount
