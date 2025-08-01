#!/bin/bash

SCRIPT_PATH=$(dirname "$(readlink -f "$0")")
OBSIDIAN_PATH="../../.."

DIRS=("RELACIONES" "LUGARES, ASOCIACIONES Y EMPRESAS" "SERESCO" "RECURSOS COMUNES" "OBSIDIAN" "OBSIDIAN/scripts" "")
REMOTES=("metadata_menu_0.8.7" "metadata_menu_0.8.7" "metadata_menu_0.8.7" "main" "un-jose-furioso" "un-jose-furioso" "dev_2025-04-20")

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
    mensaje_commit="${1:-Actualización ${fecha}}"
    echo "Actualizando $dir (rama $REMOTE) - $fecha"
    cd "$dir" || exit 1
    git add .; git commit -m "$mensaje_commit"; git push origin "$REMOTE"
    git pull; git push;    

    cd "$SCRIPT_PATH" || exit 1

done;
