#!/bin/bash

# Script para desactivar el acceso root usando claves públicas SSH
# Al intervenir en los servidores Linux dejo esta opción abierta, y una vez que el cambio está realizado ejecuto este script
# Uso: ./desactiva_acceso_root_clave_ssh.sh <nombre_servidor>

# Verificar que se proporcione el parámetro del servidor
if [ $# -eq 0 ]; then
    echo "Error: Debe proporcionar el nombre del servidor como parámetro"
    echo "Uso: $0 <nombre_servidor>"
    exit 1
fi

# Obtener el nombre del servidor del primer parámetro
SERVIDOR=${1}ges

# En el servidor remoto debería existir el script /root/desactiva_acceso_root.sh
ssh root@${SERVIDOR} "bash /root/desactiva_acceso_root.sh && rm -f /root/desactiva_acceso_root.sh /root/activa_acceso_root.sh /root/paquetes_a_instalar.sh"
if [ $? -eq 0 ]; then
    echo "✓ Acceso root desactivado y scripts eliminados en ${1}"
else
    echo "✗ Error en ${1}"
fi