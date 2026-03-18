import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Configurações de Identidade e Layout
st.set_page_config(page_title="DataPay Nexus | A.C. Camargo", layout="wide", page_icon="💰")

# --- UI/UX FUTURISTA PADRÃO v4.0 (Mantendo a Identidade Glassmorphism + MediumSpringGreen) ---
st.markdown(f"""
    <style>
    .stApp {{
        background: radial-gradient(circle at 20% 30%, #0d1b1a 0%, #050505 100%);
        color: #e0e0e0;
    }}
    [data-testid="stSidebar"] {{
        background-color: rgba(13, 27, 26, 0.98);
        border-right: 1px solid rgba(0, 250, 154, 0.2);
        backdrop-filter: blur(15px);
    }}
    label[data-baseweb="radio"] {{
        background: rgba(255, 255, 255, 0.03);
        padding: 15px !important; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid rgba(0, 250, 154, 0.1); width: 100%;
    }}
    div[data-testid="stMetricValue"] {{
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(0, 250, 154, 0.15);
        padding: 20px; border-radius: 15px; backdrop-filter: blur(10px);
    }}
    h1, h2, h3, h4, .stMetric label {{ color: #00FA9A !important; font-family: 'Inter', sans-serif; font-weight: 700; }}
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Suporte (Formatação Rigorosa BR)
def limpar_valor(val):
    if pd.isna(val) or val == ' ' or val == '' or val == '-': return 0.0
    try:
        s = str(val).replace('R$', '').replace(' ', '').replace('%', '')
        if ',' in s and '.' in s: s = s.replace('.', '').replace(',', '.')
        elif ',' in s: s = s.replace(',', '.')
        return float(s)
    except: return 0.0

def formatar_br(valor):
    """Garante o padrão 8.470,13"""
    return f"{valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def formatar_milhar(valor):
    return f"{int(valor):,}".replace(",", ".")

# --- 3. MENU LATERAL (Navegação Estruturada) ---
with st.sidebar:
    st.markdown("### 🏦 DataPay Nexus")
    st.markdown("---")
    menu = st.radio("Selecione a análise:", 
                    ["🎯 Adequação Salarial", 
                     "🗺️ Equidade Institucional", 
                     "📋 Benchmarking Geral", 
                     "🧮 Simulador de Ajustes"])
    st.markdown("---")
    st.caption("A.C. Camargo Cancer Center | 2026")

st.title("💰 Inteligência de Dados")
st.markdown(f"#### {menu}")
st.markdown("---")

file = st.file_uploader("📥 Carregue a base 'Cargos x Pesquisas' para iniciar", type=["xlsx", "csv"])

if file:
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file, encoding='latin1')

        # Busca Inteligente de Colunas (Blindagem v4.0)
        def find_col(possible_names, default_idx):
            for name in possible_names:
                for col in df.columns:
                    if name.lower() in str(col).lower(): return col
            return df.columns[default_idx] if default_idx < len(df.columns) else df.columns[0]

        col_dir, col_ger, col_car, col_qtd, col_gra, col_sal, col_mkt = (
            find_col(['Diretoria', 'Negócio'], 0), find_col(['Gerência', 'área'], 1),
            find_col(['Cargo'], 2), find_col(['Ocupante', 'Contagem', 'Qtd'], 3),
            find_col(['Grade'], 6), find_col(['R$ Médio', 'Salário Atual'], 8),
            find_col(['Compa-Ratio R$', 'Média Mercado', 'Consenso'], 34 if len(df.columns) > 34 else len(df.columns)-1)
        )

        # Processamento Geral
        df['qtd_clean'] = df[col_qtd].apply(limpar_valor).fillna(0).astype(int)
        df['ac_fixo'] = df[col_sal].apply(limpar_valor)
        df['mkt_fixo'] = df[col_mkt].apply(limpar_valor)
        df['cr_perc'] = np.where(df['mkt_fixo'] > 0, (df['ac_fixo'] / df['mkt_fixo']), 1)
        df['invest_mensal'] = np.where(df['mkt_fixo'] > df['ac_fixo'], (df['mkt_fixo'] - df['ac_fixo']) * df['qtd_clean'], 0)

        # --- LÓGICA DE PÁGINAS ---
        if menu == "🎯 Adequação Salarial":
            c1, c2, c3 = st.columns(3)
            df_al = df[(df['cr_perc'] < 0.8) & (df['mkt_fixo'] > 0)]
            c1.metric("Zona de Alerta (<80%)", f"{formatar_milhar(df_al['qtd_clean'].sum())} Pessoas")
            c2.metric("Ajuste Mensal (100% Mkt)", f"R$ {formatar_br(df['invest_mensal'].sum())}")
            c3.metric("Ajuste Anual (100% Mkt)", f"R$ {formatar_br(df['invest_mensal'].sum() * 13.33)}")
            st.dataframe(df[df['invest_mensal'] > 0].sort_values('invest_mensal', ascending=False).head(10), use_container_width=True)

        elif menu == "🗺️ Equidade Institucional":
            f1, f2, f3 = st.columns(3)
            with f1: sel_dir = st.selectbox("1. Diretoria", ["Todas"] + sorted(df[col_dir].dropna().unique().tolist()))
            df_f = df.copy() if sel_dir == "Todas" else df[df[col_dir] == sel_dir]
            with f2: sel_ger = st.selectbox("2. Gerência", ["Todas"] + sorted(df_f[col_ger].dropna().unique().tolist()))
            if sel_ger != "Todas": df_f = df_f[df_f[col_ger] == sel_ger]
            with f3: sel_car = st.selectbox("3. Cargo", ["Todos"] + sorted(df_f[col_car].dropna().unique().tolist()))
            if sel_car != "Todos": df_f = df_f[df_f[col_car] == sel_car]
            
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            cr_m = (df_f['ac_fixo'] * df_f['qtd_clean']).sum() / (df_f['mkt_fixo'] * df_f['qtd_clean']).sum() if (df_f['mkt_fixo'] * df_f['qtd_clean']).sum() > 0 else 0
            m1.metric("Compa-Ratio Médio", f"{cr_m*100:,.1f}%".replace(".", ","))
            m2.metric("Ocupantes", f"{formatar_milhar(df_f['qtd_clean'].sum())}")
            m3.metric("Ajuste da Seleção", f"R$ {formatar_br(df_f['invest_mensal'].sum())}")

        elif menu == "📋 Benchmarking Geral":
            tabela_final = df[[col_car, col_gra, col_qtd, col_sal, col_mkt]].copy()
            tabela_final.columns = ['Cargo', 'Grade', 'Ocupantes', 'Salário AC', 'Média Mercado']
            tabela_final['Salário AC'] = tabela_final['Salário AC'].apply(limpar_valor)
            tabela_final['Média Mercado'] = tabela_final['Média Mercado'].apply(limpar_valor)
            tabela_final['Compa-Ratio %'] = np.where(tabela_final['Média Mercado'] > 0, (tabela_final['Salário AC'] / tabela_final['Média Mercado']), 1)
            st.dataframe(tabela_final.style.format({
                'Salário AC': lambda x: f"R$ {formatar_br(x)}",
                'Média Mercado': lambda x: f"R$ {formatar_br(x)}",
                'Compa-Ratio %': lambda x: f"{x*100:,.1f}%".replace(".", ","),
                'Ocupantes': '{:d}'
            }), use_container_width=True, hide_index=True)

        elif menu == "🧮 Simulador de Ajustes":
            st.markdown("### 🧪 Simulador de Impacto em Remuneração")
            
            # --- SEÇÃO 1: FILTROS DE PÚBLICO ALVO ---
            st.markdown("#### 1. Qual público deseja ajustar?")
            c_p1, c_p2, c_p3 = st.columns(3)
            
            with c_p1:
                público_selecionado = st.radio("Critério de Competitividade", 
                                             ["Todos", "< 80% do Mkt", "80% - 90% do Mkt", "90% - 100% do Mkt", "> 100% do Mkt"], horizontal=True)
            
            with c_p2:
                dir_sim = st.multiselect("Diretoria Específica", options=sorted(df[col_dir].dropna().unique().tolist()))
            
            with c_p3:
                ger_sim = st.multiselect("Gerência Específica", options=sorted(df[col_ger].dropna().unique().tolist()))

            st.markdown("#### 2. Definir Parâmetro de Ajuste")
            c_aj1, c_aj2 = st.columns([2, 1])
            with c_aj1:
                tipo_ajuste = st.radio("Método de Reajuste", ["Trazer para Meta % do Mercado", "Aplicar Reajuste Linear (%)"], horizontal=True)
            with c_aj2:
                valor_input = st.number_input(f"Informe o {'% Alvo do Mercado' if 'Meta' in tipo_ajuste else '% de Reajuste Linear'}", value=100.0 if "Meta" in tipo_ajuste else 5.0)

            # --- PROCESSAMENTO DO CENÁRIO ---
            df_sim = df.copy()
            
            # Aplica Filtros de Diretoria/Gerência
            if dir_sim: df_sim = df_sim[df_sim[col_dir].isin(dir_sim)]
            if ger_sim: df_sim = df_sim[df_sim[col_ger].isin(ger_sim)]
            
            # Aplica Filtro de Público
            if público_selecionado == "< 80% do Mkt": df_sim = df_sim[df_sim['cr_perc'] < 0.8]
            elif público_selecionado == "80% - 90% do Mkt": df_sim = df_sim[(df_sim['cr_perc'] >= 0.8) & (df_sim['cr_perc'] < 0.9)]
            elif público_selecionado == "90% - 100% do Mkt": df_sim = df_sim[(df_sim['cr_perc'] >= 0.9) & (df_sim['cr_perc'] < 1.0)]
            elif público_selecionado == "> 100% do Mkt": df_sim = df_sim[df_sim['cr_perc'] >= 1.0]

            # Cálculo do Novo Salário
            if "Meta" in tipo_ajuste:
                df_sim['novo_salario'] = df_sim['mkt_fixo'] * (valor_input / 100)
                # Garante que ajuste só ocorra se o alvo for maior que o atual (opcional, mas estratégico)
                df_sim['novo_salario'] = np.where(df_sim['novo_salario'] > df_sim['ac_fixo'], df_sim['novo_salario'], df_sim['ac_fixo'])
            else:
                df_sim['novo_salario'] = df_sim['ac_fixo'] * (1 + (valor_input / 100))

            df_sim['ajuste_custo'] = (df_sim['novo_salario'] - df_sim['ac_fixo']) * df_sim['qtd_clean']
            
            st.markdown("---")
            # --- DASHBOARD DO CENÁRIO ---
            r1, r2, r3 = st.columns(3)
            r1.metric("Total de Impactados", f"{formatar_milhar(df_sim[df_sim['ajuste_custo'] > 0]['qtd_clean'].sum())} Pessoas")
            r2.metric("Investimento Mensal", f"R$ {formatar_br(df_sim['ajuste_custo'].sum())}")
            r3.metric("Ajuste Médio por Pessoa", f"R$ {formatar_br(df_sim['ajuste_custo'].sum() / df_sim['qtd_clean'].sum() if df_sim['qtd_clean'].sum() > 0 else 0)}")

            st.markdown(f"#### Detalhamento da Simulação")
            st.dataframe(pd.DataFrame({
                'Cargo': df_sim[col_car],
                'Atual': df_sim['ac_fixo'].apply(formatar_br),
                'Proposto': df_sim['novo_salario'].apply(formatar_br),
                'Ajuste %': ((df_sim['novo_salario'] / df_sim['ac_fixo'] - 1) * 100).map('{:,.1f}%'.format).str.replace(".", ","),
                'Impacto Mensal': df_sim['ajuste_custo'].apply(formatar_br)
            })[df_sim['ajuste_custo'] > 0], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"⚠️ Erro no processamento estratégico: {e}")
else:
    st.info("👋 Olá! Carregue a base consolidada para iniciar a navegação.")