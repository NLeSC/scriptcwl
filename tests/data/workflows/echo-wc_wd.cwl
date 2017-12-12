#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: Workflow
inputs:
  wfmessage: string
outputs:
  wfcount:
    type: File
    outputSource: wc/wced
steps:
  echo:
    run: echo.cwl
    in:
      message: wfmessage
    out:
    - echoed
  wc:
    run: wc.cwl
    in:
      file2count: echo/echoed
    out:
    - wced
