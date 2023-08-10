import csv
import datetime

# Função para converter a data e hora no formato desejado
def format_timestamp(timestamp):
    date_obj = datetime.datetime.strptime(timestamp, '%d-%m-%Y %H:%M:%S')
    day = date_obj.day
    month = date_obj.month
    year = date_obj.year
    weekday = date_obj.strftime('%A')
    hour = date_obj.hour
    minute = date_obj.minute
    second = date_obj.second
    return day, month, year, weekday, hour, minute, second

# Caminho do arquivo CSV de entrada e saída
input_file = 'datagymbox.csv'
output_file = 'datagymbox_treated.csv'

# Conjunto para armazenar entradas únicas
unique_entries = set()

# Abrir o arquivo de entrada e criar o arquivo de saída
with open(input_file, 'r') as file_in, open(output_file, 'w', newline='') as file_out:
    reader = csv.reader(file_in)
    writer = csv.writer(file_out)

    # Escrever o cabeçalho no arquivo de saída
    writer.writerow(['id', 'mac', 'rssi', 'day', 'month', 'year', 'weekday', 'hour', 'minute', 'second'])

    # Percorrer cada linha do arquivo de entrada
    for row in reader:
        if reader.line_num == 1:
            continue  # Ignorar o cabeçalho
        else:
            # Obter os valores da linha
            entry_id, mac, rssi, timestamp = row

            # Verificar se o valor de rssi está entre -80 e 0
            if int(rssi) >= -80 and int(rssi) <= 0:
                # Converter a data e hora no formato desejado
                day, month, year, weekday, hour, minute, second = format_timestamp(timestamp)

                # Criar uma chave única para verificar duplicatas
                entry_key = (entry_id, mac, rssi, day, month, year, weekday, hour, minute, second)

                # Verificar se a entrada já existe
                if entry_key not in unique_entries:
                    # Adicionar a entrada única ao conjunto
                    unique_entries.add(entry_key)

                    # Escrever a linha no arquivo de saída
                    writer.writerow([entry_id, mac, rssi, day, month, year, weekday, hour, minute, second])

print("O novo arquivo CSV foi gerado com sucesso!")
