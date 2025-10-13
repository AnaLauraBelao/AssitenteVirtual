#!/bin/bash

# Função para exibir uso correto do script
usage() {
  echo "Uso: $0 --resource-group-name=VALOR --server-name=VALOR --rule-name=VALOR"
  echo "       [--new-ip=VALOR (opcional)]"
  exit 1
}

# Defina os valores padrão
newIp=$(curl -s https://ifconfig.me)

# Parse os parâmetros da linha de comando
for i in "$@"; do
  case $i in
    --resource-group=*)
      resourceGroupName="${i#*=}"
      shift
      ;;
    --server-name=*)
      serverName="${i#*=}"
      shift
      ;;
    --subscription=*)
      subscription="${i#*=}"
      shift
      ;;
    --rule-name=*)
      ruleName="${i#*=}"
      ruleName=$(echo $ruleName | sed 's/ /_/g')
      shift
      ;;
    --ip=*)
      newIp="${i#*=}"
      shift
      ;;
    *)
      echo "Parâmetro desconhecido: $i"
      usage
      ;;
  esac
done

# Verifique se todos os parâmetros obrigatórios foram passados
if [ -z "$resourceGroupName" ] || [ -z "$serverName" ] || [ -z "$ruleName" ]; then
  echo "Parâmetros obrigatórios não fornecidos."
  usage
fi

# Obtenha a regra de firewall existente
existingRule=$(az sql server firewall-rule show --subscription $subscription --resource-group $resourceGroupName --server $serverName --name $ruleName)

if [ -z "$existingRule" ]; then
  az sql server firewall-rule create --subscription $subscription --resource-group $resourceGroupName --server $serverName --name $ruleName --start-ip-address $newIp --end-ip-address $newIp
  echo "Regra de firewall criada com sucesso."
  exit 1
fi

# Atualize a regra de firewall com o novo IP
az sql server firewall-rule update --subscription $subscription --resource-group $resourceGroupName --server $serverName --name "$ruleName" --start-ip-address $newIp --end-ip-address $newIp

echo "Regra de firewall atualizada com sucesso."
