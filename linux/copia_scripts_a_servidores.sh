#!/bin/bash
# Script para copiar scripts a servidores remotos
# Parámetros: -s|--scripts-dir <ruta> <servidor1> [servidor2] [servidor3] ...

# Constantes
OBSIDIAN_VAULT="C:\Users\jmciges\OneDrive - Seresco, S.A\Documentos\Marques-de-Valdecilla"
SCRIPTS_DIR="$OBSIDIAN_VAULT\WIKI DE SISTEMAS CTO DE CIGES\OBSIDIAN\files\scripts"

# Variables
subdirectorio_scripts=""
servidores=()

# Función para mostrar ayuda
mostrar_ayuda() {
    echo "Uso: $0 -s|--scripts-dir <subdirectorio> <servidor1> [servidor2] [servidor3] ..."
    echo "Ejemplo: $0 -s centos_79 servidor1 servidor2"
    echo "Ejemplo: $0 --scripts-dir linux servidor1 servidor2"
    echo ""
    echo "El subdirectorio se buscará en: $SCRIPTS_DIR"
}

# Parsing de parámetros
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--scripts-dir)
            subdirectorio_scripts="$2"
            shift 2
            ;;
        -h|--help)
            mostrar_ayuda
            exit 0
            ;;
        *)
            servidores+=("$1")
            shift
            ;;
    esac
done

# Verificar que se ha especificado el subdirectorio de scripts
if [ -z "$subdirectorio_scripts" ]; then
    echo "Error: Debe especificar el subdirectorio de scripts con -s o --scripts-dir"
    mostrar_ayuda
    exit 1
fi

# Construir la ruta completa
ruta_scripts="${SCRIPTS_DIR}\\${subdirectorio_scripts}"

# Verificar que se han especificado servidores
if [ ${#servidores[@]} -eq 0 ]; then
    echo "Error: Debe especificar al menos un servidor."
    mostrar_ayuda
    exit 1
fi

# Verificar que la ruta de scripts existe
if [ ! -d "$ruta_scripts" ]; then
    echo "Error: La ruta '$ruta_scripts' no existe."
    echo "Subdirectorio especificado: '$subdirectorio_scripts'"
    echo "Ruta base: '$SCRIPTS_DIR'"
    exit 1
fi

# Verificar que hay archivos en la ruta especificada
archivos_encontrados=$(find "$ruta_scripts" -maxdepth 1 -type f | wc -l)
if [ "$archivos_encontrados" -eq 0 ]; then
    echo "Error: No se encontraron archivos en '$ruta_scripts'."
    exit 1
fi

# Mostrar los archivos que se van a copiar
echo "Archivos encontrados en '$ruta_scripts':"
find "$ruta_scripts" -maxdepth 1 -type f -exec basename {} \; | sort

printf "\nSe van a copiar todos los archivos desde '$ruta_scripts' (subdirectorio: '$subdirectorio_scripts') a los servidores:\n"
for s in "${servidores[@]}"; do
    printf " - %s\n" "$s"
done
echo "¿Desea continuar? (s/n)"
read -r respuesta
if [[ ! "$respuesta" =~ ^[sS]$ ]]; then
    echo "Operación cancelada."
    exit 0
fi  

# Fecha de hoy en formato YYYYMMDD
hoy=$(date +%Y%m%d)

# Ejecutamos el script en cada servidor
for s in "${servidores[@]}"; do
    echo "Copiando archivos a $s..."
    scp "$ruta_scripts"/* root@${s}ges:/root/
    if [ $? -eq 0 ]; then
        echo "✓ Todos los archivos copiados a $s"
    else
        echo "✗ Error al copiar archivos a $s"
    fi
done
