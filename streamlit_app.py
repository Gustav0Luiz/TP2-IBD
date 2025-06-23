import streamlit as st
import sqlite3
import pandas as pd

# ~/.local/bin/streamlit run streamlit_app.py

DB_PATH = "vacinacao.db"

QUERIES = {
    "Consulta 1 — Pacientes com 60 anos ou mais":
     """
        SELECT
            p.id, p.idade, p.sexo
        FROM Paciente AS p
        WHERE p.idade >= 60
    """,

    "Consulta 2 — Aplicações entre 1 e 15 de Janeiro": 
    """
        SELECT
            *
        FROM Aplicacao AS p
        WHERE p.data_aplicacao >= '2025-01-01' AND p.data_aplicacao <= '2025-01-15'
    """,

    "Consulta 3 — Vacinas e seus fabricantes": """
        SELECT
            v.descricao AS vacina,
            f.descricao AS fabricante
        FROM Vacina AS v
        JOIN Fabricante AS f ON v.fabricante_fk = f.codigo
        ORDER BY f.descricao
    """,

    "Consulta 4 — Vacinas por grupo de atendimento": """
        SELECT
            v.descricao AS vacina,
            ga.descricao AS grupo_atendimento
        FROM Vacina AS v
        JOIN GrupoAtendimento AS ga ON v.grupo_atendimento_fk = ga.codigo
    """,

    "Consulta 5 — Estabelecimentos e seus tipos": """
        SELECT
            e.nome_fantasia, te.descricao
        FROM Estabelecimento AS e
        JOIN TipoEstabelecimento AS te ON e.tipo_fk = te.codigo
        ORDER BY te.descricao;
    """,

    "Consulta 6 — Histórico de um paciente específico": """
        SELECT
        p.idade,
        p.sexo,
        rc.descricao AS raca_cor,
        e.nome_fantasia,
        m.nome AS municipio,
        v.descricao AS vacina
        FROM Aplicacao AS a
        JOIN Paciente AS p ON a.paciente_fk = p.id
        JOIN RacaCor AS rc ON rc.codigo = p.raca_cor_fk
        JOIN Estabelecimento AS e ON e.id = a.estabelecimento_fk
        JOIN Municipio AS m ON m.codigo = e.municipio_fk
        JOIN Vacina AS v ON v.id = a.vacina_fk
        WHERE p.id = '4b55e0ef6c5d4de5f5315ccbc65bc66d1c7af362e7ade23606318259c39d90e0'
    """,


    "Consulta 7 — Pacientes 60+ com COVID/H1N1": """
        SELECT
            p.id, p.idade, p.sexo
        FROM Paciente AS p
        JOIN Aplicacao AS a ON p.id = a.paciente_fk
        JOIN Vacina AS v ON a.vacina_fk = v.id
        WHERE
            v.id IN (21,31,52)
            AND p.idade >= 60
        ORDER BY p.idade DESC
    """,

    "Consulta 8 — Aplicações por sistema de origem": """
        SELECT DISTINCT
            v.descricao AS vacina,
            so.descricao AS sistema_origem,
            a.data_aplicacao
        FROM Aplicacao AS a
        JOIN Vacina AS v ON a.vacina_fk = v.id
        JOIN SistemaOrigem AS so ON a.sistema_origem_fk = so.codigo
    """,


    "Consulta 9 — Total por raça/cor": """
        SELECT
            rc.descricao,
            COUNT(p.id) AS total_pacientes
        FROM Paciente AS p
        JOIN RacaCor AS rc ON p.raca_cor_fk = rc.codigo
        GROUP BY rc.descricao
        ORDER BY total_pacientes DESC;
    """,

    "Consulta 10 — Doses por fabricante em BH": """
        SELECT
            f.descricao,
            COUNT(a.vacina_fk) AS total_doses_bh
        FROM Aplicacao AS a
        JOIN Vacina AS v ON a.vacina_fk = v.id
        JOIN Fabricante AS f ON v.fabricante_fk = f.codigo
        JOIN Estabelecimento AS e ON a.estabelecimento_fk = e.id
        JOIN Municipio AS m ON e.municipio_fk = m.codigo
        WHERE m.nome = 'BELO HORIZONTE'
        GROUP BY f.descricao
        ORDER BY total_doses_bh DESC
    """
}

