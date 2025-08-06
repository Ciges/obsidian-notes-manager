#!/bin/bash

SCRIPT_PATH=$(dirname "$(readlink -f "$0")")
OBSIDIAN_PATH="../.."

LOG_FILE="$SCRIPT_PATH/$OBSIDIAN_PATH/OBSIDIAN/logs/actualizar_listados_en_wiki.log"
fecha=$(date '+%Y-%m-%d %H:%M:%S')
echo "$fecha - Inicio del script" >> "$LOG_FILE"

# La carpeta con los ficheros de listado está en dos sitios:
# - En OBSIDIAN/listados
# - En WIKI DE SISTEMAS CTO DE CIGES/OBSIDIAN/listados

# Haz un comando de copia que copie los ficheros de la primera a la segunda sólo si son mas nuevos
# No dispongo del comando rsync
for l in comunes humv; do
    origen="$SCRIPT_PATH/$OBSIDIAN_PATH/OBSIDIAN/listados/$l"
    destino="$SCRIPT_PATH/$OBSIDIAN_PATH/WIKI DE SISTEMAS CTO DE CIGES/OBSIDIAN/listados/$l"
    # Con el c
    cp -uav "$origen/"* "$destino" | tee -a "$LOG_FILE"
done;
# Actualizamos también algunos archivos CSS relacionados
cp -uav "$SCRIPT_PATH/$OBSIDIAN_PATH/.obsidian/snippets/tags.css" "$SCRIPT_PATH/$OBSIDIAN_PATH/WIKI DE SISTEMAS CTO DE CIGES/.obsidian/snippets/" | tee -a "$LOG_FILE"


echo "$fecha - Fin del script" >> "$LOG_FILE"