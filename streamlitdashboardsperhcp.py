import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="SPER & HCP - Dashboard de Registos e Pagamentos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .custom-header {
        background: white;
        border-radius: 15px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-top: 5px solid #10b981;
    }
    .custom-header h1 {
        color: #059669;
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    .custom-header .date {
        color: #666;
        font-size: 1.1em;
    }
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-left: 5px solid;
        margin-bottom: 20px;
    }
    .stat-card h3 {
        color: #666;
        font-size: 0.9em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .stat-card .value {
        font-size: 2.5em;
        font-weight: bold;
        color: #059669;
        margin-bottom: 5px;
    }
    .stat-card .subtitle {
        color: #999;
        font-size: 0.9em;
    }
    .filter-section {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-top: 3px solid #10b981;
    }
    .custom-table-container {
        background: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        overflow-x: auto;
    }
    .total-row {
        background-color: #f0fdf4;
        font-weight: bold;
        border-top: 2px solid #10b981;
    }
    .provincia-total {
        background-color: #fef3c7;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="custom-header">
    <h1>📊 SPER & HCP Moçambique 2026 - Monitoria de Registos e Pagamentos</h1>
    <p class="date">Registos e Pagamentos - Actualizado a 26-04-2026</p>
</div>
""", unsafe_allow_html=True)

# Load data from Excel file
@st.cache_data
def load_data():
    # Read the Excel file
    file_path = 'SPER and HCP_R&P streamlit dash.xlsx'
    
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
    except:
        try:
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
        except:
            st.error(f"Arquivo não encontrado: {file_path}")
            return pd.DataFrame()
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Create a clean dataframe
    clean_data = []
    
    for _, row in df.iterrows():
        provincia = row.get('provincia', '')
        delegacao = row.get('delegacao', '')
        distrito = row.get('distrito', '')
        
        # Get metas
        metas_col = None
        for col in ['metas_distrito', 'metas']:
            if col in df.columns:
                metas_col = col
                break
        
        metas = row.get(metas_col, 0) if metas_col else 0
        if isinstance(metas, str):
            metas = metas.replace('"', '').replace(',', '')
            try:
                metas = float(metas)
            except:
                metas = 0
        
        # Get registos values
        total_registos = 0
        mpesa_abertas = 0
        registos_sib = 0
        fora_rede = 0
        
        if 'total_registos' in df.columns:
            total_registos = row.get('total_registos', 0)
        elif 'Total Registos' in df.columns:
            total_registos = row.get('Total Registos', 0)
        
        if 'mpesa_abertas' in df.columns:
            mpesa_abertas = row.get('mpesa_abertas', 0)
        elif 'Mpesa Abertas' in df.columns:
            mpesa_abertas = row.get('Mpesa Abertas', 0)
        
        if 'registos_no_sib' in df.columns:
            registos_sib = row.get('registos_no_sib', 0)
        elif 'Registos SIB' in df.columns:
            registos_sib = row.get('Registos SIB', 0)
        
        if 'fora_rede' in df.columns:
            fora_rede = row.get('fora_rede', 0)
        elif 'Fora Rede' in df.columns:
            fora_rede = row.get('Fora Rede', 0)
        
        # Convert to numeric
        try:
            total_registos = float(total_registos) if pd.notna(total_registos) else 0
            mpesa_abertas = float(mpesa_abertas) if pd.notna(mpesa_abertas) else 0
            registos_sib = float(registos_sib) if pd.notna(registos_sib) else 0
            fora_rede = float(fora_rede) if pd.notna(fora_rede) else 0
        except:
            total_registos = 0
            mpesa_abertas = 0
            registos_sib = 0
            fora_rede = 0
        
        # Get pagamentos
        beneficiarios_pagos = 0
        if 'Beneficiários pagos' in df.columns:
            beneficiarios_pagos = row.get('Beneficiários pagos', 0)
        elif 'beneficiarios_pagos' in df.columns:
            beneficiarios_pagos = row.get('beneficiarios_pagos', 0)
        
        try:
            beneficiarios_pagos = float(beneficiarios_pagos) if pd.notna(beneficiarios_pagos) else 0
        except:
            beneficiarios_pagos = 0
        
        # Get status
        status = ''
        if 'Status' in df.columns:
            status = row.get('Status', '')
        elif 'status' in df.columns:
            status = row.get('status', '')
        
        # Get project and program
        projecto = row.get('projecto', '') if 'projecto' in df.columns else ''
        programa = row.get('programa', '') if 'programa' in df.columns else ''
        
        if metas > 0:
            clean_data.append({
                'provincia': provincia,
                'delegacao': delegacao,
                'distrito': distrito,
                'metas_distrito': metas,
                'projecto': projecto,
                'programa': programa,
                'total_registos': total_registos,
                'mpesa_abertas': mpesa_abertas,
                'registos_no_sib': registos_sib,
                'fora_rede': fora_rede,
                'beneficiarios_pagos': beneficiarios_pagos,
                'status': status
            })
    
    result_df = pd.DataFrame(clean_data)
    
    # Calculate percentages
    result_df['pct_total_registos'] = (result_df['total_registos'] / result_df['metas_distrito'] * 100).round(1)
    result_df['pct_contas_mpesa'] = (result_df['mpesa_abertas'] / result_df['metas_distrito'] * 100).round(1)
    result_df['pct_beneficiarios_pagos'] = (result_df['beneficiarios_pagos'] / result_df['metas_distrito'].replace(0, np.nan) * 100).round(1).fillna(0)
    
    return result_df

# Load the data
df = load_data()

if not df.empty:
    # Filters
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        provincia_filter = st.selectbox("Província", ["Todas"] + sorted(df['provincia'].unique().tolist()))
    with col2:
        delegacao_filter = st.selectbox("Delegação", ["Todas"] + sorted(df['delegacao'].dropna().unique().tolist()))
    with col3:
        projecto_filter = st.selectbox("Projecto", ["Todos"] + sorted(df['projecto'].dropna().unique().tolist()))
    with col4:
        programa_filter = st.selectbox("Programa", ["Todos"] + sorted(df['programa'].dropna().unique().tolist()))
    with col5:
        status_filter = st.selectbox("Status", ["Todos"] + sorted(df['status'].dropna().unique().tolist()))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_df = df.copy()
    if provincia_filter != "Todas":
        filtered_df = filtered_df[filtered_df['provincia'] == provincia_filter]
    if delegacao_filter != "Todas":
        filtered_df = filtered_df[filtered_df['delegacao'] == delegacao_filter]
    if projecto_filter != "Todos":
        filtered_df = filtered_df[filtered_df['projecto'] == projecto_filter]
    if programa_filter != "Todos":
        filtered_df = filtered_df[filtered_df['programa'] == programa_filter]
    if status_filter != "Todos":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    # Calculate statistics
    total_metas = filtered_df['metas_distrito'].sum()
    total_registos = filtered_df['total_registos'].sum()
    total_mpesa = filtered_df['mpesa_abertas'].sum()
    total_pagos = filtered_df['beneficiarios_pagos'].sum()
    taxa_cobertura = (total_registos / total_metas * 100) if total_metas > 0 else 0
    num_distritos = filtered_df['distrito'].nunique()
    num_provincias = filtered_df['provincia'].nunique()
    
    # Display stats cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card" style="border-left-color: #10b981;">
            <h3>Total Metas</h3>
            <div class="value">{total_metas:,.0f}</div>
            <div class="subtitle">Objectivo distrital</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card" style="border-left-color: #059669;">
            <h3>Total Registos</h3>
            <div class="value">{total_registos:,.0f}</div>
            <div class="subtitle">{taxa_cobertura:.1f}% das metas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card" style="border-left-color: #06b6d4;">
            <h3>Contas M-Pesa</h3>
            <div class="value">{total_mpesa:,.0f}</div>
            <div class="subtitle">Abertas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card" style="border-left-color: #84cc16;">
            <h3>Beneficiários Pagos</h3>
            <div class="value">{total_pagos:,.0f}</div>
            <div class="subtitle">Pagamentos efectuados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="stat-card" style="border-left-color: #f59e0b;">
            <h3>M-Pesa vs Metas</h3>
            <div class="value">{(total_mpesa / total_metas * 100):.1f}%</div>
            <div class="subtitle">Contas abertas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="stat-card" style="border-left-color: #a78bfa;">
            <h3>Distritos Activos</h3>
            <div class="value">{num_distritos}</div>
            <div class="subtitle">Em {num_provincias} províncias</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # Chart 1: Registos por Província
        provincia_data = filtered_df.groupby('provincia').agg({
            'metas_distrito': 'sum',
            'total_registos': 'sum',
            'beneficiarios_pagos': 'sum'
        }).reset_index()
        
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(name='Metas', x=provincia_data['provincia'], y=provincia_data['metas_distrito'],
                               marker_color='rgba(245, 158, 11, 0.8)'))
        fig1.add_trace(go.Bar(name='Registos', x=provincia_data['provincia'], y=provincia_data['total_registos'],
                               marker_color='rgba(16, 185, 129, 0.8)'))
        fig1.add_trace(go.Bar(name='Pagos', x=provincia_data['provincia'], y=provincia_data['beneficiarios_pagos'],
                               marker_color='rgba(6, 182, 212, 0.8)'))
        fig1.update_layout(title='Metas vs Registos vs Pagamentos por Província', 
                          barmode='group', height=450,
                          paper_bgcolor='white', plot_bgcolor='white')
        fig1.update_xaxes(title='Província')
        fig1.update_yaxes(title='Número de Beneficiários', tickformat=',.0f')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Chart 2: Taxa de Registo por Distrito
        distritos_com_registo = filtered_df[filtered_df['total_registos'] > 0].copy()
        if len(distritos_com_registo) > 0:
            distritos_com_registo = distritos_com_registo.sort_values('pct_total_registos', ascending=True)
            distritos_com_registo['label'] = distritos_com_registo['distrito'] + ' (' + distritos_com_registo['provincia'] + ')'
            
            if len(distritos_com_registo) > 15:
                distritos_com_registo = distritos_com_registo.tail(15)
            
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=distritos_com_registo['pct_total_registos'], 
                                   y=distritos_com_registo['label'],
                                   orientation='h', 
                                   marker_color='rgba(16, 185, 129, 0.8)',
                                   text=distritos_com_registo['pct_total_registos'].apply(lambda x: f'{x:.1f}%'),
                                   textposition='outside'))
            fig2.update_layout(title='Registo por Distrito (%)', height=450,
                              paper_bgcolor='white', plot_bgcolor='white',
                              xaxis=dict(title='Percentagem (%)', range=[0, 100]))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sem dados de registo disponíveis")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Chart 3: Contas M-Pesa por Distrito
        distritos_com_mpesa = filtered_df[filtered_df['mpesa_abertas'] > 0].copy()
        if len(distritos_com_mpesa) > 0:
            distritos_com_mpesa = distritos_com_mpesa.sort_values('pct_contas_mpesa', ascending=True)
            distritos_com_mpesa['label'] = distritos_com_mpesa['distrito'] + ' (' + distritos_com_mpesa['provincia'] + ')'
            
            if len(distritos_com_mpesa) > 15:
                distritos_com_mpesa = distritos_com_mpesa.tail(15)
            
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(x=distritos_com_mpesa['pct_contas_mpesa'], 
                                   y=distritos_com_mpesa['label'],
                                   orientation='h', 
                                   marker_color='rgba(6, 182, 212, 0.8)',
                                   text=distritos_com_mpesa['pct_contas_mpesa'].apply(lambda x: f'{x:.1f}%'),
                                   textposition='outside'))
            fig3.update_layout(title='Contas M-Pesa por Distrito (%)', height=450,
                              paper_bgcolor='white', plot_bgcolor='white',
                              xaxis=dict(title='Percentagem (%)', range=[0, 100]))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Sem dados de M-Pesa disponíveis")
    
    with col4:
        # Chart 4: Progresso de Pagamentos
        with_pagos = filtered_df[filtered_df['beneficiarios_pagos'] > 0].copy()
        if len(with_pagos) > 0:
            pagos_provincia = with_pagos.groupby('provincia')['beneficiarios_pagos'].sum().reset_index()
            
            fig4 = go.Figure()
            fig4.add_trace(go.Pie(labels=pagos_provincia['provincia'], 
                                   values=pagos_provincia['beneficiarios_pagos'],
                                   textinfo='label+value',
                                   textposition='auto',
                                   marker=dict(colors=px.colors.qualitative.Set3)))
            fig4.update_layout(title='Distribuição de Pagamentos por Província', 
                              height=450,
                              paper_bgcolor='white', 
                              plot_bgcolor='white',
                              showlegend=False)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Sem dados de pagamentos disponíveis")
    
    # Data Table with totals
    st.markdown("""
    <div class="custom-table-container">
        <h2 style="color: #059669; margin-bottom: 20px;">📋 Detalhes por Distrito</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Prepare display dataframe
    display_df = filtered_df[['provincia', 'delegacao', 'distrito', 'metas_distrito', 'projecto', 'programa',
                              'total_registos', 'mpesa_abertas', 'registos_no_sib', 'fora_rede',
                              'pct_contas_mpesa', 'pct_total_registos', 'beneficiarios_pagos', 
                              'pct_beneficiarios_pagos', 'status']].copy()
    
    # Format percentage columns
    display_df['pct_contas_mpesa_display'] = display_df['pct_contas_mpesa'].apply(lambda x: f"{x:.1f}%")
    display_df['pct_total_registos_display'] = display_df['pct_total_registos'].apply(lambda x: f"{x:.1f}%")
    display_df['pct_beneficiarios_pagos_display'] = display_df['pct_beneficiarios_pagos'].apply(lambda x: f"{x:.1f}%" if x > 0 else "0%")
    
    # Create table with province subtotals and grand total
    table_data = []
    
    # Group by province to add subtotals
    for provincia in sorted(display_df['provincia'].unique()):
        provincia_df = display_df[display_df['provincia'] == provincia]
        
        # Add individual rows
        for _, row in provincia_df.iterrows():
            table_data.append({
                'Província': row['provincia'],
                'Delegação': row['delegacao'],
                'Distrito': row['distrito'],
                'Metas': int(row['metas_distrito']),
                'Projecto': row['projecto'],
                'Programa': row['programa'],
                'Total Registos': int(row['total_registos']),
                'Contas M-Pesa': int(row['mpesa_abertas']),
                '% Contas M-Pesa': row['pct_contas_mpesa_display'],
                'Registos SIB': int(row['registos_no_sib']),
                'Fora da Rede': int(row['fora_rede']),
                '% Total Registos': row['pct_total_registos_display'],
                'Beneficiários Pagos': int(row['beneficiarios_pagos']),
                '% Pagos': row['pct_beneficiarios_pagos_display'],
                'Status': row['status'],
                'is_subtotal': False
            })
        
        # Add province subtotal
        provincia_metas = provincia_df['metas_distrito'].sum()
        provincia_registos = provincia_df['total_registos'].sum()
        provincia_mpesa = provincia_df['mpesa_abertas'].sum()
        provincia_sib = provincia_df['registos_no_sib'].sum()
        provincia_fora = provincia_df['fora_rede'].sum()
        provincia_pagos = provincia_df['beneficiarios_pagos'].sum()
        
        table_data.append({
            'Província': f"📍 TOTAL {provincia.upper()}",
            'Delegação': '',
            'Distrito': '',
            'Metas': int(provincia_metas),
            'Projecto': '',
            'Programa': '',
            'Total Registos': int(provincia_registos),
            'Contas M-Pesa': int(provincia_mpesa),
            '% Contas M-Pesa': f"{(provincia_mpesa/provincia_metas*100):.1f}%" if provincia_metas > 0 else "0%",
            'Registos SIB': int(provincia_sib),
            'Fora da Rede': int(provincia_fora),
            '% Total Registos': f"{(provincia_registos/provincia_metas*100):.1f}%" if provincia_metas > 0 else "0%",
            'Beneficiários Pagos': int(provincia_pagos),
            '% Pagos': f"{(provincia_pagos/provincia_registos*100):.1f}%" if provincia_registos > 0 else "0%",
            'Status': '',
            'is_subtotal': True
        })
    
    # Add grand total
    total_metas_all = display_df['metas_distrito'].sum()
    total_registos_all = display_df['total_registos'].sum()
    total_mpesa_all = display_df['mpesa_abertas'].sum()
    total_sib_all = display_df['registos_no_sib'].sum()
    total_fora_all = display_df['fora_rede'].sum()
    total_pagos_all = display_df['beneficiarios_pagos'].sum()
    
    table_data.append({
        'Província': '🎯 TOTAL GERAL',
        'Delegação': '',
        'Distrito': '',
        'Metas': int(total_metas_all),
        'Projecto': '',
        'Programa': '',
        'Total Registos': int(total_registos_all),
        'Contas M-Pesa': int(total_mpesa_all),
        '% Contas M-Pesa': f"{(total_mpesa_all/total_metas_all*100):.1f}%" if total_metas_all > 0 else "0%",
        'Registos SIB': int(total_sib_all),
        'Fora da Rede': int(total_fora_all),
        '% Total Registos': f"{(total_registos_all/total_metas_all*100):.1f}%" if total_metas_all > 0 else "0%",
        'Beneficiários Pagos': int(total_pagos_all),
        '% Pagos': f"{(total_pagos_all/total_registos_all*100):.1f}%" if total_registos_all > 0 else "0%",
        'Status': '',
        'is_subtotal': True
    })
    
    # Create final dataframe for display
    final_display_df = pd.DataFrame(table_data)
    
    # Apply styling for subtotals using DataFrame styler
    def highlight_subtotals(row):
        if row['is_subtotal']:
            return ['background-color: #fef3c7; font-weight: bold'] * len(row)
        return [''] * len(row)
    
    # Display the styled dataframe
    st.dataframe(
        final_display_df.drop('is_subtotal', axis=1),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Metas": st.column_config.NumberColumn(format="%d"),
            "Total Registos": st.column_config.NumberColumn(format="%d"),
            "Contas M-Pesa": st.column_config.NumberColumn(format="%d"),
            "Registos SIB": st.column_config.NumberColumn(format="%d"),
            "Fora da Rede": st.column_config.NumberColumn(format="%d"),
            "Beneficiários Pagos": st.column_config.NumberColumn(format="%d"),
        }
    )
    
    # Add note about totals
    st.caption("📌 Linhas com fundo amarelo representam totais por província e total geral")

else:
    st.error("""
    ### ❌ Erro ao carregar os dados
    
    **Certifique-se que:**
    1. O ficheiro Excel está na mesma pasta que este script
    2. O nome do ficheiro é exatamente: `SPER and HCP_R&P streamlit dash - Copy.xlsx`
    3. O ficheiro contém as colunas necessárias
    """)