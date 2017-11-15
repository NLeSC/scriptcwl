#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: echo
doc: |
  dit is de documentatie
  die meerdere regels heeft
inputs:
  message:
    type: string
    inputBinding:
      position: 1
outputs:
  echoed:
    type: stdout
