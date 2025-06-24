import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. App Title and Description ---
# This sets the title and a small description for your web app.
st.set_page_config(layout="wide") # Use the full page width
st.title("Dashboard de Análise de Pacientes de Diálise - POA")
st.write('Feito por Arthur Accorsi, João Paulo Carneiro, Marcelo Slaviero e Rodrigo Pires para a disciplina "Visualização de Dados"')

df = pd.read_csv('dados_tratados.csv', low_memory=False)
df_poa = df.copy()

#########################################################################
# Sidebar para seleção de página
st.sidebar.title("Navegação")
pagina = st.sidebar.selectbox("Selecione uma análise:", [
    "📌 Perfil demográfico dos pacientes",
    "📌 Distribuição geográfica e por unidade",
    "📌 Perfil clínico (CID-10)",
    "📌 Evolução temporal",
    "📌 Painéis comparativos"
])
#########################################################################

if pagina == "📌 Perfil demográfico dos pacientes":
    st.header("📌 Perfil demográfico dos pacientes")

#########################################################################
    #primeira visualização
    st.header("Distribuição por Faixa Etária e Sexo")

    df_counts = df.groupby(['faixa_etaria', 'sexo_label'], observed=False).size().reset_index(name='count')
    fig1 = px.bar(
        df_counts,
        x='faixa_etaria',
        y='count',
        color='sexo_label',
        barmode='group',  # This creates the side-by-side bars, like 'hue'
        title="Distribuição por Faixa Etária e Sexo - Pacientes em Diálise POA",
        labels={
            'faixa_etaria': 'Faixa Etária',
            'count': 'Número de Pacientes',
            'sexo_label': 'Sexo'
        },
        template='plotly_white', # A clean, presentation-ready theme
        color_discrete_map={'Masculino': '#1f77b4', 'Feminino': '#ff7f0e'} # Optional: custom colors
    )
    st.plotly_chart(fig1, use_container_width=True)
#########################################################################

