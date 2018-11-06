#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
inputs:
  msg1:
    type: string
    inputBinding:
      position: 1
  msg2:
    type: string
    inputBinding:
      position: 2
outputs:
  echoed:
    type: stdout
