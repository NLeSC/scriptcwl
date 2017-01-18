#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: wc
inputs:
  file2count:
    type: File
    inputBinding:
      position: 1
outputs:
   wced:
     type: stdout
