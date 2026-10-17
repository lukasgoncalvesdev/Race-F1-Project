
# 🏎️ Race Data Analyzer

Dashboard para análise de resultados de corridas de Fórmula 1, desenvolvido em Python.

## Sobre o projeto

O Race Data Analyzer consulta dados de corridas por meio da API Jolpica F1 e transforma esses dados em tabelas, estatísticas, gráficos e relatórios.

O projeto foi desenvolvido como estudo prático de programação, análise de dados e visualização aplicada ao automobilismo.

## Funcionalidades

- Consulta de resultados por temporada e etapa.
- Classificação dos pilotos.
- Análise de posições de largada e chegada.
- Cálculo de pontos por equipe.
- Visualização de gráficos interativos.
- Exportação de resultados em CSV.
- Geração e download de relatório em texto.

## Tecnologias utilizadas

- Python
- Streamlit
- Pandas
- Matplotlib
- Requests
- API Jolpica F1

## Como executar

### 1. Instale o Python

Instale uma versão do Python compatível com as dependências do projeto.

### 2. Clone o repositório

```bash
git clone URL_DO_SEU_REPOSITORIO
cd NOME_DO_REPOSITORIO
```

Substitua `URL_DO_SEU_REPOSITORIO` e `NOME_DO_REPOSITORIO` pelos dados do seu repositório.

### 3. Crie um ambiente virtual

No Windows:

```powershell
py -3.14 -m venv .venv
```

### 4. Ative o ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Instale as dependências

```powershell
python -m pip install -r requirements.txt
```

### 6. Execute o dashboard

```powershell
python -m streamlit run app.py
```

O Streamlit exibirá o endereço local para abrir o dashboard no navegador.

## Fonte dos dados

Os dados são consultados por meio da API Jolpica F1.

A disponibilidade e a cobertura dos dados podem variar conforme a temporada e a corrida.

## Autor

Projeto pessoal de estudo em programação e análise de dados aplicada ao automobilismo.
