#!/bin/bash

# Extraemos la información en formato JSON y mediante Python la transformamos a Asciidoc.
python3 py/tratar-json.py  > logs.adoc
# Exportamos el fichero adoc a PDF.
asciidoctor-pdf logs.adoc
# Abre el PDF generado.
open ./logs.pdf
