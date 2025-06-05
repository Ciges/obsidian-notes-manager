#!/bin/bash

SCRIPT_PATH=$(dirname "$(readlink -f "$0")")
#OBSIDIAN_PATH="../.."
OBSIDIAN_PATH="Marques-de-Valdecilla"

DIRS=("WIKI DE SISTEMAS CTO DE CIGES" "SERESCO" "RECURSOS COMUNES" "OBSIDIAN" "OBSIDIAN/scripts" "")
REMOTES=("master" "metadata_menu_0.8.7" "main" "abril_2025" "show_note" "master")

# Ponemos el contenido local idéntico al remoto, eliminando los cambios locales
for i in ${!DIRS[@]}; do
    DIR="${DIRS[$i]}"
    REMOTE="${REMOTES[$i]}"

    dir="$SCRIPT_PATH/$OBSIDIAN_PATH/$DIR"
    if [ ! -d "$dir" ]; then
        echo "El directorio $dir no existe. Saltando..."
        continue
    fi
    fecha="$(LANG=es date)"
    echo "Actualizando $dir (rama $REMOTE) - $fecha"
    cd "$dir" || exit 1
    git add *; git commit -m "Actualización ${fecha}"; git push origin "$REMOTE"
    #git pull; git push;    

    cd "$SCRIPT_PATH" || exit 1

done;
