import json
import csv
import uuid

with open('jsons_tratados/terca.json', 'r') as f:
    dados_json = json.load(f)

cabecalho = ['id', 'mac', 'rssi', 'timestamp']
linhas_csv = []

for mac, dados in dados_json['dados'].items():
    for id, leitura in dados.items():
        linha = [str(uuid.uuid4()), leitura['mac'], leitura['rssi'], leitura['timestamp']]
        linhas_csv.append(linha)

with open('csvs/terca.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(cabecalho)
    writer.writerows(linhas_csv)
