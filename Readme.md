### 🎯 Finalidade (O Porquê)
A violência de género, nomeadamente a violência doméstica e o feminicídio, é um problema estrutural e complexo que exige ações baseadas em evidências. A finalidade principal deste projeto é **democratizar a compreensão dos dados de segurança pública**, transformando milhares de linhas brutas de boletins de ocorrência num conhecimento visual, dinâmico e acessível. 

Este painel analítico foi idealizado para servir como uma ferramenta estratégica, visando:
* **Apoiar Políticas Públicas e Forças de Segurança:** Permitir a identificação de "manchas criminais" (locais com maior incidência) e padrões de horários/meses, auxiliando no planeamento de ações preventivas (como rondas de proteção à mulher).
* **Auxiliar Pesquisadores e Jornalistas:** Facilitar o cruzamento sociodemográfico, evidenciando, por exemplo, como a violência afeta de forma diferente mulheres de diferentes grupos étnicos (cor/cútis).
* **Consciencializar a Sociedade Civil:** Dar visibilidade ao volume real (média de casos por dia) e à gravidade dos incidentes que ocorrem tanto em via pública quanto em ambiente doméstico.

### ⚙️ Explicação (O Quê e Como)
O projeto é um **Dashboard Interativo** (Painel de Controlo) desenvolvido em Python. Ele funciona através do processamento simultâneo de duas bases de dados policiais: uma focada no amplo espetro da violência doméstica (ameaças, agressões físicas, violação de medidas protetivas) e outra com o recorte estrito de letalidade (homicídios e feminicídios).

Através de uma interface web limpa (gerada via **Streamlit**), o utilizador não necessita de conhecimentos técnicos em planilhas ou programação para explorar os dados. O sistema utiliza a biblioteca **Pandas** nos bastidores para agrupar e cruzar informações em frações de segundo sempre que um filtro é alterado. Em seguida, a biblioteca **Plotly** renderiza os resultados em mapas geográficos e gráficos de tendência, permitindo uma investigação detalhada que vai do nível macro (o estado/ano inteiro) ao nível micro (um bairro específico num município).

### 2. Preparar a Base de Dados do Espirito Santo

O sistema foi desenhado para processar os dados oficiais diretamente de dois ficheiros CSV organizados com separador ponto e vírgula (`;`) e codificação `latin1`. Certifique-se de posicionar os seguintes ficheiros exatamente na **raiz do projeto**:

-   `violencia-domestica.csv`
    
-   `homicidios-e-feminicidios.csv`
    

### 3. Instalar os Pacotes Necessários

Pode instalar as dependências diretamente através do gestor de pacotes do Python (`pip`):

Bash

```
pip install streamlit pandas plotly

```

### 4. Executar a Aplicação Streamlit

Inicie o servidor local da aplicação com o comando:

Bash

```
streamlit run app.py

```

Após a inicialização rápida, o Streamlit fornecerá um endereço local (geralmente `http://localhost:8501`) e abrirá o painel automaticamente no seu navegador web padrão.

## 📊 Estrutura dos Dados Esperada

O correto funcionamento do pipeline depende da presença das seguintes colunas principais nas bases de dados originais:

### Violência Doméstica (`violencia-domestica.csv`)

-   `DATA DO FATO`: Data da ocorrência (formato esperado `DD/MM/AAAA`).
    
-   `SEXO`: Filtro de género (o app isola os registos onde o valor é `FEMININO`).
    
-   `MUNICÍPIO`: Nome da cidade onde o facto ocorreu.
    
-   `CÚTIS`: Classificação étnico-racial da vítima (ex: Negra, Parda, Branca).
    
-   `TIPO DE INCIDENTE`: A tipificação jurídica do ato violento (Ameaça, Lesão Corporal, etc.).
    
-   `TIPO DE LOCAL`: O local do acontecimento (Residência, Via Pública, etc.).
    

### Homicídios e Feminicídios (`homicidios-e-feminicidios.csv`)

-   `DATA`: Data do óbito/fato.
    
-   `TIPIFICACAO`: Classificação legal do crime (utilizado para isolar os casos com o termo `Feminicídio`).
    
-   `MEIOS`: Instrumento ou método utilizado na execução (Arma de Fogo, Arma Branca, etc.).
    
-   `COR`: Perfil étnico-racial registado no óbito.
    

## 🛠️ Tecnologias Utilizadas

-   **[Python](https://www.python.org/):** Linguagem base de engenharia de dados.
    
-   **[Streamlit](https://streamlit.io/):** Framework para prototipagem rápida e deployment de apps de dados.
    
-   **[Plotly Express](https://plotly.com/python/):** Biblioteca para visualizações de dados imersivas e responsivas.
    
-   **[Pandas](https://pandas.pydata.org/):** Motor de alto desempenho para análise de matrizes de dados.
    

## ✒️ Licença

Este projeto está sob a licença MIT. Consulte o ficheiro `LICENSE` para obter mais detalhes.
