from src.etl import ler_e_validar_arquivo, calcular_kpis

dados_validados = ler_e_validar_arquivo('data')
kpis_calculados = calcular_kpis(dados_validados)