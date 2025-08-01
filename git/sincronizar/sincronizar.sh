#!/bin/bash

SCRIPT_PATH=$(dirname "$(readlink -f "$0")")
OBSIDIAN_PATH="../../../.."

DIRS=("RELACIONES" "LUGARES, ASOCIACIONES Y EMPRESAS" "SERESCO" "RECURSOS COMUNES" "OBSIDIAN" "OBSIDIAN/scripts" "")
REMOTES=("metadata_menu_0.8.7" "metadata_menu_0.8.7" "metadata_menu_0.8.7" "main" "un-jose-furioso" "master" "dev_2025-04-20")

# Ponemos el contenido local idéntico al remoto, eliminando los cambios locales
for i in ${!DIRS[@]}; do
    DIR="${DIRS[$i]}"
    REMOTE="${REMOTES[$i]}"

    dir="$SCRIPT_PATH/$OBSIDIAN_PATH/$DIR"
    if [ ! -d "$dir" ]; then
        echo "El directorio $dir no existe. Saltando..."
        continue
    fi
    echo "Sincronizando $dir con el remoto $REMOTE"
    cd "$dir" || exit 1
    git checkout "$REMOTE"
    git clean -fdx
    git fetch
    git reset --hard "origin/$REMOTE"
    git pull

    cd "$SCRIPT_PATH" || exit 1

done;
