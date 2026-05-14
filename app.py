import streamlit as st
import pandas as pd
import os

# 1. Configuração de Página
st.set_page_config(page_title="Painel de Remuneração de Jetons", layout="wide")

# 2. Customização de Cores (Azul nas seleções)
st.markdown("""
    <style>
    span[data-baseweb="tag"] {
        background-color: #1f77b4 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Função de Carga e Limpeza


@st.cache_data
def load_data():
    caminho_dados = os.path.join('dados', 'base_jeton_2025_2026.csv')
    if not os.path.exists(caminho_dados):
        return pd.DataFrame()

    df = pd.read_csv(caminho_dados, sep=';', encoding='latin1')

    if 'Jetons Pagos' in df.columns:
        def converter_valor(val):
            if pd.isnull(val):
                return 0.0
            if isinstance(val, (int, float)):
                return float(val)
            v = str(val).strip().replace('.', '').replace(',', '.')
            try:
                return float(v)
            except:
                return 0.0
        df['Jetons Pagos'] = df['Jetons Pagos'].apply(converter_valor)
    return df


df = load_data()

# 4. Inicialização de Estados (Menu e Filtros)
# Definimos as variáveis possíveis para a tabela
colunas_possiveis = ['Mês - descritivo', 'Ano', 'Servidor', 'Empresa - Sigla']
colunas_reais = [c for c in colunas_possiveis if c in df.columns]

if "menu_selecionado" not in st.session_state:
    st.session_state.menu_selecionado = colunas_reais  # Inicia com todas selecionadas

if "f_nome" not in st.session_state:
    st.session_state.f_nome = ""
if "f_ano" not in st.session_state:
    st.session_state.f_ano = []
if "f_mes" not in st.session_state:
    st.session_state.f_mes = []
if "f_emp" not in st.session_state:
    st.session_state.f_emp = []


def limpar_tudo():
    st.session_state.f_nome = ""
    st.session_state.f_ano = []
    st.session_state.f_mes = []
    st.session_state.f_emp = []


# 5. Barra Lateral
st.sidebar.header("Filtros de Pesquisa")
st.sidebar.button("🧹 Limpar Filtros", on_click=limpar_tudo,
                  use_container_width=True)
st.sidebar.markdown("---")

busca = st.sidebar.text_input("🔍 Servidor:", key="f_nome")
anos_sel = st.sidebar.multiselect("Ano:", options=sorted(
    df['Ano'].unique()) if 'Ano' in df.columns else [], key="f_ano")
meses_sel = st.sidebar.multiselect("Mês:", options=df['Mês - descritivo'].unique(
) if 'Mês - descritivo' in df.columns else [], key="f_mes")
emp_sel = st.sidebar.multiselect("Empresa:", options=sorted(
    df['Empresa - Sigla'].unique()) if 'Empresa - Sigla' in df.columns else [], key="f_emp")

# Aplicar Filtros
df_f = df.copy()
if anos_sel:
    df_f = df_f[df_f['Ano'].isin(anos_sel)]
if meses_sel:
    df_f = df_f[df_f['Mês - descritivo'].isin(meses_sel)]
if emp_sel:
    df_f = df_f[df_f['Empresa - Sigla'].isin(emp_sel)]
if busca:
    df_f = df_f[df_f['Servidor'].str.contains(busca, case=False, na=False)]

# 6. Área Principal
st.subheader("Painel Dinâmico de Jetons Pagos")

# Menu Dinâmico com todas as variáveis selecionadas por padrão
selecao_colunas = st.multiselect(
    "Variáveis de exibição (Jetons Pagos é fixo):",
    options=colunas_reais,
    key="menu_selecionado"
)

st.divider()

if selecao_colunas:
    # Agrupamento
    df_resumo = df_f.groupby(selecao_colunas, as_index=False)[
        'Jetons Pagos'].sum()

    # ORDENAÇÃO NUMÉRICA (Essencial para o Gustavo Barbosa ficar no topo)
    df_resumo = df_resumo.sort_values(by='Jetons Pagos', ascending=False)

    # FORMATAÇÃO BRASILEIRA (Forçando ponto no milhar e vírgula no decimal)
    def formatar_br(valor):
        # Gera R$ 391,600.79 -> Troca para R$ 391.600,79
        texto = f"R$ {valor:,.2f}"
        return texto.replace(',', 'X').replace('.', ',').replace('X', '.')

    df_resumo['Jetons Pagos'] = df_resumo['Jetons Pagos'].apply(formatar_br)

    # Exibição
    st.dataframe(df_resumo, use_container_width=True, hide_index=True)

    # Total Geral no rodapé
    total = df_f['Jetons Pagos'].sum()
    st.info(f"**Total na seleção atual:** {formatar_br(total)}")
else:
    st.warning("Selecione variáveis no menu acima para compor a tabela.")
