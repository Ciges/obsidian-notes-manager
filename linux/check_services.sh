#!/bin/bash

# Script para obtener la lista de servicios en ejecución en un servidor remoto Linux
# Uso: ./check_services.sh <nombre_servidor>

# Verificar que se proporcione el parámetro del servidor
if [ $# -eq 0 ]; then
    echo "Error: Debe proporcionar el nombre del servidor como parámetro"
    echo "Uso: $0 <nombre_servidor>"
    exit 1
fi

# Obtener el nombre del servidor del primer parámetro
SERVIDOR=${1}ges

# Ejecutar el comando SSH como root
SO="$(ssh root@$SERVIDOR "cat /etc/centos-release")"

# Verificar el estado de salida del comando SSH
if [ $? -ne 0 ]; then
    echo "Error: No se pudo ejecutar el comando en $SERVIDOR"
    exit 1
fi

# Limpiar espacios en blanco al principio y final
SO=$(echo "$SO" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

# Si el resultado del comando anterior es "CentOS Linux release 7.9.2009 (Core)" entonces lanzar el comando de veriificación de servicios "systemctl list-units --type=service --state=running"
so_conocido=false
echo "Sistema operativo detectado en $SERVIDOR: ${SO}"
case "$SO" in
    "CentOS Linux release 7.9.2009 (Core)"|"CentOS Linux release 7.2.1511 (Core)")
        comando_verificacion="systemctl list-units --type=service --state=running"
        so_conocido=true
        ;;
    *)
        echo "Error: Sistema operativo no reconocido en $SERVIDOR: ${SO}"
        exit 1
        ;;
esac
if [ "$so_conocido" = true ]; then
    echo "Lista de servicios:"
    echo "\$ ${comando_verificacion}"
    ssh root@$SERVIDOR "$comando_verificacion"
fi