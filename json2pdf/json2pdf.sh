#!/bin/bash

python3 py/tratar-json.py  > logs.adoc
asciidoctor-pdf logs.adoc
open ./logs.pdf
