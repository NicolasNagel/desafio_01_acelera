import pandas as pd

import os
import glob
import json
import csv

from pathlib import Path

def validar_dados(linha: str) -> bool:
    """
    Valida cada linha do CSV, garantindo que todos os campos
    obrigatórios estejam corretos.
    """
    try:
        if not linha.get('nome') or linha['nome'].strip() == '':
            return False
        
        if not linha.get('area') or linha['area'].strip() == '':
            return False
        
        try:
            salario = float(linha.get('salario'))
            if salario < 0:
                return False
        except ValueError:
            return False
        
        try:
            bonus = float(linha.get('bonus_percentual'))
            if not (0 < bonus < 1):
                return False
        except ValueError:
            return False
        
        return True
    
    except Exception:
        return False
    

def ler_e_validar_arquivo(pasta: str) -> Path:
    """
    Lê o arquivo 'funcionarios.csv' em uma pasta, valida as colunas e
    salva os dados válidos e inválidos em arquivos CSV separados.

    Argumentos:
        - pasta (str): caminho do arquivo CSV.

    Retorno:
        - Caminho do arquivo validado.
    """
    arquivos = glob.glob(os.path.join(pasta, 'funcionarios.csv'))
    if not arquivos:
        print("Nenhum arquivo encontrado.")
        return None
    
    arquivo: Path = Path(arquivos[0])
    if not arquivo:
        print(f"O arquivo: {arquivo} não foi encontrado na pasta.")
        return None
    else:
        print(f"Lendo arquivo: {arquivo}")
    
    file_path_validos: Path = Path(pasta) / 'relatorio_individual.csv'
    file_path_invalidos: Path = Path(pasta) / 'dados_invalidos.csv'
    
    with open(file=arquivo, mode='r', encoding='utf-8') as file:
        _reader: csv.DictReader = csv.DictReader(file)

        dados_validos, dados_invalidos = [], []
        filednames = _reader.fieldnames

        for linha in _reader:
            if validar_dados(linha):
                dados_validos.append(linha)
            else:
                dados_invalidos.append(linha)

    if dados_invalidos:
        with open(file=file_path_invalidos, mode='w', newline='', encoding='utf-8') as file:
            _writer: csv.DictWriter = csv.DictWriter(file, filednames=filednames)
            _writer.writeheader()
            _writer.writerows(dados_invalidos)
            print(f"🚫 {len(dados_invalidos)} registros inválidos salvos em: {file_path_invalidos}")
    else:
        print("Nenhum dado inválido encontrado.")

    if dados_validos:
        with open(file=file_path_validos, mode='w', newline='', encoding='utf-8') as file:
            _writer: csv.DictWriter = csv.DictWriter(file, fieldnames=filednames)
            _writer.writeheader()
            _writer.writerows(dados_validos)
            print(f"✅ {len(dados_validos)} registros válidos retornados para processamento.")
    else:
        print("Nenhum dado válido encontrado.")

    return file_path_validos


def calcular_kpi(arquivo_validado: str) -> json:
    """
    Lê o arquivo de dados válidos e calcula KPIs em formato JSON.

    Argumentos:
        -> arquivo_validado (str | Path): nome ou caminho do arquivo validado.
    
    Retorna: 
        -> Caminho do arquivo JSON gerado.
    """
    arquivo_validado = Path(arquivo_validado)
    if not arquivo_validado:
        print(f"❌ Arquivo: {arquivo_validado} não encontrado")
        return None
    else:
        print(f"Lendo arquivo {arquivo_validado} e calculando KPI")

    df = pd.read_csv(arquivo_validado)
    if df.empty:
        print("⚠️ Arquivo validado está vazio. Nenhum KPI calculado.")

    df['bonus_final'] = 1000 + ( df['salario'] * df['bonus_percentual'] )

    media_por_area = df.groupby('area')['salario'].mean().round(2).to_dict()
    qtd_por_area = df.groupby('area').size().to_dict()
    bonus_total = df['bonus_final']

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

    with open(file="kpis.json", mode="w", encoding="utf-8") as file:
        json.dump(resultado, file, ensure_ascii=False, indent=4)

    print(f"Arquivo JSON gerado: kpis.json")