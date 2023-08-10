import os
import csv

caminho_pasta = 'csvs'
conteudo_csv = []

fieldnames = ['id', 'mac', 'rssi', 'timestamp']

for nome_arquivo in os.listdir(caminho_pasta):
    if nome_arquivo.endswith('.csv'):
        caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
        with open(caminho_arquivo, 'r', newline='') as f:
            conteudo_csv += list(csv.DictReader(f))

with open('datagymbox.csv', 'w', newline='') as f:
    escritor_csv = csv.DictWriter(f, fieldnames=fieldnames)
    escritor_csv.writeheader()
    for row in conteudo_csv:
        nova_linha = {
            'id': row['id'],
            'mac': row['mac'],
            'rssi': row['rssi'],
            'timestamp': row['timestamp']
        }
        escritor_csv.writerow(nova_linha)