@st.cache_data(ttl=600)
def run_query(sql):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn)


DESCRICOES = {
    "Consulta 1 — Pacientes com 60 anos ou mais": "Monitorar um grupo etário prioritário para possíveis campanhas de vacinação caso a quantidade registrada esteja abaixo do ideal. É uma faixa etária que está sob constante risco de infecção, então a busca permite avaliar a cobertura vacinal destinada a eles.",
    
    "Consulta 2 — Aplicações entre 1 e 15 de Janeiro": "A análise neste período inicial do ano é vital para monitorar o ritmo inicial das campanhas de vacinação no ano, além do fato de monitorar como os serviços de saúde estão respondendo à carga de trabalho ao fim das férias.",
    
    "Consulta 3 — Vacinas e seus fabricantes": "Consulta com maior valor administrativo, principalmente no âmbito de diversificação de fornecedores de vacinas, sendo possível ponderar novas escolhas de negócios.",
    
    "Consulta 4 — Vacinas por grupo de atendimento": "Permite análise dos principais focos de cada imunizante, identificando o público-alvo prioritário de cada vacina e determinando possíveis grupos com carência de cobertura.",
    
    "Consulta 5 — Estabelecimentos e seus tipos": "Mapeamento da rede de vacinação, essencial para a logística de distribuição de vacinas, como priorizar unidades básicas de saúde, por exemplo.",
    
    "Consulta 6 — Histórico de um paciente específico": "Consulta útil para avaliação médica individual. Permite a visualização do histórico de vacinação do paciente em 2025.",
    
    "Consulta 7 — Pacientes 60+ com COVID/H1N1": "Consulta importante para o monitoramento de doenças endêmicas em grupos de risco, ajudando a avaliar a necessidade de campanhas de reforço.",
    
    "Consulta 8 — Aplicações por sistema de origem": "Voltada para auditoria e verificação da integridade do banco de dados, identificando possíveis falhas entre sistemas de origem e banco de destino.",
    
    "Consulta 9 — Total por raça/cor": "Avalia a distribuição de vacinação entre diferentes grupos raciais e étnicos, auxiliando no direcionamento de políticas públicas para equidade na saúde.",
    
    "Consulta 10 — Doses por fabricante em BH": "Consulta administrativa para verificar a atuação dos fabricantes no município de Belo Horizonte, auxiliando na diversificação de fornecedores e planejamento logístico."
}


def main():
    st.set_page_config("TP2 - Visualização Vacinação", layout="wide")
    st.sidebar.title("Escolha a Consulta")
    
    opcao = st.sidebar.selectbox("Consulta", list(QUERIES.keys()))
    sql = QUERIES[opcao]

    # Título dinâmico principal da consulta
    st.title("Análise de Doses Aplicadas pelo Programa Nacional de Imunizações (PNI) em 2025")
    st.markdown(f"**Objetivo:** {DESCRICOES.get(opcao, 'Descrição não disponível.')}")
    st.subheader(opcao)  # esse é o nome da consulta exibido acima da query

    # Mostrar o SQL da consulta
    with st.expander("📝 Ver SQL utilizado nesta consulta"):
        st.code(sql, language="sql")

    # Executa a query e exibe os dados
    df = run_query(sql)
    st.dataframe(df, use_container_width=True)

    # Opção de gráfico
    st.sidebar.markdown("---")
    chart = st.sidebar.selectbox("Gráfico", ["Nenhum", "Bar Chart", "Line Chart", "Area Chart"])
    if chart != "Nenhum" and df.shape[1] >= 2:
        st.subheader(f"Gráfico: {chart}")
        if chart == "Bar Chart":
            st.bar_chart(df.set_index(df.columns[0]))
        elif chart == "Line Chart":
            st.line_chart(df.set_index(df.columns[0]))
        elif chart == "Area Chart":
            st.area_chart(df.set_index(df.columns[0]))
if __name__ == "__main__":
    main()
