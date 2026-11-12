import pandas as pd
import plotly.express as px
import os

# 1. Configurações Iniciais
COORDENADAS_ES = {
    'SERRA': {'lat': -20.1286, 'lon': -40.3078}, 'CARIACICA': {'lat': -20.2631, 'lon': -40.4205},
    'VITORIA': {'lat': -20.3155, 'lon': -40.3128}, 'VILA VELHA': {'lat': -20.3297, 'lon': -40.2925},
    'LINHARES': {'lat': -19.3911, 'lon': -40.0722}, 'ARACRUZ': {'lat': -19.8194, 'lon': -40.2742},
    'MONTANHA': {'lat': -18.1269, 'lon': -40.3633}, 'SAO GABRIEL DA PALHA': {'lat': -18.7647, 'lon': -40.5344},
    'GOVERNADOR LINDENBERG': {'lat': -19.2661, 'lon': -40.4786}, 'CACHOEIRO DE ITAPEMIRIM': {'lat': -20.8489, 'lon': -41.1128},
    'SAO MATEUS': {'lat': -18.7161, 'lon': -39.8617}, 'GUARAPARI': {'lat': -20.6667, 'lon': -40.4975},
    'COLATINA': {'lat': -19.5383, 'lon': -40.6294}
}

# 2. Carregar Dados Tratando as Quebras de Encoding ()
print("Carregando dados...")
caminhos_violencia = ["data/violencia-domestica.csv", "violencia-domestica.csv", "violencia-domestica_2.csv"]
caminhos_homicidios = ["data/homicidios-e-feminicidios.csv", "homicidios-e-feminicidios.csv", "homicidios-e-feminicidios_2.csv"]

file_v = next((p for p in caminhos_violencia if os.path.exists(p)), caminhos_violencia[-1])
file_h = next((p for p in caminhos_homicidios if os.path.exists(p)), caminhos_homicidios[-1])

df_violencia = pd.read_csv(file_v, sep=";", on_bad_lines="skip", encoding='latin1')
df_homicidios = pd.read_csv(file_h, sep=";", on_bad_lines="skip", encoding='utf-8')

# Função salva-vidas para arrumar as colunas e os ""
def limpar_dados_corrompidos(df):
    df.columns = df.columns.str.replace('', 'Í').str.replace('ï¿½', 'Í').str.strip().str.upper()

    mapeamento_colunas = {
        'MUNICPIO': 'MUNICÍPIO',
        'CUTIS': 'CÚTIS',
        'COR': 'CÚTIS',
        'GENERO': 'SEXO',
        'DATA': 'DATA DO FATO'
    }
    # Corrigido o alerta do Pandas (removido inplace=True)
    df = df.rename(columns=mapeamento_colunas)

    df = df.replace({'': 'í', 'ï¿½': 'í'}, regex=True)
    return df

df_violencia = limpar_dados_corrompidos(df_violencia)
df_homicidios = limpar_dados_corrompidos(df_homicidios)

if 'MUNICÍPIO' in df_violencia.columns:
    df_violencia['MUNICÍPIO'] = df_violencia['MUNICÍPIO'].astype(str).str.strip().str.upper()
if 'MUNICÍPIO' in df_homicidios.columns:
    df_homicidios['MUNICÍPIO'] = df_homicidios['MUNICÍPIO'].astype(str).str.strip().str.upper()
    df_homicidios['MUNICÍPIO'] = df_homicidios['MUNICÍPIO'].str.replace('MUNICíPIO', 'MUNICÍPIO')

if 'SEXO' in df_violencia.columns:
    df_mulheres = df_violencia[df_violencia['SEXO'].isin(['FEMININO', 'TRANSEXUAL', '2 - FEMININO', '2 - Feminino'])].copy()
else:
    df_mulheres = df_violencia.copy()

if 'DATA DO FATO' in df_mulheres.columns:
    df_mulheres['DATA DO FATO'] = pd.to_datetime(df_mulheres['DATA DO FATO'], format='%d/%m/%Y', errors='coerce')
    df_mulheres['Ano-Mes'] = df_mulheres['DATA DO FATO'].dt.to_period('M').astype(str)

colunas_tipificacao = [c for c in df_homicidios.columns if 'TIPIFICA' in c]
if colunas_tipificacao:
    df_feminicidios = df_homicidios[df_homicidios[colunas_tipificacao[0]].str.contains('Feminic', case=False, na=False)].copy()
else:
    df_feminicidios = df_homicidios.iloc[0:0].copy()

if 'DATA DO FATO' in df_feminicidios.columns:
    df_feminicidios['DATA'] = pd.to_datetime(df_feminicidios['DATA DO FATO'], format='%d/%m/%Y', errors='coerce')
    df_feminicidios['Ano-Mes'] = df_feminicidios['DATA'].dt.to_period('M').astype(str)

