#!/bin/bash

# Variables de fecha y host
HOST=$(hostname)
FECHA=$(date +"%Y%m%d")
LOGFILE="${HOST}_updates_${FECHA}.txt"
CSVFILE="${HOST}_updates_${FECHA}.csv"

# Obtener información del SO
SO=$(cat /etc/redhat-release 2>/dev/null || echo "Desconocido")
NOW=$(date +"%Y-%m-%d %H:%M:%S")

# Imprimir informe en pantalla y guardar en log
{
  echo "=============================================="
  echo "Host:       $HOST"
  echo "Fecha:      $NOW"
  echo "Versión SO: $SO"
  echo "=============================================="
  echo
  printf "%-35s %-25s %-25s\n" "Paquete" "Versión instalada" "Versión nueva"
} | tee "$LOGFILE"

# Cabecera para CSV
echo "Paquete,Version_instalada,Version_nueva" > "$CSVFILE"

# Procesar yum check-update
yum check-update | tail -n +5 | awk 'NF==3 {print $1, $2}' | while read pkg newver; do
  installed=$(rpm -q --qf "%{VERSION}-%{RELEASE}" "$pkg" 2>/dev/null)
  # Imprimir en pantalla y log
  printf "%-35s %-25s %-25s\n" "$pkg" "$installed" "$newver" | tee -a "$LOGFILE"
  # Guardar en CSV
  echo "$pkg,$installed,$newver" >> "$CSVFILE"
done
