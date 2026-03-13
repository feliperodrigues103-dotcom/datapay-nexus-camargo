import streamlit as st
import pandas as pd
import plotly.express as px
import io
import re
import unicodedata
from fpdf import FPDF

# 1. Configurações de Identidade
st.set_page_config(page_title="DataPay Nexus", layout="wide", page_icon="💰")

# --- CSS DE ALTA TECNOLOGIA (GLASSMORPHISM & NEON) ---
st.markdown("""
    <style>
    /* Fundo Profundo e Imersivo */
    .stApp {
        background: radial-gradient(circle at top right, #0d1b1a, #050505);
    }
    
    /* Customização das Abas (Modern Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255, 255, 255, 0.03) !important;
        border-radius: 10px 10px 0px 0px !important;
        color: white !important;
        border: 1px solid rgba(0, 250, 154, 0.1) !important;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(0, 250, 154, 0.1) !important;
        border: 1px solid #00FA9A !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 250, 154, 0.15) !important;
        border-bottom: 3px solid #00FA9A !important;
        box-shadow: 0px 5px 15px rgba(0, 250, 154, 0.2);
    }

    /* Cards de Métricas (Glass Effect) */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(0, 250, 154, 0.2);
        padding: 20px !important;
        border-radius: 15px;
        backdrop-filter: blur(12px);
        transition: transform 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #00FA9A;
        box-shadow: 0px 10px 30px rgba(0, 250, 154, 0.15);
    }
    [data-testid="stMetricValue"] {
        color: #00FA9A !important;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0px 0px 10px rgba(0, 250, 154, 0.5);
    }

    /* Sliders e Botões Neon */
    .stSlider [data-testid="stThumb"] { background-color: #00FA9A !important; border: 2px solid #7FFFD4 !important; }
    .stSlider [data-baseweb="slider"] > div > div { background: linear-gradient(90deg, #00FA9A, #7FFFD4) !important; }
    
    .stButton>button {
        background: rgba(0, 250, 154, 0.1) !important;
        color: #00FA9A !important;
        border: 1px solid #00FA9A !important;
        border-radius: 8px !important;
        transition: all 0.4s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background: #00FA9A !important;
        color: #050505 !important;
        box-shadow: 0px 0px 20px rgba(0, 250, 154, 0.4);
    }

    /* Ajustes Gerais */
    h1, h2, h3 { color: #f0f0f0 !important; font-weight: 300 !important; letter-spacing: -0.5px; }
    .stCaption { color: #7FFFD4 !important; opacity: 0.8; }
    
    /* Tabela Sofisticada */
    .stDataFrame { border: 1px solid rgba(127, 255, 212, 0.1) !important; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES CORE (PRESERVADAS) ---
def limpar_para_pdf(texto):
    if pd.isna(texto): return ""
    subst = {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ã':'a','õ':'o','â':'a','ê':'e','ô':'o','ç':'c','Á':'A','É':'E','Í':'I','Ó':'O','Ú':'U','Ã':'A','Õ':'O','Â':'A','Ê':'E','Ô':'O','Ç':'C'}
    texto = str(texto).replace('R$', 'RS')
    for k,v in subst.items(): texto = texto.replace(k,v)
    return re.sub(r'[^a-zA-Z0-9\s\.\,\-\/\:]', '', texto)

def gerar_pdf_bytes(df_pdf):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(190, 10, "DataPay Nexus - Inteligencia Salarial", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 10)
    for _, row in df_pdf.head(60).iterrows():
        pdf.cell(100, 8, limpar_para_pdf(row['Cargo']), border=1)
        pdf.cell(45, 8, f"RS {row['Novo Salário']:,.2f}", border=1, align='C')
        pdf.cell(45, 8, limpar_para_pdf(row['Novo Status']), border=1)
        pdf.ln()
    return bytes(pdf.output())

def definir_status(ratio):
    if pd.isna(ratio) or ratio == 0: return "Sem Dados"
    if ratio < 0.80: return "🔴 Abaixo do Piso"
    elif 0.80 <= ratio < 0.95: return "🟡 Entrada"
    elif 0.95 <= ratio <= 1.05: return "🟢 Alinhado"
    elif 1.05 < ratio <= 1.20: return "🔵 Senior/Retencao"
    else: return "🟣 Acima do Teto"

# --- FLUXO DE DADOS ---
st.title("💰 DataPay Nexus")
st.caption("Advanced Remuneration Intelligence | A.C. Camargo Cancer Center")

arquivo = st.file_uploader("", type=["xlsx", "csv"]) # Uploader minimalista

if arquivo:
    df_raw = pd.read_excel(arquivo) if arquivo.name.endswith('.xlsx') else pd.read_csv(arquivo)
    
    # Busca de Cabeçalho Inteligente
    if "Negócio" not in df_raw.columns:
        for i in range(min(10, len(df_raw))):
            if "Negócio" in df_raw.iloc[i].values:
                df_raw.columns = df_raw.iloc[i]; df_raw = df_raw[i+1:].reset_index(drop=True); break

    cols_ok = ['Negócio', 'Cargo', 'R$ Médio', 'Mediana Pesquisas R$']
    if all(c in df_raw.columns for c in cols_ok):
        for c in ['R$ Médio', 'Mediana Pesquisas R$']: df_raw[c] = pd.to_numeric(df_raw[c], errors='coerce')
        df_base = df_raw.dropna(subset=['Negócio', 'R$ Médio', 'Mediana Pesquisas R$']).copy()
        df_base['Compa-Ratio'] = df_base['R$ Médio'] / df_base['Mediana Pesquisas R$']
        df_base['Status'] = df_base['Compa-Ratio'].apply(definir_status)
        df_base['Gap R$'] = df_base.apply(lambda x: max(0, x['Mediana Pesquisas R$'] - x['R$ Médio']), axis=1)

        # Filtros no Sidebar (Estilo Dark)
        st.sidebar.markdown("### 🎯 Central de Filtros")
        sel_dir = st.sidebar.multiselect("Selecionar Diretoria", sorted(df_base['Negócio'].unique().astype(str)))
        df = df_base[df_base['Negócio'].isin(sel_dir)] if sel_dir else df_base

        # Tabs com Estilo Moderno
        t1, t2, t3 = st.tabs(["📊 VISION", "📋 INTEL", "💰 SIMULATOR"])

        with t1:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Cargos Ativos", len(df))
            with c2: st.metric("Market Fit (CR)", f"{df['Compa-Ratio'].mean():.1%}")
            with c3: st.metric("Gap Orçamentário", f"R$ {df['Gap R$'].sum():,.0f}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_a, col_b = st.columns([1, 1.5])
            with col_a: 
                fig_pie = px.pie(df, names='Status', hole=0.5, color_discrete_sequence=px.colors.sequential.Mint)
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_b: 
                df_bar = df.groupby('Negócio')['Gap R$'].sum().reset_index().sort_values('Gap R$')
                fig_bar = px.bar(df_bar, x='Gap R$', y='Negócio', orientation='h', color_discrete_sequence=['#00FA9A'])
                fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig_bar, use_container_width=True)

        with t2:
            st.markdown("### 📋 Tabela de Inteligência Salarial")
            st.dataframe(df[['Negócio', 'área', 'Cargo', 'R$ Médio', 'Mediana Pesquisas R$', 'Compa-Ratio', 'Status']], 
                         column_config={"R$ Médio": st.column_config.NumberColumn(format="R$ %.2f"),
                                        "Mediana Pesquisas R$": st.column_config.NumberColumn(format="R$ %.2f"),
                                        "Compa-Ratio": st.column_config.NumberColumn(format="%.1%"),},
                         use_container_width=True, hide_index=True)

        with t3:
            st.markdown("### 💰 Simulador de Cenários")
            perc = st.slider("", 0.0, 30.0, 0.0) / 100
            df_sim = df.copy()
            df_sim['Novo Salário'] = df_sim['R$ Médio'] * (1 + perc)
            df_sim['Novo Status'] = (df_sim['Novo Salário'] / df_sim['Mediana Pesquisas R$']).apply(definir_status)
            
            # Alerta Estilizado
            st.info(f"🌿 IMPACTO MENSAL: R$ {(df_sim['Novo Salário'] - df_sim['R$ Médio']).sum():,.2f}  |  ANUAL (13º): R$ {(df_sim['Novo Salário'] - df_sim['R$ Médio']).sum()*13:,.2f}")
            
            col_bt1, col_bt2, _ = st.columns([1,1,2])
            with col_bt1: st.download_button("📥 Excel", data=df_sim.to_csv().encode('utf-8'), file_name="datapay_nexus.csv")
            with col_bt2: st.download_button("📄 PDF", data=gerar_pdf_bytes(df_sim), file_name="relatorio.pdf")

            st.dataframe(df_sim[['Cargo', 'R$ Médio', 'Novo Salário', 'Novo Status']], use_container_width=True, hide_index=True)

else:
    st.markdown("<h3 style='text-align:center; opacity:0.5;'>Nexus System Offline. Waiting for Salary Base...</h3>", unsafe_allow_html=True)