for col in ['MUNICÍPIO', 'CÚTIS']:
    if col not in df_mulheres.columns: df_mulheres[col] = 'S/I'

# 3. Gerar Gráficos com Plotly
print("Gerando gráficos...")

map_data = df_mulheres.groupby(['MUNICÍPIO', 'CÚTIS']).size().reset_index(name='Casos')
map_data['lat'] = map_data['MUNICÍPIO'].map(lambda x: COORDENADAS_ES.get(x, {}).get('lat', None))
map_data['lon'] = map_data['MUNICÍPIO'].map(lambda x: COORDENADAS_ES.get(x, {}).get('lon', None))
map_data = map_data.dropna(subset=['lat', 'lon'])

# Atualizado para o novo padrão do Plotly v6.0+ (scatter_map e map_style)
fig_mapa = px.scatter_map(map_data, lat="lat", lon="lon", size="Casos", color="CÚTIS", hover_name="MUNICÍPIO", zoom=6.5, height=450, color_discrete_sequence=px.colors.qualitative.Bold)
fig_mapa.update_layout(map_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
html_mapa = fig_mapa.to_html(full_html=False, include_plotlyjs='cdn')

top_cidades = df_mulheres['MUNICÍPIO'].value_counts().head(10).index
df_top_cidades = df_mulheres[df_mulheres['MUNICÍPIO'].isin(top_cidades)]
fig_barras = px.bar(df_top_cidades, x="MUNICÍPIO", color="CÚTIS", color_discrete_sequence=px.colors.qualitative.Safe, barmode="stack", height=420)
fig_barras.update_layout(xaxis={'categoryorder':'total descending'}, margin={"r":0,"t":0,"l":0,"b":0})
html_barras = fig_barras.to_html(full_html=False, include_plotlyjs=False)

if 'Ano-Mes' in df_mulheres.columns:
    agg_violencia = df_mulheres.groupby('Ano-Mes').size().reset_index(name='Quantidade')
    agg_violencia = agg_violencia[agg_violencia['Ano-Mes'] != 'NaT'].sort_values('Ano-Mes')
    fig_evolucao_v = px.line(agg_violencia, x='Ano-Mes', y='Quantidade', markers=True, color_discrete_sequence=['#9A031E'])
    html_evolucao_v = fig_evolucao_v.to_html(full_html=False, include_plotlyjs=False)
else:
    html_evolucao_v = "<p>Sem dados de data.</p>"

if 'Ano-Mes' in df_feminicidios.columns:
    agg_feminicidios = df_feminicidios.groupby('Ano-Mes').size().reset_index(name='Quantidade')
    agg_feminicidios = agg_feminicidios[agg_feminicidios['Ano-Mes'] != 'NaT'].sort_values('Ano-Mes')
    fig_evolucao_f = px.line(agg_feminicidios, x='Ano-Mes', y='Quantidade', markers=True, color_discrete_sequence=['#171720'])
    html_evolucao_f = fig_evolucao_f.to_html(full_html=False, include_plotlyjs=False)
else:
    html_evolucao_f = "<p>Sem dados de data.</p>"

# 4. Montar o HTML Final
print("Montando index.html...")
html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard: Violência contra a Mulher</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style> body {{ background-color: #f8f9fa; }} .card {{ border: none; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; padding: 20px; }} </style>
</head>
<body>
    <div class="container py-4">
        <h2 class="mb-1">🛡️ Sistema de Análise de Violência de Gênero</h2>
        <p class="text-muted mb-4">Relatório Estático Gerado Automaticamente</p>

        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card bg-primary text-white text-center">
                    <h4>Ocorrências Totais</h4>
                    <h2>{len(df_mulheres):,}</h2>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card bg-dark text-white text-center">
                    <h4>Feminicídios Totais</h4>
                    <h2>{len(df_feminicidios)}</h2>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-7"><div class="card"><h5>📍 Mapa de Calor</h5>{html_mapa}</div></div>
            <div class="col-md-5"><div class="card"><h5>📊 Top 10 Municípios (Por Cútis)</h5>{html_barras}</div></div>
        </div>

        <div class="row">
            <div class="col-md-6"><div class="card"><h5>📈 Evolução: Agressões</h5>{html_evolucao_v}</div></div>
            <div class="col-md-6"><div class="card"><h5>📈 Evolução: Feminicídios</h5>{html_evolucao_f}</div></div>
        </div>

        <footer class="text-center text-muted mt-4"><small>Atualizado automaticamente via GitHub Actions 🚀</small></footer>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("✅ Deploy estático gerado com sucesso: index.html")
