#!/bin/bash
# Script para enviar comandos a servidores remotos
# Parámetros: -s|--servers <servidor1,servidor2,servidor3> <comando a ejecutar>

# Variables
servidores_str=""
servidores=()
comando=""
skip_confirmation=false
no_verbose=false

# Función para mostrar ayuda
mostrar_ayuda() {
    echo "Uso: $0 -s|--servers <servidor1,servidor2,servidor3> [-y|--yes] [-nv|--no-verbose] <comando>"
    echo "Ejemplo: $0 -s servidor1,servidor2,servidor3 'ls -la /root'"
    echo "Ejemplo: $0 --servers srv01,srv02 -y 'bash /root/activa_acceso_root.sh'"
    echo "Ejemplo: $0 -s srv01,srv02 -nv 'uptime'"
    echo ""
    echo "Opciones:"
    echo "  -s, --servers      Lista de servidores separados por coma"
    echo "  -y, --yes          No pedir confirmación antes de ejecutar"
    echo "  -nv, --no-verbose  Solo mostrar la salida del comando (sin mensajes informativos)"
    echo "  -h, --help         Mostrar esta ayuda"
    echo ""
    echo "Nota: Se añadirá el sufijo 'ges' a cada nombre de servidor para la conexión SSH"
}

# Parsing de parámetros
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--servers)
            servidores_str="$2"
            shift 2
            ;;
        -y|--yes)
            skip_confirmation=true
            shift
            ;;
        -nv|--no-verbose)
            no_verbose=true
            shift
            ;;
        -h|--help)
            mostrar_ayuda
            exit 0
            ;;
        *)
            # Todo lo que queda es el comando a ejecutar
            comando="$*"
            break
            ;;
    esac
done

# Verificar que se han especificado servidores
if [ -z "$servidores_str" ]; then
    echo "Error: Debe especificar los servidores con -s o --servers"
    mostrar_ayuda
    exit 1
fi

# Verificar que se ha especificado un comando
if [ -z "$comando" ]; then
    echo "Error: Debe especificar un comando a ejecutar"
    mostrar_ayuda
    exit 1
fi

# Convertir la cadena de servidores separados por coma en un array
IFS=',' read -ra servidores <<< "$servidores_str"

# Preguntar confirmación al usuario
if [ ${#servidores[@]} -eq 0 ]; then
    echo "Error: No se pudieron procesar los servidores especificados."
    exit 1
fi

# Mostrar información solo si no está en modo no-verbose
if [ "$no_verbose" = false ]; then
    printf "Se va a ejecutar el comando '$comando' en los siguientes servidores:\n"
    for s in "${servidores[@]}"; do
        printf " - %s (conexión: root@${s}ges)\n" "$s"
    done
fi

# Pedir confirmación solo si no se especificó -y y no está en modo no-verbose
if [ "$skip_confirmation" = false ] && [ "$no_verbose" = false ]; then
    echo "¿Desea continuar? (s/n)"
    read -r respuesta
    if [[ ! "$respuesta" =~ ^[sS]$ ]]; then
        echo "Operación cancelada."
        exit 0
    fi
elif [ "$skip_confirmation" = false ] && [ "$no_verbose" = true ]; then
    # En modo no-verbose pero sin -y, asumir que sí quiere continuar
    # ya que no puede mostrar el prompt de confirmación
    :
elif [ "$no_verbose" = false ]; then
    echo "Ejecutando automáticamente (opción -y especificada)..."
fi  

# Fecha de hoy en formato YYYYMMDD
hoy=$(date +%Y%m%d)

# Ejecutamos el comando en cada servidor
for s in "${servidores[@]}"; do
    if [ "$no_verbose" = false ]; then
        echo "Ejecutando en $s..."
    fi
    
    ssh root@${s}ges "$comando"
    exit_code=$?
    
    if [ "$no_verbose" = false ]; then
        if [ $exit_code -eq 0 ]; then
            echo "✓ Comando ejecutado correctamente en $s"
        else
            echo "✗ Error al ejecutar comando en $s"
        fi
        echo "----------------------------------------"
    fi
done
