import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Avançado: Violência contra a Mulher", page_icon="🛡️", layout="wide")

COORDENADAS_ES = {
    'SERRA': {'lat': -20.1286, 'lon': -40.3078},
    'CARIACICA': {'lat': -20.2631, 'lon': -40.4205},
    'VITORIA': {'lat': -20.3155, 'lon': -40.3128},
    'VILA VELHA': {'lat': -20.3297, 'lon': -40.2925},
    'LINHARES': {'lat': -19.3911, 'lon': -40.0722},
    'ARACRUZ': {'lat': -19.8194, 'lon': -40.2742},
    'MONTANHA': {'lat': -18.1269, 'lon': -40.3633},
    'SAO GABRIEL DA PALHA': {'lat': -18.7647, 'lon': -40.5344},
    'GOVERNADOR LINDENBERG': {'lat': -19.2661, 'lon': -40.4786},
    'CACHOEIRO DE ITAPEMIRIM': {'lat': -20.8489, 'lon': -41.1128},
    'SAO MATEUS': {'lat': -18.7161, 'lon': -39.8617},
    'GUARAPARI': {'lat': -20.6667, 'lon': -40.4975},
    'COLATINA': {'lat': -19.5383, 'lon': -40.6294}
}


@st.cache_data
def carregar_dados():
    df_violencia = pd.read_csv(
        "data/violencia-domestica.csv", sep=";", on_bad_lines="skip", encoding='latin1')
    df_homicidios = pd.read_csv(
        "data/homicidios-e-feminicidios.csv", sep=";", on_bad_lines="skip", encoding='latin1')

    if 'MUNICÍPIO' in df_violencia.columns:
        df_violencia['MUNICÍPIO'] = df_violencia['MUNICÍPIO'].str.strip(
        ).str.upper()
    if 'MUNICÍPIO' in df_homicidios.columns:
        df_homicidios['MUNICÍPIO'] = df_homicidios['MUNICÍPIO'].str.strip(
        ).str.upper()

    if 'SEXO' in df_violencia.columns:
        df_mulheres = df_violencia[df_violencia['SEXO'] == 'FEMININO'].copy()
    else:
        df_mulheres = df_violencia.copy()

    if 'DATA DO FATO' in df_mulheres.columns:
        df_mulheres['DATA DO FATO'] = pd.to_datetime(
            df_mulheres['DATA DO FATO'], format='%d/%m/%Y', errors='coerce')
        df_mulheres['Ano'] = df_mulheres['DATA DO FATO'].dt.year
        df_mulheres['Ano-Mes'] = df_mulheres['DATA DO FATO'].dt.to_period(
            'M').astype(str)

    df_feminicidios = df_homicidios[df_homicidios['TIPIFICACAO'].str.contains(
        'Feminicídio', case=False, na=False)].copy()
    if 'DATA' in df_feminicidios.columns:
        df_feminicidios['DATA'] = pd.to_datetime(
            df_feminicidios['DATA'], format='%d/%m/%Y', errors='coerce')
        df_feminicidios['Ano'] = df_feminicidios['DATA'].dt.year
        df_feminicidios['Ano-Mes'] = df_feminicidios['DATA'].dt.to_period(
            'M').astype(str)

    return df_mulheres, df_feminicidios


df_mulheres, df_feminicidios = carregar_dados()

st.title("🛡️ Sistema de Análise de Violência de Gênero")
st.markdown("Explore a distribuição geográfica, perfis étnicos e tendências temporais das ocorrências registradas.")

st.sidebar.header("🎯 Filtros do Painel")

anos_unicos = [int(a) for a in df_mulheres['Ano'].unique() if pd.notna(a)]
lista_anos = ["Todos"] + sorted(anos_unicos, reverse=True)
ano_selecionado = st.sidebar.selectbox("Selecione o Ano:", lista_anos)

municipios_unicos = [str(m)
                     for m in df_mulheres['MUNICÍPIO'].unique() if pd.notna(m)]
lista_municipios = ["Todos"] + sorted(municipios_unicos)
municipio_selecionado = st.sidebar.selectbox(
    "Selecione o Município:", lista_municipios)

cores_unicas = [str(c) for c in df_mulheres['CÚTIS'].unique() if pd.notna(c)]
lista_cores = ["Todas"] + sorted(cores_unicas)
cor_selecionada = st.sidebar.selectbox("Filtrar por Cor/Cútis:", lista_cores)

tipos_unicos = [
    str(t) for t in df_mulheres['TIPO DE INCIDENTE'].unique() if pd.notna(t)]
lista_tipos = ["Todos"] + sorted(tipos_unicos)
tipo_selecionado = st.sidebar.selectbox(
    "Tipo de Incidente (Apenas Agressões):", lista_tipos)

df_v_filtrado = df_mulheres.copy()
df_f_filtrado = df_feminicidios.copy()

if ano_selecionado != "Todos":
    df_v_filtrado = df_v_filtrado[df_v_filtrado['Ano'] == ano_selecionado]
    df_f_filtrado = df_f_filtrado[df_f_filtrado['Ano'] == ano_selecionado]

if municipio_selecionado != "Todos":
    df_v_filtrado = df_v_filtrado[df_v_filtrado['MUNICÍPIO']
                                  == municipio_selecionado]
    df_f_filtrado = df_f_filtrado[df_f_filtrado['MUNICÍPIO']
                                  == municipio_selecionado]

if cor_selecionada != "Todas":
    df_v_filtrado = df_v_filtrado[df_v_filtrado['CÚTIS'] == cor_selecionada]
    if 'COR' in df_f_filtrado.columns:
        df_f_filtrado = df_f_filtrado[df_f_filtrado['COR'].str.contains(
            cor_selecionada, case=False, na=False)]

