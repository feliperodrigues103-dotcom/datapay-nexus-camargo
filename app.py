import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Configurações de Identidade e Layout
st.set_page_config(page_title="DataPay Nexus | A.C. Camargo", layout="wide", page_icon="💰")

# --- UI/UX v5.6 (Design Consolidado & Totalmente Blindado) ---
st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle at 20% 30%, #0d1b1a 0%, #050505 100%); color: #ffffff !important; }}
    [data-testid="stSidebar"] {{ background-color: rgba(13, 27, 26, 0.98); border-right: 1px solid rgba(0, 250, 154, 0.2); backdrop-filter: blur(15px); }}
    div[data-testid="stMetricValue"] {{ color: #00FA9A !important; font-size: clamp(1.1rem, 1.8vw, 1.6rem) !important; }}
    div[data-testid="stMetric"] {{ background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 250, 154, 0.2); padding: 20px; border-radius: 15px; }}
    h1, h2, h3, h4 {{ color: #ffffff !important; font-weight: 700; }}
    .stMetric label {{ color: #e0e0e0 !important; font-weight: 600; }}
    .custom-alert {{ background-color: rgba(233, 102, 102, 0.2); border: 1px solid #E96666; color: #ffffff; padding: 15px; border-radius: 10px; margin-bottom: 20px; }}
    .flash-card {{ background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 250, 154, 0.2); padding: 15px; border-radius: 15px; text-align: center; }}
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
    if valor == 0: return "-"
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def formatar_milhar(valor):
    return f"{int(valor):,}".replace(",", ".")

# --- 3. MENU LATERAL ---
with st.sidebar:
    st.success("✅ v5.6 - Homologação Final")
    st.markdown("### 🏦 DataPay Nexus")
    menu = st.radio("Navegação:", ["🎯 Adequação Salarial", "🗺️ Equidade Institucional", "📋 Benchmarking Geral", "🧮 Simulador de Ajustes"])

st.title("💰 Inteligência de Dados")
st.markdown(f"#### {menu}")
st.markdown("---")

file = st.file_uploader("📥 Carregue a base consolidada", type=["xlsx", "csv"])

if file:
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file, encoding='latin1')
        df.columns = [str(c).strip() for c in df.columns]

        # Mapeamento Centralizado
        def f_col(keywords, fallback):
            for k in keywords:
                for c in df.columns:
                    if k.lower() in c.lower(): return c
            return df.columns[fallback]

        c_dir, c_ger, c_car, c_qtd, c_gra, c_sal = f_col(['Diretoria'], 0), f_col(['Gerência'], 1), f_col(['Cargo'], 2), f_col(['Ocupante'], 3), f_col(['Grade'], 6), f_col(['Salário Atual', 'Média Salarial'], 8)
        c_mkt = f_col(['Compa-Ratio R$', 'Consenso', 'Média Mercado'], -1)

        # Processamento Principal
        df['qtd_clean'] = df[c_qtd].apply(limpar_valor).fillna(0).astype(int)
        df['ac_fixo'] = df[c_sal].apply(limpar_valor)
        df['mkt_fixo'] = df[c_mkt].apply(limpar_valor)
        df['cr_perc'] = np.where(df['mkt_fixo'] > 0, (df['ac_fixo'] / df['mkt_fixo']), 1.0)
        df['invest_mensal'] = np.where(df['mkt_fixo'] > df['ac_fixo'], (df['mkt_fixo'] - df['ac_fixo']) * df['qtd_clean'], 0.0)

        # --- ABA 1: ADEQUAÇÃO (CONGELADA) ---
        if menu == "🎯 Adequação Salarial":
            c1, c2, c3 = st.columns(3)
            df_al = df[(df['cr_perc'] < 0.8) & (df['mkt_fixo'] > 0)]
            c1.metric("Zona de Alerta (<80%)", f"{formatar_milhar(df_al['qtd_clean'].sum())} Pessoas")
            c2.metric("Ajuste Mensal Total", formatar_br(df['invest_mensal'].sum()))
            c3.metric("Ajuste Anual Projetado", formatar_br(df['invest_mensal'].sum() * 13.33))
            
            st.markdown("#### 📉 Diagnóstico de Necessidade de Investimento")
            df_diag = df[df['invest_mensal'] > 0].sort_values('invest_mensal', ascending=False).head(10).copy()
            tab_adeq = df_diag[[c_car, 'ac_fixo', 'mkt_fixo', 'cr_perc', 'qtd_clean', 'invest_mensal']]
            tab_adeq.columns = ['Cargo', 'Salário AC', 'Média Mercado', 'Compa-Ratio', 'Ocupantes', 'Investimento Mensal']
            st.dataframe(tab_adeq.style.format({'Salário AC': formatar_br, 'Média Mercado': formatar_br, 'Compa-Ratio': '{:.1%}'.format, 'Investimento Mensal': formatar_br}), use_container_width=True, hide_index=True)

        # --- ABA 2: EQUIDADE (CONGELADA) ---
        elif menu == "🗺️ Equidade Institucional":
            f1, f2, f3 = st.columns(3)
            with f1: sel_dir = st.selectbox("Diretoria", ["Todas"] + sorted(df[c_dir].dropna().unique().tolist()))
            df_f = df.copy() if sel_dir == "Todas" else df[df[c_dir] == sel_dir]
            with f2: sel_ger = st.selectbox("Gerência", ["Todas"] + sorted(df_f[c_ger].dropna().unique().tolist()))
            if sel_ger != "Todas": df_f = df_f[df_f[c_ger] == sel_ger]
            with f3: sel_car = st.selectbox("Cargo", ["Todos"] + sorted(df_f[c_car].dropna().unique().tolist()))
            if sel_car != "Todos": df_f = df_f[df_f[c_car] == sel_car]

            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            cr_area = (df_f['ac_fixo'] * df_f['qtd_clean']).sum() / (df_f['mkt_fixo'] * df_f['qtd_clean']).sum() if (df_f['mkt_fixo'] * df_f['qtd_clean']).sum() > 0 else 0
            m1.metric("Compa-Ratio Médio", f"{cr_area*100:,.1f}%".replace(".", ","))
            m2.metric("Gap de Investimento Mensal", formatar_br(df_f['invest_mensal'].sum()))
            m3.metric("Pessoas em Alerta", formatar_milhar(df_f[df_f['cr_perc'] < 0.8]['qtd_clean'].sum()))
            m4.metric("Total de Ocupantes", formatar_milhar(df_f['qtd_clean'].sum()))

            target_col = c_dir if sel_dir == "Todas" else (c_ger if sel_ger == "Todas" else c_car)
            chart_data = df_f.groupby(target_col).apply(lambda x: (x['ac_fixo']*x['qtd_clean']).sum() / (x['mkt_fixo']*x['qtd_clean']).sum()).reset_index(name='CR').sort_values('CR')
            chart_data_clean = chart_data[chart_data['CR'] <= 1.5]
            outliers = chart_data[chart_data['CR'] > 1.5]
            
            fig = px.bar(chart_data_clean, x='CR', y=target_col, orientation='h', color='CR', color_continuous_scale=['#FF4B4B', '#00FA9A'], text=chart_data_clean['CR'].apply(lambda x: f"{x*100:,.1f}%".replace(".", ",")))
            fig.update_traces(textposition='auto', textfont_color='black')
            fig.update_layout(coloraxis_showscale=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=max(400, len(chart_data_clean)*40))
            st.plotly_chart(fig, use_container_width=True)

            if not outliers.empty:
                st.markdown(f'<div class="custom-alert">⚠️ <b>Atenção:</b> Desvios extremos detectados (>150% CR).</div>', unsafe_allow_html=True)
                with st.expander("Ver anomalias"): st.dataframe(outliers.style.format({'CR': '{:.1%}'.format}), use_container_width=True, hide_index=True)

        # --- ABA 3: BENCHMARKING (REFINE FINAL) ---
        elif menu == "📋 Benchmarking Geral":
            st.markdown("### 📋 Tabela Mestra de Pesquisas")
            search = st.text_input("🔍 Buscar Cargo ou Diretoria:", "")
            
            # Listagem de pesquisas
            cols_ana = [c for c in df.columns if 'ANAHP' in c.upper()]
            cols_kf = [c for c in df.columns if 'KF' in c.upper()]
            cols_g7 = [c for c in df.columns if 'G7' in c.upper()]
            cols_xr = [c for c in df.columns if 'XR' in c.upper()]
            
            df_b = df[[c_car, c_dir, c_gra, 'qtd_clean', 'ac_fixo', 'mkt_fixo', 'cr_perc']].copy()
            df_b = pd.concat([df_b, df[cols_ana + cols_kf + cols_g7 + cols_xr]], axis=1)

            # Lógica das Setas
            def trend_icon(survey_val, ac_val):
                s_val = limpar_valor(survey_val)
                a_val = limpar_valor(ac_val)
                if s_val == 0 or a_val == 0: return ""
                return " 🟢↑" if s_val > a_val else " 🔴↓"

            # Formatação Dinâmica de Colunas (v5.6)
            dict_format = {'Salário AC': formatar_br, 'Média Mercado': formatar_br, 'cr_perc': '{:.1%}'.format, 'qtd_clean': '{:d}'}
            
            for c in df_b.columns:
                # 1. Código de Cargos (Remoção de .000000)
                if 'CÓD' in c.upper() or 'COD' in c.upper():
                    df_b[c] = df_b[c].apply(lambda x: str(int(limpar_valor(x))) if limpar_valor(x) > 0 else "-")
                # 2. Carga Horária (Inteiro)
                elif 'CH' in c.upper():
                    dict_format[c] = lambda x: f"{int(limpar_valor(x))}" if limpar_valor(x) > 0 else "-"
                # 3. Salário Base e Total Comp (Moeda)
                elif 'R$' in c.upper():
                    df_b[c] = df_b.apply(lambda row: f"{formatar_br(limpar_valor(row[c]))}{trend_icon(row[c], row['ac_fixo'])}" if 'SB' in c.upper() else formatar_br(limpar_valor(row[c])), axis=1)
                # 4. Percentuais
                elif '%' in c.upper():
                    dict_format[c] = lambda x: f"{limpar_valor(x)*100:,.1%}".replace(".", ",")

            df_b = df_b.rename(columns={'qtd_clean': 'Ocupantes', 'ac_fixo': 'Salário AC', 'mkt_fixo': 'Média Mercado', 'cr_perc': 'Compa-Ratio'})

            if search:
                df_b = df_b[df_b['Cargo'].str.contains(search, case=False) | df_b['Diretoria'].str.contains(search, case=False)]

            st.dataframe(df_b.style.format(dict_format), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro v5.6: {e}")
else:
    st.info("👋 Cockpit Pronto. Carregue o arquivo.")