#########################################################################
    st.header("🌍 Distribuição por Raça/Cor")

    # Dicionário para traduzir os códigos
    map_raca = {
        1: "Branca",
        2: "Preta",
        3: "Parda",
        4: "Amarela",
        5: "Indígena",
        9: "Ignorado"
    }
    df_poa["raca_desc"] = df_poa["AP_RACACOR"].map(map_raca)

    raca_counts = df_poa["raca_desc"].value_counts().reset_index()
    raca_counts.columns = ["Raça/Cor", "Quantidade"]

    fig = px.pie(raca_counts, names="Raça/Cor", values="Quantidade", title="Distribuição por Raça/Cor - Pacientes em Diálise POA", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
#########################################################################

#########################################################################
    st.header("📊 Distribuição por Faixa Etária, Raça/Cor e Sexo")

    # Mapeia raça/cor e sexo para descrição
    map_raca = {
        1: "Branca",
        2: "Preta",
        3: "Parda",
        4: "Amarela",
        5: "Indígena",
        9: "Ignorado"
    }
    map_sexo = {
        "M": "Masculino",
        "F": "Feminino"
    }

    df_poa["raca_desc"] = df_poa["AP_RACACOR"].map(map_raca)
    df_poa["sexo_desc"] = df_poa["AP_SEXO"].map(map_sexo)

    # Agrupamento
    df_grouped = df_poa.groupby(["faixa_etaria", "raca_desc", "sexo_desc"]).size().reset_index(name="Quantidade")

    # Gráfico
    fig = px.treemap(df_grouped,
                    path=["sexo_desc", "raca_desc", "faixa_etaria"],
                    values="Quantidade",
                    color="raca_desc",
                    title="Treemap - Distribuição Demográfica")


    fig.update_layout(legend_title_text='Raça/Cor', template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
#########################################################################

elif pagina == "📌 Distribuição geográfica e por unidade":
    st.header("📌 Distribuição geográfica e por unidade")

#########################################################################
    st.header("🏘️ Mapa da distribuição de procedimentos por unidade")

    centro_lat = -30.03
    centro_lon = -51.23

    df_mapa = df_poa.groupby(['NOME_HOSPITAL', 'latitude', 'longitude']).size().reset_index(name='contagem_procedimentos')

    fig_mun = px.scatter_map(df_mapa,
                            lat="latitude",
                            lon="longitude",
                            size="contagem_procedimentos",
                            color="NOME_HOSPITAL", 
                            hover_name="NOME_HOSPITAL",
                            hover_data=["contagem_procedimentos"],
                            size_max=60,
                            zoom=11,
                            height=600,
                            )
    
    fig_mun.update_layout(
        mapbox_style="carto-positron",
        mapbox_center_lat=df_mapa['latitude'].mean(), 
        mapbox_center_lon=df_mapa['longitude'].mean(),
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )

    st.plotly_chart(fig_mun, use_container_width=True)
#########################################################################
#########################################################################
    st.header("🏥 Distribuição de Pacientes por Sexo nas Unidades")

    # Agrupamento
    sexo_unidade = df.groupby(['NOME_HOSPITAL', 'AP_SEXO']).size().reset_index(name='Número de Pacientes')
    sexo_unidade['Sexo'] = sexo_unidade['AP_SEXO'].map({'M': 'Masculino', 'F': 'Feminino'})

    # Unidades ordenadas por volume
    unidades_ordenadas = (
        sexo_unidade.groupby('NOME_HOSPITAL')['Número de Pacientes']
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    # Seleção de unidades
    unidades_selecionadas = st.multiselect(
        "Selecione as Unidades de Saúde para visualizar:",
        options=unidades_ordenadas,
        default=unidades_ordenadas[:7]
    )

    # Filtra os dados
    dados_filtrados = sexo_unidade[sexo_unidade['NOME_HOSPITAL'].isin(unidades_selecionadas)]

    # Gráfico
    fig_sexo = px.bar(
        dados_filtrados,
        x='NOME_HOSPITAL',
        y='Número de Pacientes',
        color='Sexo',
        barmode='group',
        labels={'NOME_HOSPITAL': 'Unidade'},
        template='plotly_white',
        color_discrete_map={'Masculino': '#264653', 'Feminino': '#e76f51'}
    )

    fig_sexo.update_layout(title="Distribuição de Pacientes nas Unidades", xaxis_title=None, yaxis_title="Número de Pacientes")
    st.plotly_chart(fig_sexo, use_container_width=True)
#########################################################################
elif pagina == "📌 Perfil clínico (CID-10)":
    st.header("📌 Perfil clínico (CID-10)")
#########################################################################

    st.header("Diagrama de sankey: Fluxo de Pacientes entre Procedimentos, CIDs e Unidades")

    # # --- Etapas 1 e 2: Limpeza e Preparação dos Dados (iguais ao anterior) ---
    # flow_cols_original = ['procedimento_desc', 'CIDCAS_DESC', 'NOME_HOSPITAL']
    # df_cleaned = df_poa.dropna(subset=flow_cols_original)

    # top_5_hospitals = df_cleaned['NOME_HOSPITAL'].value_counts().nlargest(5).index
    # df_filtered_hosp = df_cleaned[df_cleaned['NOME_HOSPITAL'].isin(top_5_hospitals)]

    # top_5_procedures = df_filtered_hosp['procedimento_desc'].value_counts().nlargest(5).index
    # df_filtered_proc = df_filtered_hosp[df_filtered_hosp['procedimento_desc'].isin(top_5_procedures)]

    # top_5_cids = df_filtered_proc['CIDCAS_DESC'].value_counts().nlargest(5).index
    # df_final = df_filtered_proc[df_filtered_proc['CIDCAS_DESC'].isin(top_5_cids)]

    # Mude de nlargest(5) para nlargest(10), por exemplo
    # --- Etapa 1: Limpeza e Nova Ordem de Filtragem ---
    flow_cols_original = ['procedimento_desc', 'CIDCAS_DESC', 'NOME_HOSPITAL']
    df_cleaned = df_poa.dropna(subset=flow_cols_original)

    # 1. Filtra para os 5 principais hospitais (como antes)
    top_7_hospitals = df_cleaned['NOME_HOSPITAL'].value_counts().nlargest(7).index
    df_filtered_hosp = df_cleaned[df_cleaned['NOME_HOSPITAL'].isin(top_7_hospitals)]

    all_cids = sorted(df_filtered_hosp['CIDCAS_DESC'].unique())
    selected_cids = st.multiselect(
        "Selecione um ou mais diagnósticos (CID) para analisar o fluxo:",
        options=all_cids,
        default=all_cids[:3] # Seleciona os 3 primeiros por padrão
    )

    if not selected_cids:
        st.warning("Por favor, selecione pelo menos um diagnóstico (CID).")
    else:
        # --- MUDANÇA 2: FILTRAR PELOS CIDs SELECIONADOS ---
        # Filtra o DataFrame com base na seleção de CIDs do usuário.
        df_selection = df_filtered_hosp[df_filtered_hosp['CIDCAS_DESC'].isin(selected_cids)]
        
        # --- MUDANÇA 3: A LÓGICA "TOP 5" AGORA É PARA PROCEDIMENTOS ---
        # DENTRO DA SELEÇÃO de CIDs, pega os 5 principais PROCEDIMENTOS.
        top_5_procedures = df_selection['procedimento_desc'].value_counts().nlargest(5).index
        df_final = df_selection[df_selection['procedimento_desc'].isin(top_5_procedures)]

        # --- Etapa 2: Preparação dos Nós e Links (código inalterado) ---
        # A ordem do fluxo no gráfico continua a mesma: Procedimento -> CID -> Hospital
        flow_cols_original = ['procedimento_desc', 'CIDCAS_DESC', 'NOME_HOSPITAL']
        
        all_labels = []
        for col in flow_cols_original:
            all_labels.extend(df_final[col].unique())

        all_labels = pd.unique(all_labels).tolist()
        label_to_index = {label: i for i, label in enumerate(all_labels)}

        sources, targets, values = [], [], []

        for i in range(len(flow_cols_original) - 1):
            source_col, target_col = flow_cols_original[i], flow_cols_original[i+1]
            link_counts = df_final.groupby([source_col, target_col]).size().reset_index(name='count')
            for _, row in link_counts.iterrows():
                sources.append(label_to_index[row[source_col]])
                targets.append(label_to_index[row[target_col]])
                values.append(row['count'])
                
        # --- Etapa 3: Criação da Figura Plotly ---
        if not values:
            st.warning("Nenhum dado encontrado para a seleção atual. Tente selecionar outros diagnósticos.")
        else:
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                pad=25,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_labels,
                color="#a6cde4",
                hovertemplate='<b>%{label}</b><br>Fluxo Total: %{value}<extra></extra>'
                ),
                link=dict(
                source=sources,
                target=targets,
                value=values,
                hovertemplate='De %{source.label} para %{target.label}<br>Total: %{value}<extra></extra>'
                )
            )])
            
            fig.update_layout(
                title_text=f"Fluxo para Diagnósticos Selecionados",
                height=700
            )
            st.plotly_chart(fig, use_container_width=True)

