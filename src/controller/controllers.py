import pandas as pd
import os
import glob

from pandera.errors import SchemaErrors
from pathlib import Path

from src.database.db import SessionLocal, engine, Base
from src.database.db_models import Funcionario
from src.schemas.schema import schema_funcionarios

Base.metadata.create_all(bind=engine)


def ler_e_validar_arquivo(pasta: str) -> Path:
    arquivos = glob.glob(os.path.join(pasta, 'funcionarios.csv'))
    if not arquivos:
        print(f"Nenhum arquivo encontrado.")
        return None
    
    arquivo = Path(arquivos[0])
    if not arquivo:
        print(f"Arquivo não encontrado")
        return None
    else:
        print(f"Lendo arquivo: {arquivo}")

    df = pd.read_csv(arquivo)
    df['salario'] = pd.to_numeric(df['salario'], errors='coerce')
    df['bonus_percentual'] = pd.to_numeric(df['bonus_percentual'], errors='coerce')

    file_path_validos = Path(pasta) / 'relatorio_individual.csv'
    file_path_invalidos = Path(pasta) / 'dados_invalidos.csv'

    try:
        df_validado = schema_funcionarios.validate(df, lazy=True)
        df_validado.to_csv(file_path_validos, index=False)
        print(f"✅ {len(df_validado)} registros validados.")
        return file_path_validos
    
    except SchemaErrors as e:
        error_df = e.failure_cases
        invalid_indices = error_df['index'].unique()
        df_invalidos = df.loc[invalid_indices]
        df_validos = df.drop(index=invalid_indices)

        if not df_invalidos.empty:
            df_invalidos.to_csv(file_path_invalidos, index=False)
            print(f"🚫 {len(df_invalidos)} registros inválidos salvos.")

        print("\n Detalhes do erro:")
        print(error_df[["column", "check", "failure_case", "index"]].head())

        return df_validos
    

def salvar_dados_validos(df_validos: pd.DataFrame) -> Funcionario:
    if df_validos.empty:
        print(f"Nenhum arquivo validado encontrado")
        return None
    
    funcionarios_salvos = []

    try:
        with SessionLocal() as session:
                    funcionario = [
                        Funcionario(
                            id = row['id'],
                            nome = row['nome'],
                            area = row['area'],
                            salario = row['salario'],
                            bonus_percentual = row['bonus_percentual']
                        )
                        for _, row in df_validos.iterrows()
                    ]

                    session.add_all(funcionario)
                    session.commit()
                    funcionarios_salvos.extend(funcionario)

                    print(f"✅ {len(funcionarios_salvos)} registros salvos no Banco de Dados.")
                    return funcionarios_salvos
    
    except Exception as e:
        print("Não foi possível salvar os dados no banco de dados.")
        return None

if __name__ == '__main__':
    df = ler_e_validar_arquivo('data')
    banco = salvar_dados_validos(df)