#!/bin/bash

trap 'echo "Execução encerrada inesperadamente."; exit 99' EXIT

usage() {
  echo "Uso: $0 --resource-group=VALOR --server-name=VALOR --rule-name=VALOR [--ip=VALOR (opcional) --type=VALOR(opcional)]"
  exit 1
}

newIp=$(curl -s https://ifconfig.me)

for i in "$@"; do
  case $i in
    --subscription=*) subscription="${i#*=}"; shift ;;
    --resource-group=*) resourceGroupName="${i#*=}"; shift ;;
    --server-name=*) serverName="${i#*=}"; shift ;;
    --rule-name=*) ruleName="${i#*=}"; ruleName=$(echo $ruleName | sed 's/ /_/g'); shift ;;
    --ip=*) newIp="${i#*=}"; shift ;;
    --type=*) type="${i#*=}"; shift ;;
  esac
done

if [ -z "$subscription" ] || [ -z "$resourceGroupName" ] || [ -z "$serverName" ] || [ -z "$ruleName" ]; then
  echo "Parâmetros obrigatórios não fornecidos."
  usage
fi

if [ "$type" == "sqlserver" ]; then
  existingRule=$(az sql server firewall-rule show --subscription $subscription --resource-group $resourceGroupName --server $serverName --name $ruleName 2>/dev/null)
  if [ -z "$existingRule" ]; then
    az sql server firewall-rule create --subscription $subscription --resource-group $resourceGroupName --server $serverName --name $ruleName --start-ip-address $newIp --end-ip-address $newIp 2>/dev/null
    if [ $? -ne 0 ]; then
      echo "Erro ao criar a regra de firewall SQL Server."
      exit 2
    fi
    echo "Regra de firewall SQL Server criada com sucesso."
    exit 0
  fi
  az sql server firewall-rule update --subscription $subscription --resource-group $resourceGroupName --server $serverName --name "$ruleName" --start-ip-address $newIp --end-ip-address $newIp 2>/dev/null
  if [ $? -ne 0 ]; then
    echo "Erro ao atualizar a regra de firewall SQL Server."
    exit 3
  fi
  echo "Regra de firewall SQL Server atualizada com sucesso."
  exit 0
elif [ "$type" == "mysql" ]; then
  existingRule=$(az mysql flexible-server firewall-rule show --subscription $subscription --resource-group $resourceGroupName --name $serverName --rule-name $ruleName 2>/dev/null)
  if [ -z "$existingRule" ]; then
    az mysql flexible-server firewall-rule create --subscription $subscription --resource-group $resourceGroupName --name $serverName --rule-name $ruleName --start-ip-address $newIp --end-ip-address $newIp 2>/dev/null
    if [ $? -ne 0 ]; then
      echo "Erro ao criar a regra de firewall MySQL."
      exit 2
    fi
    echo "Regra de firewall MySQL criada com sucesso."
    exit 0
  fi
  az mysql flexible-server firewall-rule update --subscription $subscription --resource-group $resourceGroupName --name $serverName --rule-name "$ruleName" --start-ip-address $newIp --end-ip-address $newIp 2>/dev/null
  if [ $? -ne 0 ]; then
    echo "Erro ao atualizar a regra de firewall MySQL."
    exit 3
  fi
  echo "Regra de firewall MySQL atualizada com sucesso."
  exit 0
else
  echo "Tipo de banco não reconhecido. Use 'sqlserver' ou 'mysql'."
  usage
  exit 0
fi