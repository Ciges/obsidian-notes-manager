#!/bin/bash

# Parse command line arguments
ONLY_COMMIT=false
COMMIT_MESSAGE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--only-commit)
            ONLY_COMMIT=true
            shift
            ;;
        -m|--commit-message)
            COMMIT_MESSAGE="$2"
            shift 2
            ;;
        *)
            echo "Opción desconocida: $1"
            echo "Uso: $0 [-c|--only-commit] [-m|--commit-message \"mensaje\"]"
            exit 1
            ;;
    esac
done

SCRIPT_PATH=$(dirname "$(readlink -f "$0")")
OBSIDIAN_PATH="../../.."

DIRS=("WIKI DE SISTEMAS CTO DE CIGES/OBSIDIAN" "WIKI DE SISTEMAS CTO DE CIGES" "SERESCO" "RECURSOS COMUNES" "OBSIDIAN/scripts" "OBSIDIAN"  "")
REMOTES=("wiki-de-sistemas-cto-de-ciges" "dev" "metadata_menu_0.8.7" "main" "marques-de-valdecilla" "marques-de-valdecilla" "master" "master")

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
    mensaje_commit="${COMMIT_MESSAGE:-Actualización ${fecha}}"
    
    if [ "$ONLY_COMMIT" = true ]; then
        echo "Solo commit en $dir (rama $REMOTE) - $fecha"
        cd "$dir" || exit 1
        git add .; git commit -m "$mensaje_commit"
    else
        echo "Actualizando $dir (rama $REMOTE) - $fecha"
        cd "$dir" || exit 1
        git add .; git commit -m "$mensaje_commit"; 
        git push origin "$REMOTE"
        git pull; git push;
    fi    

    cd "$SCRIPT_PATH" || exit 1

done;
