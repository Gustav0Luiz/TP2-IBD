import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "vacinacao.db"

QUERIES = {
    "Consulta 1 — Cobertura Vacinal por Faixa Etária": """
        SELECT 
            CASE 
                WHEN idade < 12 THEN 'Crianças (0-11)' 
                WHEN idade BETWEEN 12 AND 17 THEN 'Adolescentes (12-17)'
                WHEN idade BETWEEN 18 AND 59 THEN 'Adultos (18-59)'
                WHEN idade >= 60 THEN 'Idosos (60+)' 
                ELSE 'Não Informado'
            END AS faixa_etaria,
            COUNT(*) AS total_aplicacoes
        FROM Paciente
        JOIN Aplicacao ON Paciente.id = Aplicacao.paciente_fk
        GROUP BY faixa_etaria
        ORDER BY total_aplicacoes DESC;
    """,

    "Consulta 2 — Vacinação por dia da semana": """
        SELECT 
            CASE strftime('%w', data_aplicacao)
                WHEN '0' THEN 'Domingo'
                WHEN '1' THEN 'Segunda'
                WHEN '2' THEN 'Terça'
                WHEN '3' THEN 'Quarta'
                WHEN '4' THEN 'Quinta'
                WHEN '5' THEN 'Sexta'
                WHEN '6' THEN 'Sábado'
            END AS dia_semana,
            COUNT(*) AS total_aplicacoes
        FROM Aplicacao AS a
        JOIN Estabelecimento AS e ON a.estabelecimento_fk = e.id
        JOIN Municipio AS m ON e.municipio_fk = m.codigo
        GROUP BY dia_semana
        ORDER BY total_aplicacoes DESC;
    """,

    "Consulta 3 — Doses Aplicadas por Etnia Indígena": """
        SELECT 
            ei.descricao AS etnia_indigena,
            COUNT(*) AS total_aplicacoes
        FROM Paciente AS p
        JOIN Aplicacao AS a ON p.id = a.paciente_fk
        JOIN EtniaIndigena AS ei ON p.etnia_indigena_fk = ei.codigo
        GROUP BY ei.descricao
        ORDER BY total_aplicacoes DESC;
    """,

    "Consulta 4 — Top Municípios com Maior Número de Doses Aplicadas": """
        SELECT 
            m.nome AS municipio,
            COUNT(*) AS total_doses
        FROM Aplicacao AS a
        JOIN Estabelecimento AS e ON a.estabelecimento_fk = e.id
        JOIN Municipio AS m ON e.municipio_fk = m.codigo
        GROUP BY m.nome
        ORDER BY total_doses DESC
        LIMIT 10;
    """,

    "Consulta 5 — Locais Anatômicos Mais Utilizados": """
        SELECT 
            l.descricao AS local_anatomico,
            COUNT(*) AS total
        FROM Aplicacao AS a
        JOIN LocalAplicacao AS l ON a.local_aplicacao_fk = l.codigo
        GROUP BY l.descricao
        ORDER BY total DESC;
    """,

    "Consulta 6 — Total por raça/cor": """
        SELECT
            rc.descricao AS raca_cor,
            COUNT(p.id) AS total_pacientes
        FROM Paciente AS p
        JOIN RacaCor AS rc ON p.raca_cor_fk = rc.codigo
        GROUP BY rc.descricao
        ORDER BY total_pacientes DESC;
    """,

    "Consulta 7 — Doses por fabricante em BH": """
        SELECT
            f.descricao AS fabricante,
            COUNT(a.vacina_fk) AS total_doses_bh
        FROM Aplicacao AS a
        JOIN Vacina AS v ON a.vacina_fk = v.id
        JOIN Fabricante AS f ON v.fabricante_fk = f.codigo
        JOIN Estabelecimento AS e ON a.estabelecimento_fk = e.id
        JOIN Municipio AS m ON e.municipio_fk = m.codigo
        WHERE m.nome = 'BELO HORIZONTE'
        GROUP BY f.descricao
        ORDER BY total_doses_bh DESC;
    """
}

DESCRICOES = {
    "Consulta 1 — Cobertura Vacinal por Faixa Etária": "Avalia o alcance da vacinação em diferentes faixas etárias.",
    "Consulta 2 — Vacinação por dia da semana": "Exibe em quais dias da semana ocorrem mais aplicações.",
    "Consulta 3 — Doses Aplicadas por Etnia Indígena": "Analisa a distribuição de vacinas entre etnias indígenas.",
    "Consulta 4 — Top Municípios com Maior Número de Doses Aplicadas": "Mostra os municípios com mais vacinações registradas.",
    "Consulta 5 — Locais Anatômicos Mais Utilizados": "Indica os locais do corpo mais utilizados nas aplicações.",
    "Consulta 6 — Total por raça/cor": "Distribuição de vacinação entre diferentes grupos raciais.",
    "Consulta 7 — Doses por fabricante em BH": "Mostra quais fabricantes são mais utilizados em BH."
}

@st.cache_data(ttl=600)
def run_query(sql):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn)

