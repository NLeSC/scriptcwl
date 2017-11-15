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
    run:
      cwlVersion: v1.0
      class: CommandLineTool
      baseCommand: echo
      inputs:
      - type: string
        inputBinding:
          position: 1
        id: _:echo.cwl#message
      outputs:
      - type: File
        id: _:echo.cwl#echoed
        outputBinding:
          glob: 8341e6646e16f373b00fc5a45b4f299d5901b0ad
      id: _:echo.cwl
      stdout: 8341e6646e16f373b00fc5a45b4f299d5901b0ad
    in:
      message: wfmessage
    out:
    - echoed
  wc:
    run:
      cwlVersion: v1.0
      class: CommandLineTool
      baseCommand: wc
      inputs:
      - type: File
        inputBinding:
          position: 1
        id: _:wc.cwl#file2count
      outputs:
      - type: File
        id: _:wc.cwl#wced
        outputBinding:
          glob: bcd587c62be60d5d0473ee2c39dc73257b20ecca
      id: _:wc.cwl
      stdout: bcd587c62be60d5d0473ee2c39dc73257b20ecca
    in:
      file2count: echo/echoed
    out:
    - wced
