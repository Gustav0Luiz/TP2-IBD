# tp2_extracao_carga.py

import requests
import json
import time
import pandas as pd
import sqlite3
from pathlib import Path

# ---------- ETAPA 1: Coleta de dados ----------
def coletar_dados_vacinacao(max_paginas=10, delay=1, salvar_arquivo=True):
    base_url = "https://apidadosabertos.saude.gov.br/vacinacao/doses-aplicadas-pni-2025"
    limit = 1000
    offset = 0
    all_data = []

    for pagina in range(max_paginas):
        url = f"{base_url}?limit={limit}&offset={offset}"
        response = requests.get(url, headers={"accept": "application/json"})

        if response.status_code != 200:
            print(f"Erro na página {pagina}: Status {response.status_code}")
            break

        dados = response.json().get("doses_aplicadas_pni", [])
        if not dados:
            print(f"Sem dados na página {pagina}, encerrando.")
            break

        all_data.extend(dados)
        print(f"Página {pagina} coletada com {len(dados)} registros.")
        offset += 1
        time.sleep(delay)

    if salvar_arquivo:
        with open("dados_vacinacao_2025.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"Arquivo 'dados_vacinacao_2025.json' salvo com {len(all_data)} registros.")

    return all_data

# ---------- ETAPA 2: Unificação dos JSONs ----------
def unificar_jsons_em_tabela(caminho_json: str) -> pd.DataFrame:
    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return pd.DataFrame(dados)

# ---------- ETAPA 3: Criação e carga do banco ----------
def criar_banco_e_popular(df_unificado: pd.DataFrame, caminho_db="vacinacao.db"):
    conn = sqlite3.connect(caminho_db)

    tabelas_para_dropar = [
        'Aplicacao', 'Paciente', 'Estabelecimento', 'Vacina', 'RacaCor', 'EtniaIndigena',
        'Municipio', 'UF', 'Fabricante', 'DoseVacina', 'GrupoAtendimento', 'CategoriaAtendimento',
        'TipoEstabelecimento', 'NaturezaEstabelecimento', 'LocalAplicacao', 'ViaAdministracao',
        'EstrategiaVacinacao', 'CondicaoMaternal', 'OrigemRegistro', 'SistemaOrigem'
    ]
    for tabela in tabelas_para_dropar:
        conn.execute(f'DROP TABLE IF EXISTS {tabela}')

    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    # Populando tabelas de dimensão
    def carregar_dimensao(col_map, tabela):
        df_dim = df_unificado[list(col_map.keys())].rename(columns=col_map).dropna(subset=[list(col_map.values())[0]]).drop_duplicates(subset=[list(col_map.values())[0]])
        df_dim.to_sql(tabela, conn, if_exists='append', index=False)

    carregar_dimensao({'codigo_raca_cor_paciente': 'codigo', 'nome_raca_cor_paciente': 'descricao'}, 'RacaCor')
    carregar_dimensao({'codigo_etnia_indigena_paciente': 'codigo', 'nome_etnia_indigena_paciente': 'descricao'}, 'EtniaIndigena')

    ufs_df = pd.concat([
        df_unificado[['sigla_uf_paciente', 'nome_uf_paciente']].rename(columns={'sigla_uf_paciente': 'sigla', 'nome_uf_paciente': 'nome'}),
        df_unificado[['sigla_uf_estabelecimento', 'nome_uf_estabelecimento']].rename(columns={'sigla_uf_estabelecimento': 'sigla', 'nome_uf_estabelecimento': 'nome'})
    ]).dropna(subset=['sigla']).drop_duplicates(subset=['sigla'])
    ufs_df.to_sql('UF', conn, if_exists='append', index=False)

    municipios_df = pd.concat([
        df_unificado[['codigo_municipio_paciente', 'nome_municipio_paciente', 'sigla_uf_paciente']].rename(columns={'codigo_municipio_paciente': 'codigo', 'nome_municipio_paciente': 'nome', 'sigla_uf_paciente': 'uf_sigla'}),
        df_unificado[['codigo_municipio_estabelecimento', 'nome_municipio_estabelecimento', 'sigla_uf_estabelecimento']].rename(columns={'codigo_municipio_estabelecimento': 'codigo', 'nome_municipio_estabelecimento': 'nome', 'sigla_uf_estabelecimento': 'uf_sigla'})
    ]).dropna(subset=['codigo']).drop_duplicates(subset=['codigo'])
    municipios_df.to_sql('Municipio', conn, if_exists='append', index=False)

    carregar_dimensao({'codigo_vacina_fabricante': 'codigo', 'descricao_vacina_fabricante': 'descricao'}, 'Fabricante')
    carregar_dimensao({'codigo_dose_vacina': 'codigo', 'descricao_dose_vacina': 'descricao'}, 'DoseVacina')
    carregar_dimensao({'codigo_vacina_grupo_atendimento': 'codigo', 'descricao_vacina_grupo_atendimento': 'descricao'}, 'GrupoAtendimento')
    carregar_dimensao({'codigo_vacina_categoria_atendimento': 'codigo', 'descricao_vacina_categoria_atendimento': 'descricao'}, 'CategoriaAtendimento')
    carregar_dimensao({'codigo_tipo_estabelecimento': 'codigo', 'descricao_tipo_estabelecimento': 'descricao'}, 'TipoEstabelecimento')
    carregar_dimensao({'codigo_natureza_estabelecimento': 'codigo', 'descricao_natureza_estabelecimento': 'descricao'}, 'NaturezaEstabelecimento')
    carregar_dimensao({'codigo_local_aplicacao': 'codigo', 'descricao_local_aplicacao': 'descricao'}, 'LocalAplicacao')
    carregar_dimensao({'codigo_via_administracao': 'codigo', 'descricao_via_administracao': 'descricao'}, 'ViaAdministracao')
    carregar_dimensao({'codigo_estrategia_vacinacao': 'codigo', 'descricao_estrategia_vacinacao': 'descricao'}, 'EstrategiaVacinacao')
    carregar_dimensao({'codigo_condicao_maternal': 'codigo', 'descricao_condicao_maternal': 'descricao'}, 'CondicaoMaternal')
    carregar_dimensao({'codigo_origem_registro': 'codigo', 'descricao_origem_registro': 'descricao'}, 'OrigemRegistro')
    carregar_dimensao({'codigo_sistema_origem': 'codigo', 'descricao_sistema_origem': 'descricao'}, 'SistemaOrigem')

    # Entidades principais
    df_unificado[['codigo_paciente', 'tipo_sexo_paciente', 'numero_idade_paciente', 'numero_cep_paciente', 'descricao_nacionalidade_paciente', 'codigo_raca_cor_paciente', 'codigo_municipio_paciente', 'codigo_etnia_indigena_paciente']].rename(columns={
        'codigo_paciente': 'id', 'tipo_sexo_paciente': 'sexo', 'numero_idade_paciente': 'idade', 'numero_cep_paciente': 'cep', 'descricao_nacionalidade_paciente': 'nacionalidade', 'codigo_raca_cor_paciente': 'raca_cor_fk', 'codigo_municipio_paciente': 'municipio_fk', 'codigo_etnia_indigena_paciente': 'etnia_indigena_fk'
    }).dropna(subset=['id']).drop_duplicates(subset=['id']).to_sql("Paciente", conn, if_exists="append", index=False)

    df_unificado[['codigo_cnes_estabelecimento', 'nome_razao_social_estabelecimento', 'nome_fantasia_estalecimento', 'codigo_municipio_estabelecimento', 'codigo_tipo_estabelecimento', 'codigo_natureza_estabelecimento']].rename(columns={
        'codigo_cnes_estabelecimento': 'id', 'nome_razao_social_estabelecimento': 'razao_social', 'nome_fantasia_estalecimento': 'nome_fantasia', 'codigo_municipio_estabelecimento': 'municipio_fk', 'codigo_tipo_estabelecimento': 'tipo_fk', 'codigo_natureza_estabelecimento': 'natureza_fk'
    }).dropna(subset=['id']).drop_duplicates(subset=['id']).to_sql("Estabelecimento", conn, if_exists="append", index=False)

    df_unificado[['codigo_vacina', 'descricao_vacina', 'sigla_vacina', 'codigo_vacina_fabricante', 'codigo_vacina_grupo_atendimento', 'codigo_vacina_categoria_atendimento']].rename(columns={
        'codigo_vacina': 'id', 'descricao_vacina': 'descricao', 'sigla_vacina': 'sigla', 'codigo_vacina_fabricante': 'fabricante_fk', 'codigo_vacina_grupo_atendimento': 'grupo_atendimento_fk', 'codigo_vacina_categoria_atendimento': 'categoria_atendimento_fk'
    }).dropna(subset=['id']).drop_duplicates(subset=['id']).to_sql("Vacina", conn, if_exists="append", index=False)

    df_unificado[['codigo_documento', 'data_vacina', 'codigo_lote_vacina', 'status_documento', 'codigo_paciente', 'codigo_vacina', 'codigo_cnes_estabelecimento', 'codigo_dose_vacina', 'codigo_local_aplicacao', 'codigo_via_administracao', 'codigo_estrategia_vacinacao', 'codigo_condicao_maternal', 'codigo_origem_registro', 'codigo_sistema_origem']].rename(columns={
        'codigo_documento': 'id', 'data_vacina': 'data_aplicacao', 'codigo_lote_vacina': 'lote', 'codigo_paciente': 'paciente_fk', 'codigo_vacina': 'vacina_fk', 'codigo_cnes_estabelecimento': 'estabelecimento_fk', 'codigo_dose_vacina': 'dose_fk', 'codigo_local_aplicacao': 'local_aplicacao_fk', 'codigo_via_administracao': 'via_administracao_fk', 'codigo_estrategia_vacinacao': 'estrategia_fk', 'codigo_condicao_maternal': 'condicao_maternal_fk', 'codigo_origem_registro': 'origem_registro_fk', 'codigo_sistema_origem': 'sistema_origem_fk'
    }).dropna(subset=['id']).drop_duplicates(subset=['id']).to_sql("Aplicacao", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()
    print(f"Banco de dados salvo como '{caminho_db}'")


# ---------- EXECUÇÃO COMPLETA ----------
if __name__ == "__main__":
    dados = coletar_dados_vacinacao(max_paginas=100, delay=1, salvar_arquivo=True)
    df = unificar_jsons_em_tabela("dados_vacinacao_2025.json")

    # Garante que o schema.sql esteja presente antes de rodar
    if not Path("schema.sql").exists():
        print("ERRO: Arquivo 'schema.sql' com o esquema do banco não encontrado.")
    else:
        criar_banco_e_popular(df, caminho_db="vacinacao.db")