CONSULTAS_COM_GRAFICO = {
    "Consulta 1 — Cobertura Vacinal por Faixa Etária": "bar_chart",
    "Consulta 2 — Vacinação por dia da semana": "bar_chart",
    "Consulta 3 — Doses Aplicadas por Etnia Indígena": "bar_chart",
    "Consulta 4 — Top Municípios com Maior Número de Doses Aplicadas": "bar_chart",
    "Consulta 5 — Locais Anatômicos Mais Utilizados": "bar_chart",
    "Consulta 6 — Total por raça/cor": "bar_chart",
    "Consulta 7 — Doses por fabricante em BH": "bar_chart"
}

EXPLICACOES_GRAFICOS = {
    "Consulta 1 — Cobertura Vacinal por Faixa Etária": "Este gráfico mostra a distribuição das vacinas por faixa etária. Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Consulta 2 — Vacinação por dia da semana": "Exibe os dias da semana com maior número de aplicações. Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Consulta 3 — Doses Aplicadas por Etnia Indígena": "Mostra a distribuição de vacinas entre diferentes etnias indígenas. Lorem ipsum dolor sit amet.",
    "Consulta 4 — Top Municípios com Maior Número de Doses Aplicadas": "Apresenta os 10 municípios com maior número de doses registradas. Lorem ipsum dolor sit amet.",
    "Consulta 5 — Locais Anatômicos Mais Utilizados": "Visualiza as partes do corpo onde as vacinas foram mais aplicadas. Lorem ipsum dolor.",
    "Consulta 6 — Total por raça/cor": "Distribuição da vacinação entre grupos raciais. Lorem ipsum dolor sit amet.",
    "Consulta 7 — Doses por fabricante em BH": "Mostra os fabricantes mais utilizados na cidade de Belo Horizonte. Lorem ipsum."
}

def main():
    st.set_page_config("TP2 - Visualização Vacinação", layout="wide")

    st.sidebar.title("Escolha a Consulta")
    opcao = st.sidebar.selectbox("Consulta", list(QUERIES.keys()))
    sql_base = QUERIES[opcao]

    st.title("Doses Aplicadas pelo Programa Nacional de Imunizações (PNI) em 2025")
    st.markdown(f"**Objetivo:** {DESCRICOES.get(opcao, 'Descrição não disponível.')}")

    st.subheader(opcao)
    with st.expander("📝Código SQL ", expanded=True):
        st.code(sql_base, language="sql")

    if "mostrar_consulta" not in st.session_state:
        st.session_state.mostrar_consulta = False

    def alternar_consulta():
        st.session_state.mostrar_consulta = not st.session_state.mostrar_consulta

    texto_botao = "🔽 Esconder consulta" if st.session_state.mostrar_consulta else "🔎 Exibir consulta"
    st.button(texto_botao, on_click=alternar_consulta)

    if st.session_state.mostrar_consulta:

        sql = sql_base  # padrão

        # Filtro de BH aplicado em consultas específicas
        if opcao == "Consulta 1 — Cobertura Vacinal por Faixa Etária":
            filtrar_bh = st.checkbox("Filtrar em BH")
            if filtrar_bh:
                sql = """
                    SELECT 
                        CASE 
                            WHEN idade < 12 THEN 'Crianças (0-11)' 
                            WHEN idade BETWEEN 12 AND 17 THEN 'Adolescentes (12-17)'
                            WHEN idade BETWEEN 18 AND 59 THEN 'Adultos (18-59)'
                            WHEN idade >= 60 THEN 'Idosos (60+)' 
                            ELSE 'Não Informado'
                        END AS faixa_etaria,
                        COUNT(*) AS total_aplicacoes
                    FROM Paciente
                    JOIN Aplicacao ON Paciente.id = Aplicacao.paciente_fk
                    JOIN Estabelecimento AS e ON Aplicacao.estabelecimento_fk = e.id
                    JOIN Municipio AS m ON e.municipio_fk = m.codigo
                    WHERE m.nome = 'BELO HORIZONTE'
                    GROUP BY faixa_etaria
                    ORDER BY total_aplicacoes DESC;
                """
        elif opcao == "Consulta 2 — Vacinação por dia da semana":
            filtrar_bh = st.checkbox("Filtrar em BH")
            if filtrar_bh:
                sql = """
                    SELECT 
                        CASE strftime('%w', data_aplicacao)
                            WHEN '0' THEN 'Domingo'
                            WHEN '1' THEN 'Segunda'
                            WHEN '2' THEN 'Terça'
                            WHEN '3' THEN 'Quarta'
                            WHEN '4' THEN 'Quinta'
                            WHEN '5' THEN 'Sexta'
                            WHEN '6' THEN 'Sábado'
                        END AS dia_semana,
                        COUNT(*) AS total_aplicacoes
                    FROM Aplicacao AS a
                    JOIN Estabelecimento AS e ON a.estabelecimento_fk = e.id
                    JOIN Municipio AS m ON e.municipio_fk = m.codigo
                    WHERE m.nome = 'BELO HORIZONTE'
                    GROUP BY dia_semana
                    ORDER BY total_aplicacoes DESC;
                """

        df = run_query(sql)
        st.dataframe(df, use_container_width=True)

        if opcao in CONSULTAS_COM_GRAFICO and df.shape[1] >= 2:
            st.subheader("📊 Gráfico")
            try:
                df = df.set_index(df.columns[0])
                st.bar_chart(df)
            except Exception as e:
                st.error(f"Erro ao exibir gráfico: {e}")

if __name__ == "__main__":
    main()
