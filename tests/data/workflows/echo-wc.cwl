#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
doc: Counts words of a message via echo and wc
inputs:
  wfmessage: string
outputs:
  wfcount:
    type: File
    outputSource: wc/wced
steps:
  echo:
    run: ../tools/echo.cwl
    in:
      message: wfmessage
    out:
    - echoed
  wc:
    run: ../tools/wc.cwl
    in:
      file2count: echo/echoed
    out:
    - wced
