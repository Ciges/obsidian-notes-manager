#!/bin/bash

SCRIPT_PATH=$(dirname "$(readlink -f "$0")")
OBSIDIAN_PATH="../../../.."

DIRS=("SERESCO" "RECURSOS COMUNES" "OBSIDIAN" "OBSIDIAN/scripts" "WIKI DE SISTEMAS CTO DE CIGES" "WIKI DE SISTEMAS CTO DE CIGES/OBSIDIAN")
REMOTES=("metadata_menu_0.8.7" "main" "marques-de-valdecilla" "marques-de-valdecilla" "dev" "wiki-de-sistemas-cto-de-ciges")

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
