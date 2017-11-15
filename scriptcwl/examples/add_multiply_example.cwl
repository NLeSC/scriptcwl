#!/usr/bin/env cwltool
cwlVersion: v1.0
class: Workflow
inputs:
  num1: int
  num2: int
outputs:
  final_answer:
    type: int
    outputSource: multiply/answer
steps:
  add:
    run: /home/jvdzwaan/code/scriptcwl/scriptcwl/examples/add.cwl
    in:
      y: num2
      x: num1
    out:
    - answer
  multiply:
    run: /home/jvdzwaan/code/scriptcwl/scriptcwl/examples/multiply.cwl
    in:
      y: num2
      x: add/answer
    out:
    - answer
