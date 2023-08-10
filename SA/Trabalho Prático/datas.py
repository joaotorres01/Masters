import json
from datetime import datetime

with open('jsons_originais/dia6.json', 'r') as f:
    dados_json = json.load(f)

dados_filtrados = []
data_inicio = datetime(2023, 5, 9, 8, 30, 0)
data_fim = datetime(2023, 5, 9, 22, 0, 0)

for mac, dados in dados_json['dados'].items():
    for id, leitura in dados.items():
        timestamp = datetime.strptime(leitura['timestamp'], '%d-%m-%Y %H:%M:%S')
        if data_inicio <= timestamp <= data_fim:
            dados_filtrados.append({mac: {id: leitura}})

dados_filtrados_json = {'dados': {}}
for dados in dados_filtrados:
    mac = list(dados.keys())[0]
    if mac not in dados_filtrados_json['dados']:
        dados_filtrados_json['dados'][mac] = {}
    dados_filtrados_json['dados'][mac].update(dados[mac])

with open('jsons_tratados/terca.json', 'w') as f:
    json.dump(dados_filtrados_json, f, indent=2)
