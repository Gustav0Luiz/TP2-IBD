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
    "Consulta 3 — Top Municípios com Maior Número de Doses Aplicadas": """
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

    "Consulta 4 — Locais Anatômicos Mais Utilizados": """
        SELECT 
            l.descricao AS local_anatomico,
            COUNT(*) AS total_aplicacoes
        FROM Aplicacao AS a
        JOIN LocalAplicacao AS l ON a.local_aplicacao_fk = l.codigo
        WHERE l.descricao != 'Sem registro no sistema de informação de origem' 
        GROUP BY l.descricao
        ORDER BY total_aplicacoes DESC
        LIMIT 15;
    """,
}

DESCRICOES = {
    "Consulta 1 — Cobertura Vacinal por Faixa Etária": "Avalia o alcance da vacinação em diferentes faixas etárias.",
    "Consulta 2 — Vacinação por dia da semana": "Exibe em quais dias da semana ocorrem mais aplicações.",
    "Consulta 3 — Top Municípios com Maior Número de Doses Aplicadas": "Mostra os municípios com mais vacinações registradas.",
    "Consulta 4 — Locais Anatômicos Mais Utilizados": "Indica os locais do corpo mais utilizados nas aplicações."

}

@st.cache_data(ttl=600)
def run_query(sql):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn)

CONSULTAS_COM_GRAFICO = {
    "Consulta 1 — Cobertura Vacinal por Faixa Etária": "bar_chart",
    "Consulta 2 — Vacinação por dia da semana": "bar_chart",
    "Consulta 3 — Top Municípios com Maior Número de Doses Aplicadas": "bar_chart",
    "Consulta 4 — Locais Anatômicos Mais Utilizados": "bar_chart",
}

EXPLICACOES_GRAFICOS = {
    "Consulta 1 — Cobertura Vacinal por Faixa Etária": """
        Este gráfico apresenta a distribuição das vacinas aplicadas por faixa etária. As faixas etárias são definidas como:
        - Crianças (0-11 anos)
        - Adolescentes (12-17 anos)
        - Adultos (18-59 anos)
        - Idosos (60 anos ou mais)

        Cada barra do gráfico representa o número total de doses aplicadas para cada faixa etária. A análise da distribuição pode nos fornecer informações importantes sobre a cobertura vacinal em diferentes grupos da população.

        A partir da visualização, podemos observar que a maioria das vacinas aplicadas estão concentradas nas faixas de Crianças e Adultos. Isso pode indicar um foco maior na imunização infantil e adulta, provavelmente devido à prevalência de campanhas de vacinação para esses grupos. 

        Essa análise pode ser útil para planejar futuras campanhas de vacinação e direcionar esforços para grupos com menor cobertura vacinal, caso seja o caso.
    """,
    
        "Consulta 2 — Vacinação por dia da semana": """
            Este gráfico apresenta o número total de vacinas aplicadas em cada dia da semana. A distribuição dos dados permite analisar 
            a variabilidade no volume de vacinação ao longo da semana, ajudando a identificar os dias com maior movimentação de vacinação.

            Observa-se que a maior parte das vacinas são aplicadas durante os dias úteis da semana, de segunda a sexta-feira. Por outro lado, os fins de semana (sábado e domingo) apresentam um número muito menor de aplicações. 

            Essa tendência sugere que a vacinação pode ocorrer predominantemente de segunda a sexta-feira, com uma possível pausa ou redução nas atividades de vacinação durante o fim de semana.

            A análise dessa distribuição é importante para o planejamento logístico de campanhas de vacinação, podendo indicar a necessidade de ajustar os dias de aplicação para atingir a população de maneira mais eficiente, especialmente considerando possíveis filas ou horários de pico.
        """,

        "Consulta 3 — Top Municípios com Maior Número de Doses Aplicadas": """
            Este gráfico apresenta os 10 municípios com o maior número de doses aplicadas, permitindo uma visualização clara das regiões 
            com maior cobertura vacinal.

            A análise mostra que os estados de São Paulo (SP), Rio de Janeiro (RJ) e o município de Manaus se destacam com o maior número 
            de doses aplicadas. É interessante notar a presença de Manaus entre os líderes, o que pode surpreender, considerando que 
            outras regiões com maior população ou maior infraestrutura de saúde não aparecem no topo. Essa informação sugere que o programa 
            de vacinação em Manaus tem sido muito eficaz, e a cidade pode ter implementado estratégias inovadoras ou enfrentado condições 
            específicas que exigiram uma grande mobilização para alcançar a população.

            Essa análise pode ajudar a entender como as campanhas de vacinação estão sendo distribuídas geograficamente e identificar quais 
            municípios estão alcançando um maior sucesso na imunização da população. Também pode indicar a necessidade de ajustar os recursos 
            e esforços em regiões que não estão representadas entre os municípios com maior cobertura vacinal.
        """,

        "Consulta 4 — Locais Anatômicos Mais Utilizados": """
            Este gráfico apresenta os locais anatômicos mais comuns para a aplicação das vacinas, destacando os pontos mais frequentes 
            onde as injeções são administradas.

            A análise mostra que o Deltóide é o local mais utilizado, seguido pelas coxas. Esses locais são preferidos provavelmente devido à facilidade de acesso e maior volume de músculo, 
            que facilita a administração da vacina.

            Um outro local comum é na boca, que é o mais utilizado após braços e pernas.

            A distribuição dos locais anatômicos pode fornecer insights sobre os métodos preferidos de aplicação.
        """,
        "Consulta 5 — Estabelecimentos de saude": """
            Este gráfico apresenta os locais anatômicos mais comuns para a aplicação das vacinas, destacando os pontos mais frequentes 
            onde as injeções são administradas.

            A análise mostra que o Deltóide é o local mais utilizado, seguido pelas coxas. Esses locais são preferidos provavelmente devido à facilidade de acesso e maior volume de músculo, 
            que facilita a administração da vacina.

            Um outro local comum é na boca, que é o mais utilizado após braços e pernas.

            A distribuição dos locais anatômicos pode fornecer insights sobre os métodos preferidos de aplicação.
        """,

}

def main():
    st.set_page_config("TP2 - Visualização Vacinação", layout="wide")

    # Usando uma chave única para o selectbox
    st.sidebar.title("Escolha a Consulta")
    opcao = st.sidebar.selectbox("Consulta", list(QUERIES.keys()), key="consulta_selectbox")
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

                # Exibe o texto explicativo
                st.subheader("Análise do Gráfico")
                st.write(EXPLICACOES_GRAFICOS[opcao])
            except Exception as e:
                st.error(f"Erro ao exibir gráfico: {e}")

if __name__ == "__main__":
    main()