if tipo_selecionado != "Todos":
    df_v_filtrado = df_v_filtrado[df_v_filtrado['TIPO DE INCIDENTE']
                                  == tipo_selecionado]

col1, col2, col3 = st.columns(3)
col1.metric("Ocorrências no Filtro",
            f"{len(df_v_filtrado):,}".replace(",", "."))
col2.metric("Feminicídios no Filtro", f"{len(df_f_filtrado)}")
dias_f = df_v_filtrado['DATA DO FATO'].nunique()
col3.metric("Média Diária (Filtro)",
            f"{(len(df_v_filtrado)/dias_f if dias_f > 0 else 0):.2f}")

st.divider()
st.subheader("📍 Geolocalização e Perfil Étnico")

map_data = df_v_filtrado.groupby(
    ['MUNICÍPIO', 'CÚTIS']).size().reset_index(name='Casos')
map_data['lat'] = map_data['MUNICÍPIO'].map(
    lambda x: COORDENADAS_ES.get(x, {}).get('lat', None))
map_data['lon'] = map_data['MUNICÍPIO'].map(
    lambda x: COORDENADAS_ES.get(x, {}).get('lon', None))
map_data = map_data.dropna(subset=['lat', 'lon'])

col_mapa, col_proporcao = st.columns([6, 4])

with col_mapa:
    if not map_data.empty:
        fig_mapa = px.scatter_mapbox(
            map_data, lat="lat", lon="lon", size="Casos", color="CÚTIS",
            hover_name="MUNICÍPIO", hover_data=["Casos"], zoom=6.5, height=450,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_mapa.update_layout(mapbox_style="carto-positron",
                               margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig_mapa, use_container_width=True)
    else:
        st.info("Não há dados com coordenadas válidas para os filtros selecionados.")

with col_proporcao:
    top_cidades = df_v_filtrado['MUNICÍPIO'].value_counts().head(10).index
    df_top_cidades = df_v_filtrado[df_v_filtrado['MUNICÍPIO'].isin(
        top_cidades)]

    fig_barras_cor = px.bar(
        df_top_cidades, x="MUNICÍPIO", color="CÚTIS",
        title="Top 10 Municípios por Grupo Étnico",
        color_discrete_sequence=px.colors.qualitative.Safe, barmode="stack"
    )
    fig_barras_cor.update_layout(
        xaxis={'categoryorder': 'total descending'}, height=420)
    st.plotly_chart(fig_barras_cor, use_container_width=True)


st.divider()
st.subheader("📈 Análise Temporal: Agressões vs. Feminicídios")
st.markdown("Visualização da evolução do volume de ocorrências ao longo dos meses. Utilizar dois gráficos separados permite observar as tendências sem que a enorme diferença de escala entre agressões e homicídios esconda os dados de feminicídio.")

agg_violencia = df_v_filtrado.groupby(
    'Ano-Mes').size().reset_index(name='Quantidade')
agg_violencia = agg_violencia[agg_violencia['Ano-Mes']
                              != 'NaT'].sort_values('Ano-Mes')

agg_feminicidios = df_f_filtrado.groupby(
    'Ano-Mes').size().reset_index(name='Quantidade')
agg_feminicidios = agg_feminicidios[agg_feminicidios['Ano-Mes']
                                    != 'NaT'].sort_values('Ano-Mes')

col_tend_v, col_tend_f = st.columns(2)

with col_tend_v:
    if not agg_violencia.empty:
        fig_evolucao_v = px.line(
            agg_violencia, x='Ano-Mes', y='Quantidade', markers=True,
            title="Evolução de Ocorrências / Agressões",
            color_discrete_sequence=['#9A031E']
        )
        fig_evolucao_v.update_xaxes(tickangle=45)
        st.plotly_chart(fig_evolucao_v, use_container_width=True)
    else:
        st.info("Sem dados de ocorrências para este período.")

with col_tend_f:
    if not agg_feminicidios.empty:
        fig_evolucao_f = px.line(
            agg_feminicidios, x='Ano-Mes', y='Quantidade', markers=True,
            title="Evolução de Feminicídios",
            color_discrete_sequence=['#171720']
        )
        fig_evolucao_f.update_xaxes(tickangle=45)
        st.plotly_chart(fig_evolucao_f, use_container_width=True)
    else:
        st.info("Não houve registros de feminicídios para os filtros selecionados.")


st.divider()
col_local, col_meios = st.columns(2)

with col_local:
    st.markdown("**Ambientes de Risco (Tipo de Local)**")
    if 'TIPO DE LOCAL' in df_v_filtrado.columns:
        locais = df_v_filtrado['TIPO DE LOCAL'].value_counts().head(
            6).reset_index()
        locais.columns = ['Tipo de Local', 'Total de Ocorrências']
        fig_local = px.bar(locais, x='Total de Ocorrências', y='Tipo de Local',
                           orientation='h', color_discrete_sequence=['#4A4E69'])
        fig_local.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_local, use_container_width=True)

with col_meios:
    st.markdown("**Instrumentos Utilizados nos Feminicídios**")
    if 'MEIOS' in df_f_filtrado.columns:
        meios = df_f_filtrado['MEIOS'].value_counts().reset_index()
        meios.columns = ['Meio Utilizado', 'Casos']
        fig_meios = px.pie(meios, names='Meio Utilizado', values='Casos',
                           hole=0.3, color_discrete_sequence=px.colors.sequential.Plotly3)
        st.plotly_chart(fig_meios, use_container_width=True)
