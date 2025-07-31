#!/bin/bash
OBSIDIAN_VAULT="c:\Users\jmciges\Notas\Marques-de-Valdecilla"
SOURCE_DIR="$OBSIDIAN_VAULT"
DESTINATION_DIR="C:\Users\jmciges\OneDrive - Seresco, S.A\Documentos\Marques-de-Valdecilla"

python "$OBSIDIAN_VAULT\OBSIDIAN\scripts\rsync.py" -s "$SOURCE_DIR" -d "$DESTINATION_DIR" -v