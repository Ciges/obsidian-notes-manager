#!/bin/bash

# Constantes
OBSIDIAN_VAULT="C:\Users\jmciges\OneDrive - Seresco, S.A\Documentos\Marques-de-Valdecilla"

# variable servidores es el primer paraámetro del script
servidores=("$@")
# Preguntar confirmación al usuario
if [ ${#servidores[@]} -eq 0 ]; then
    echo "No se han proporcionado servidores. Por favor, especifique al menos uno."
    exit 1
fi
printf "Se van a descargar informes de los siguientes servidores:\n"
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

# Subimos el script paquetes_a_instalar.sh a los servidores en /root/
for s in "${servidores[@]}"; do
    echo "Subiendo script a $s"
    scp paquetes_a_instalar.sh root@${s}ges:/root/
done

# Ejecutamos el script en cada servidor
for s in "${servidores[@]}"; do
    echo "Ejecutando script en $s"
    ssh root@${s}ges "bash /root/paquetes_a_instalar.sh"
done

for s in "${servidores[@]}"; do
    echo "Descargando informes para $s"
    scp root@${s}ges:/root/${s}_updates_$hoy.txt .
done

# Preguntamos por el número de ticket
echo "Por favor, introduzca el número de ticket:"
read -r ticket

# Movemos los informes a la carpeta ../../../TICKETS/$ticket/
FICHEROS_TICKET=${OBSIDIAN_VAULT}/FICHEROS/TICKETS/${ticket}
if ! [ -d "$FICHEROS_TICKET" ]; then
    mkdir -p "$FICHEROS_TICKET"
fi
for s in "${servidores[@]}"; do
    mv "${s}_updates_$hoy.txt" "$FICHEROS_TICKET/"
done