#########################################################################
    # Segunda visualização - Tipos de Procedimento
    st.header("🔬 Análise de Tipo de Procedimento")

    # Dados dos procedimentos
    top_procs = (
        df[df["procedimento_desc"].notna()]["procedimento_desc"]
        .value_counts()
        .reset_index()
    )
    top_procs.columns = ["Procedimento", "Ocorrências"]

    # Menu de seleção do tipo de gráfico
    grafico_tipo = st.sidebar.radio(
        "Tipo de visualização dos procedimentos:",
        ["Gráfico de barras", "Treemap", "Pizza (rosca)"],
        index=0,
        key="procedimento_grafico"
    )

    # Renderiza o gráfico conforme escolha
    if grafico_tipo == "Gráfico de barras":
        fig2 = px.bar(
            top_procs.head(10),
            x="Ocorrências",
            y="Procedimento",
            orientation="h",
            title="Distribuição dos Procedimentos",
            color="Procedimento",
            color_discrete_sequence=px.colors.sequential.Viridis_r  # cores mais escuras
        )

        fig2.update_layout(
            yaxis=dict(autorange="reversed"),
            template="plotly_white",
            showlegend=False
        )

    elif grafico_tipo == "Treemap":
        fig2 = px.treemap(
            top_procs,
            path=["Procedimento"],
            values="Ocorrências",
            title="Distribuição dos Procedimentos",
            color="Ocorrências",
            color_continuous_scale=px.colors.sequential.Viridis  # gradiente escuro
        )

        fig2.update_layout(template="plotly_white")

    elif grafico_tipo == "Pizza (rosca)":
        fig2 = px.pie(
            top_procs.head(10),
            names="Procedimento",
            values="Ocorrências",
            title="Distribuição dos Procedimentos",
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        fig2.update_traces(textinfo='percent+label', pull=[0.05]*10)
        fig2.update_layout(template='plotly_white')

    # Exibe o gráfico
    st.plotly_chart(fig2, use_container_width=True)
#########################################################################

#########################################################################
    # Terceira visualização - Análise de CID
    st.header("🧾 Análise de CID")

    # Filtra os CIDs (remove '0000') e pega os principais
    top_cidcas = df[df["AP_CIDCAS"] != "0000"]["CIDCAS_DESC"].value_counts().reset_index()
    top_cidcas.columns = ["CID", "Ocorrências"]

    # Menu de seleção do tipo de gráfico
    grafico_cid_tipo = st.sidebar.radio(
        "Tipo de visualização dos CIDs:",
        ["Gráfico de barras", "Treemap", "Pizza (rosca)"],
        index=0,
        key="cid_grafico"
    )

    # Renderiza o gráfico conforme escolha
    if grafico_cid_tipo == "Gráfico de barras":
        fig3_bar = px.bar(
            top_cidcas.head(10),
            x="Ocorrências",
            y="CID",
            orientation="h",
            color="CID",
            color_discrete_sequence=px.colors.sequential.Viridis_r
        )
        fig3_bar.update_layout(
            yaxis=dict(autorange="reversed"),
            template="plotly_white",
            title="Distribuição por CID",
            showlegend=False
        )
        st.plotly_chart(fig3_bar, use_container_width=True)

    elif grafico_cid_tipo == "Treemap":
        fig3_tree = px.treemap(
            top_cidcas.head(15),
            path=["CID"],
            values="Ocorrências",
            color="Ocorrências",
            color_continuous_scale="Viridis",
            title="Distribuição por CID"
        )
        fig3_tree.update_layout(template='plotly_white')
        st.plotly_chart(fig3_tree, use_container_width=True)

    elif grafico_cid_tipo == "Pizza (rosca)":
        fig3_pizza = px.pie(
            top_cidcas.head(10),
            names="CID",
            values="Ocorrências",
            hole=0.4,
            title="Distribuição por CID",
            color_discrete_sequence=px.colors.sequential.Viridis_r
        )
        fig3_pizza.update_traces(textinfo='percent+label', pull=[0.05]*10)
        fig3_pizza.update_layout(template='plotly_white')
        st.plotly_chart(fig3_pizza, use_container_width=True)
#########################################################################
elif pagina == "📌 Evolução temporal":
    st.header("📌Evolução temporal")
#########################################################################
    # Primeira visualização - Distribuição por Ano
    st.header("📅 Evolução Anual de Pacientes em Diálise")

    # Conta os pacientes por ano e ordena
    ano_counts = df["ano"].value_counts().sort_index()

    # Gráfico com Plotly
    fig_ano = px.bar(
        x=ano_counts.index,
        y=ano_counts.values,
        labels={"x": "Ano", "y": "Número de Pacientes"},
        template="plotly_white",
        color_discrete_sequence=['#264653']  # tom escuro
    )

    fig_ano.update_layout(
        title="Número de Pacientes por ano",
        showlegend=False,
        xaxis_title="Ano",
        yaxis_title="Número de Pacientes"
    )

    # Mostra no Streamlit
    st.plotly_chart(fig_ano, use_container_width=True)
#########################################################################

#########################################################################
    # Sexta visualização
    st.header("📊 Internações por Faixa Etária e Ano")

    df_area = df.groupby(["ano", "faixa_etaria"]).size().reset_index(name="n_pacientes")
    df_area = df_area.sort_values(["ano", "faixa_etaria"])

    fig = px.area(
        df_area,
        x="ano",
        y="n_pacientes",
        color="faixa_etaria",
        labels={"n_pacientes": "Número de Pacientes", "ano": "Ano", "faixa_etaria": "Faixa Etária"},
        title="Evolução Acumulada das Internações por Faixa Etária"
    )
    fig.update_layout(xaxis=dict(type='category'), height=600)

    st.plotly_chart(fig, use_container_width=True)
#########################################################################

#######################################################################
    st.header("🏥 Evolução de Internações por Unidade")

    # Agrupa internações por unidade e ano
    unidade_ano = df.groupby(['NOME_HOSPITAL', 'ano']).size().reset_index(name='Internações')

    # Lista todas as unidades disponíveis (ordenadas pelas mais frequentes)
    unidades_disponiveis = unidade_ano.groupby("NOME_HOSPITAL")["Internações"].sum().sort_values(ascending=False).index.tolist()

    # Seleção interativa no sidebar ou direto no app
    unidades_selecionadas = st.multiselect(
        "Selecione as Unidades de Diálise para Comparação:",
        options=unidades_disponiveis,
        default=unidades_disponiveis[:7]  # Top 7 por padrão
    )

    # Filtra os dados conforme a seleção
    unidade_ano_filtrado = unidade_ano[unidade_ano['NOME_HOSPITAL'].isin(unidades_selecionadas)]

    # Gera o gráfico de linha
    fig = px.line(
        unidade_ano_filtrado,
        x='ano',
        y='Internações',
        color='NOME_HOSPITAL',
        markers=True,
        labels={
            'ano': 'Ano',
            'Internações': 'Número de Internações',
            'NOME_HOSPITAL': 'Unidade de Diálise'
        },
        title="Número de Internações por ano",
        template='plotly_white',
        line_shape='linear'
    )

    # Exibe o gráfico no app
    st.plotly_chart(fig, use_container_width=True)
#########################################################################

elif pagina == "📌 Painéis comparativos":
    st.header("📌 Painéis comparativos")
#######################################################################
    sexo_map = {'F': 'Feminino', 'M': 'Masculino'}
    df_poa['sexo_desc'] = df_poa['AP_SEXO'].map(sexo_map)
    st.header("🔄 Comparativo: Indicadores por Unidade de Saúde")

    # Seleciona as unidades com mais registros
    top_unidades = df_poa["NOME_HOSPITAL"].value_counts().nlargest(5).index.tolist()

    # Filtro interativo
    unidade_selecionada = st.selectbox("Selecione a Unidade", top_unidades)

    # Filtra os dados
    df_unidade = df_poa[df_poa["NOME_HOSPITAL"] == unidade_selecionada]

    # Calcula indicadores
    idade_media = round(df_unidade["AP_NUIDADE"].mean(), 1)
    sexo_mais_comum = df_unidade["sexo_desc"].mode()[0]
    cid_mais_comum = df_unidade["CIDCAS_DESC"].mode()[0] if df_unidade["CIDCAS_DESC"].notna().any() else "Não disponível"
    proc_mais_comum = df_unidade["procedimento_desc"].mode()[0] if df_unidade["procedimento_desc"].notna().any() else "Não disponível"

    # Exibe painel
    st.markdown(f"""
    **Unidade Selecionada:** `{unidade_selecionada}`  
    - 👤 Idade média: **{idade_media} anos**  
    - ⚧️ Sexo mais comum: **{sexo_mais_comum}**  
    - 🧾 CID causa associada mais comum: **{cid_mais_comum}**  
    - 💉 Procedimento mais comum: **{proc_mais_comum}**
    """)
#######################################################################

#######################################################################
    st.header("🎯 Perfil do Paciente Típico")

    # Cálculo dos dados
    idade_media_geral = round(df_poa["AP_NUIDADE"].mean(), 1)
    sexo_mais_comum_geral = df_poa["sexo_desc"].mode()[0]
    cid_mais_comum_geral = df_poa[df_poa["CIDCAS_DESC"].notna()]["CIDCAS_DESC"].mode()[0]
    proc_mais_comum_geral = df_poa[df_poa["procedimento_desc"].notna()]["procedimento_desc"].mode()[0]
    unidade_mais_comum = df_poa["NOME_HOSPITAL"].mode()[0]

    # Exibição
    st.markdown(f"""
    - 👤 **Idade média:** {idade_media_geral} anos  
    - ⚧️ **Sexo mais comum:** {sexo_mais_comum_geral}  
    - 🧾 **CID causa associada mais comum:** {cid_mais_comum_geral}  
    - 💉 **Procedimento mais comum:** {proc_mais_comum_geral}  
    - 🏥 **Unidade com mais atendimentos:** {unidade_mais_comum}
    """)
#######################################################################

#######################################################################
    st.header("🎯 Perfil do Paciente Típico em Diálise (POA)")

    # Mapeia o sexo para descrição legível (caso ainda não exista)
    if "sexo_desc" not in df_poa.columns:
        sexo_map = {'F': 'Feminino', 'M': 'Masculino'}
        df_poa['sexo_desc'] = df_poa['AP_SEXO'].map(sexo_map)

    # Calcula os indicadores gerais
    idade_media_geral = round(df_poa["AP_NUIDADE"].mean(), 1)
    sexo_mais_comum_geral = df_poa["sexo_desc"].mode()[0]
    cid_mais_comum_geral = df_poa["CIDCAS_DESC"].mode()[0] if "CIDCAS_DESC" in df_poa.columns else "N/D"
    proc_mais_comum_geral = df_poa["procedimento_desc"].mode()[0] if "procedimento_desc" in df_poa.columns else "N/D"
    unidade_mais_comum = df_poa["NOME_HOSPITAL"].mode()[0] if "NOME_HOSPITAL" in df_poa.columns else "N/D"

    # Mostra os dados no Streamlit com st.metric
    col1, col2, col3 = st.columns(3)
    col1.metric("Idade Média", f"{idade_media_geral} anos")
    col2.metric("Sexo Mais Comum", sexo_mais_comum_geral)
    col3.metric("Unidade Mais Frequente", unidade_mais_comum)

    col4, col5 = st.columns(2)
    col4.metric("CID Mais Recorrente", cid_mais_comum_geral)
    col5.metric("Procedimento Mais Frequente", proc_mais_comum_geral)
#######################################################################
