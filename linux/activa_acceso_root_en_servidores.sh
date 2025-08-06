#!/bin/bash
# variable servidores es el primer paraámetro del script
servidores=("$@")
# Preguntar confirmación al usuario
if [ ${#servidores[@]} -eq 0 ]; then
    echo "No se han proporcionado servidores. Por favor, especifique al menos uno."
    exit 1
fi
printf "Se va a activar el acceso a root con clave pública en los siguientes servidores:\n"
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
    ssh root@${s}ges "bash /root/activa_acceso_root.sh"
    if [ $? -eq 0 ]; then
        echo "✓ Script ejecutado en $s"
    else
        echo "✗ Error en $s"
    fi
done
