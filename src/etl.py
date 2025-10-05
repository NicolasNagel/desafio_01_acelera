import pandas as pd

import csv
import json

from pathlib import Path


def ler_e_validar_arquivo(pasta: str) -> str:
    """
    Lê o arquivo 'funcionarios.csv' em uma pasta, valida as colunas e
    salva os dados válidos e inválidos em arquivos CSV separados.

    Retorna:
        -> Path_dados_validos
    """
    pasta_path: str = Path(pasta)
    pasta_path.mkdir(exist_ok=True)

    arquivo_entrada = pasta_path / 'funcionarios.csv'
    file_path_validados = pasta_path / 'dados_validos.csv'
    file_path_invalidados = pasta_path / 'dados_invalidos.csv'

    if not arquivo_entrada.exists():
        print(f"Arquivo {arquivo_entrada} não encontrado")
        return None, None

    with open(file=arquivo_entrada, mode='r', encoding='utf-8') as file:
        _reader = csv.DictReader(file)

        dados_validos: list = []
        dados_invalidos: list = []
        fieldnames = _reader.fieldnames

        for linha in _reader:
            linha_valida = True

            try:
                if linha['nome'].strip() == '':
                    print(f"Linha Inválida, nome incorreto!")
                    linha_valida = False
                    
                if linha['area'].strip() == '':
                    print(f"Linha Inválida, área incorreta!")
                    linha_valida = False

                try:
                    salario = float(linha['salario'])
                    if salario < 0:
                        print(f"Linha inválida, salário incorreto!")
                        linha_valida = False
                except ValueError:
                    print(f"Linha inválida, salário incorreto!")
                    linha_valida = False

                try:
                    bonus = float(linha['bonus_percentual'])
                    if not (0 < bonus < 1):
                        print(f"Linha inválida, campo bônus percentual incorreto!")
                        linha_valida = False
                except ValueError:
                    print(f"Linha inválida, campo bônus percentual incorreto!")
                    linha_valida = False

            except Exception as e:
                print(f"Erro ao ler o arquivo: {file}")

            if linha_valida:
                dados_validos.append(linha)
            else:
                dados_invalidos.append(linha)

    if dados_invalidos:
        with open(file_path_invalidados, mode='w', newline='', encoding='utf-8') as file:
            _writer = csv.DictWriter(file, fieldnames=fieldnames)
            _writer.writeheader()
            _writer.writerows(dados_invalidos)
        print(f"🚫 {len(dados_invalidos)} registros inválidos salvos em: {file_path_invalidados}")
    else:
        print("Nenhum dado inválido encontrado.")

    if dados_validos:
        with open(file_path_validados, mode='w', newline='', encoding='utf-8') as file:
            _writer = csv.DictWriter(file, fieldnames=fieldnames)
            _writer.writeheader()
            _writer.writerows(dados_validos)
        print(f"✅ {len(dados_validos)} registros válidos retornados para processamento.")
    else:
        print("Nenhum dado válido encontrado.")

    return file_path_validados


def calcular_kpis(arquivo_validado: str) -> json:
    """
    Lê o arquivo de dados válidos e calcula KPIs em formato JSON.
    
    Retorna: 
        -> Caminho do arquivo JSON gerado.
    """
    if not arquivo_validado.exists():
        print(f"Arquivo {arquivo_validado} não encontrado")

    df = pd.read_csv(arquivo_validado)
    df['bonus_final'] = 1000 + df['salario'] * df['bonus_percentual']

    media_por_area = df.groupby("area")['salario'].mean().round(2).to_dict()
    qtd_por_area = df.groupby("area")['id'].count().to_dict()
    bonus_total = df['bonus_final'].sum().round(2)

    top3 = (
        df[['nome', 'area', 'salario', 'bonus_percentual', 'bonus_final']]
        .sort_values(by='bonus_final', ascending=False)
        .head(3)
        .to_dict(orient='records')
    )

    resultado = {
        "quantidade_por_area": qtd_por_area,
        "media_salario_por_area": media_por_area,
        "bonus_total": bonus_total,
        "top3_bonus": top3
    }

    arquivo_saida = arquivo_validado.parent / 'kpis.json'
    with open(arquivo_saida, mode="w", encoding="utf-8") as file:
        json.dump(resultado, file, ensure_ascii=False, indent=4)

    print(f"📊 Cálculos de KPIs realizados e salvos em formato JSON: {arquivo_saida}")
    return arquivo_saida