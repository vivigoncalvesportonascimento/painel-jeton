import streamlit as st
import pandas as pd
import os

# Configuração inicial da página
st.set_page_config(page_title="Painel de Remuneração de Jetons", layout="wide")

# Função para carregar os dados considerando o caminho relativo no repositório


@st.cache_data
def load_data():
    # Caminho ajustado para a pasta 'dados' conforme solicitado
    caminho_dados = os.path.join('dados', 'base_jeton_2025_2026.csv')

    if not os.path.exists(caminho_dados):
        st.error(
            f"Arquivo não encontrado em: {caminho_dados}. Verifique se a pasta e o arquivo existem no repositório.")
        return pd.DataFrame()

    # Lê o arquivo CSV consolidado (separador ponto e vírgula)
    df = pd.read_csv(caminho_dados, sep=';', encoding='utf-8-sig')

    # Tratamento da coluna 'Jetons Pagos' para garantir cálculos numéricos
    if 'Jetons Pagos' in df.columns and df['Jetons Pagos'].dtype == 'O':
        df['Jetons Pagos'] = (
            df['Jetons Pagos']
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )
    return df


df = load_data()

if not df.empty:
    # ==========================================
    # BARRA LATERAL (SIDEBAR) - FILTROS E BUSCA
    # ==========================================
    st.sidebar.header("Filtros de Pesquisa")

    # Campo de busca por nome do Servidor
    busca_nome = st.sidebar.text_input("🔍 Buscar por Nome do Servidor:")

    # Filtros Multi-seleção
    anos = st.sidebar.multiselect(
        "Ano",
        options=sorted(df['Ano'].dropna().unique()),
        default=sorted(df['Ano'].dropna().unique())
    )

    meses = st.sidebar.multiselect(
        "Mês - descritivo",
        options=df['Mês - descritivo'].dropna().unique(),
        default=df['Mês - descritivo'].dropna().unique()
    )

    empresas = st.sidebar.multiselect(
        "Empresa - Sigla",
        options=sorted(df['Empresa - Sigla'].dropna().unique()),
        default=sorted(df['Empresa - Sigla'].dropna().unique())
    )

    # Aplicando os filtros no DataFrame
    df_filtered = df.copy()

    if anos:
        df_filtered = df_filtered[df_filtered['Ano'].isin(anos)]
    if meses:
        df_filtered = df_filtered[df_filtered['Mês - descritivo'].isin(meses)]
    if empresas:
        df_filtered = df_filtered[df_filtered['Empresa - Sigla'].isin(
            empresas)]
    if busca_nome:
        df_filtered = df_filtered[df_filtered['Servidor'].str.contains(
            busca_nome, case=False, na=False)]

    # ==========================================
    # ÁREA PRINCIPAL - MENU DINÂMICO E TABELA
    # ==========================================
    st.title("📊 Painel Dinâmico de Jetons Pagos")

    st.markdown("""
    Utilize o menu abaixo para compor a visão da tabela. O campo **Jetons Pagos** será consolidado 
    automaticamente conforme os parâmetros selecionados.
    """)

    # Variáveis disponíveis para o usuário escolher
    variaveis_disponiveis = ['Mês - descritivo',
                             'Ano', 'Servidor', 'Empresa - Sigla']

    # Menu dinâmico de seleção de colunas (acima da tabela)
    colunas_selecionadas = st.multiselect(
        "Selecione as variáveis para agrupamento:",
        options=variaveis_disponiveis,
        default=['Ano', 'Empresa - Sigla']
    )

    st.divider()

    if colunas_selecionadas:
        # Agrupamento dinâmico
        df_agrupado = df_filtered.groupby(colunas_selecionadas, as_index=False)[
            'Jetons Pagos'].sum()
        df_agrupado = df_agrupado.sort_values(by=colunas_selecionadas)

        # Formatação para moeda brasileira (R$)
        df_agrupado['Valor Formatado'] = df_agrupado['Jetons Pagos'].apply(
            lambda x: f"R$ {x:,.2f}".replace(
                ',', 'X').replace('.', ',').replace('X', '.')
        )

        # Exibição da tabela dinâmica
        df_display = df_agrupado.drop(columns=['Jetons Pagos']).rename(
            columns={'Valor Formatado': 'Jetons Pagos'})
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Resumo métrico
        total_selecao = df_filtered['Jetons Pagos'].sum()
        st.info(f"**Total acumulado na seleção:** R$ {total_selecao:,.2f}".replace(
            ',', 'X').replace('.', ',').replace('X', '.'))
    else:
        st.warning(
            "⚠️ Selecione pelo menos uma variável no menu acima para visualizar os dados.")
