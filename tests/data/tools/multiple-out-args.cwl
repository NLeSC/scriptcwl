#!/usr/bin/env cwlrunner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: ["python", "-m", "nlppln.commands.extract_annotations"]

inputs:
  in_files:
    type:
      type: array
      items: File
    inputBinding:
      position: 2
  out_dir:
    type: Directory?
    inputBinding:
      prefix: --out_dir=
      separate: false
  counselors:
    type:
      type: array
      items: string
      inputBinding:
        prefix: -c

stdout: missing_introductions.json

outputs:
  out_files:
    type:
      type: array
      items: File
    outputBinding:
      glob: "*.txt"
  meta_out:
    type: File
    outputBinding:
      glob: "missing_introductions.json"
