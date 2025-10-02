import pandas as pd
import csv
import json

from pathlib import Path

# Declarando variávies
file_path: Path = 'funcionarios.csv'
file_path_validados = 'relatorio_individual.csv'
file_path_invalidos: Path = 'dados_invalidos.csv'

with open(file=file_path, mode='r', encoding='utf-8') as file:
    _reader: csv.DictReader = csv.DictReader(file)

    dados_validos: list = []
    dados_invalidos: list = []
    fieldnames = _reader.fieldnames

    for linha in _reader:
        # Variável de controle, assume válida até que se encontre um erro 
        linha_valida = True

        try:
            # Validando o nome
            if linha['nome'].strip() == '':
                print(f"Linha inválida (Nome Inválido): {linha}")
                linha_valida = False

            # Validando a área
            if linha['area'].strip() == '':
                print(f"Linha inválida (Área inválida): {linha}")
                linha_valida = False

            # Validando salário
            try:
                salario = float(linha['salario'])
                if salario < 0:
                    print(f"Linha inválida (Salário Inválido): {linha}")
                    linha_valida = False
            except ValueError:
                print(f"Linha inválida (Salário Inválido): {linha}")
                linha_valida = False

            # Validando bônus
            try:
                bonus = float(linha['bonus_percentual'])
                if not (0 < bonus < 1):
                    print(f"Linha inválida (Bônus Inválido): {linha}")
                    linha_valida = False
            except ValueError:
                print(f"Linha inválida (Bônus Inválido): {linha}")
                linha_valida = False

        except Exception as e:
            print("Erro ao validar o dataset.")

        # Fazendo a classificação final das linhas
        if linha_valida:
            dados_validos.append(linha)
        else:
            dados_invalidos.append(linha)

# Salvando os registros inválidos
if dados_invalidos:
    with open(file_path_invalidos, mode='w', newline='', encoding='utf-8') as file:
        _writer = csv.DictWriter(file, fieldnames=fieldnames)
        _writer.writeheader()
        _writer.writerows(dados_invalidos)
    print(f"Foram salvos {len(dados_invalidos)} registros no arquivo: {file_path_invalidos}")
else:
    print("Nenhum dado inválido encontrado.")

# Salvando os registros válidos
if dados_validos:
    with open(file_path_validados, mode='w', newline='', encoding='utf-8') as file:
        _writer = csv.DictWriter(file, fieldnames=fieldnames)
        _writer.writeheader()
        _writer.writerows(dados_validos)
    print(f"Foram salvos {len(dados_validos)} registros no arquivo: {file_path_validados}")
else:
    print("Nenhum dado válido encontrado.")


# Calculando o bônus nos dados validados
df = pd.read_csv(file_path_validados)

# Cálculo direto
df['bonus_final'] = 1000 + df['salario'] * df['bonus_percentual']

# agregações
media_por_area = df.groupby("area")['salario'].mean().round(2).to_dict()
qtd_por_area = df.groupby("area")['id'].count().to_dict()
bonus_total = df['bonus_final'].sum().round(2)

# Top 3 funcionários com maior bônus final
top3 = (
    df[['nome', 'area', 'salario', 'bonus_percentual', 'bonus_final']]
    .sort_values(by='bonus_final', ascending=False)
    .head(3)
    .to_dict(orient='records')
)

# Estruturando o arquivo JSON
resultado = {
    "quantidade_por_area": qtd_por_area,
    "media_salario_por_area": media_por_area,
    "bonus_total": bonus_total,
    "top3_bonus": top3
}

with open(file="kpis.json", mode="w", encoding="utf-8") as file:
    json.dump(resultado, file, ensure_ascii=False, indent=4)

print(f"Arquivo JSON gerado: kpis.json")