# Dashboard de Inferência Bayesiana 📊

Repositório do Trabalho 1 da disciplina de Inferência Bayesiana (2/2025), com dados do Censo da Educação Superior de 2023.

## 🎯 Objetivo

Este projeto implementa um dashboard completo em Streamlit para análise bayesiana dos dados do Censo da Educação Superior 2023, permitindo explorar tendências, padrões e fazer inferências estatísticas sobre o ensino superior brasileiro.

## 🚀 Funcionalidades

### 📊 Análise Exploratória
- Estatísticas descritivas automáticas
- Visualizações interativas dos dados
- Detecção de outliers e valores ausentes
- Matriz de correlação e distribuições

### 🔬 Modelos Bayesianos
- **Regressão Linear Bayesiana**: Para relações lineares entre variáveis
- **Regressão Logística Bayesiana**: Para variáveis categóricas binárias
- **Modelos Hierárquicos**: Para dados agrupados (ex: por região, instituição)
- **Análise de Variância Bayesiana**: Comparação entre grupos
- **Modelos de Mistura**: Para populações heterogêneas

### 📈 Visualizações Interativas
- Gráficos de dispersão, histogramas e box plots
- Mapas de calor de correlação
- Séries temporais
- Visualizações 3D
- Gráficos específicos para resultados bayesianos

### 🔍 Comparação de Modelos
- Critérios de informação (WAIC, LOO)
- Diagnósticos de convergência (R-hat, ESS)
- Validação cruzada bayesiana

### 📋 Relatórios
- Exportação de resultados em CSV/Excel
- Relatórios executivos e técnicos
- Documentação metodológica

## 🛠️ Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/)**: Framework para criação do dashboard
- **[PyMC](https://docs.pymc.io/)**: Biblioteca para modelagem bayesiana probabilística
- **[ArviZ](https://arviz-devs.github.io/arviz/)**: Análise e visualização de resultados bayesianos
- **[Plotly](https://plotly.com/python/)**: Visualizações interativas
- **[Pandas](https://pandas.pydata.org/)**: Manipulação e análise de dados
- **[NumPy](https://numpy.org/)**: Computação numérica
- **[SciPy](https://scipy.org/)**: Algoritmos científicos
- **[Scikit-learn](https://scikit-learn.org/)**: Ferramentas de machine learning

## 📦 Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/jobsrobson/InferenciaBayesiana1.git
cd InferenciaBayesiana1
```

2. **Crie um ambiente virtual (recomendado):**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

## 🎮 Como Usar

1. **Inicie o dashboard:**
```bash
streamlit run app.py
```

2. **Acesse no navegador:**
   - O dashboard abrirá automaticamente em `http://localhost:8501`

3. **Carregue seus dados:**
   - Use o painel lateral para fazer upload de arquivos CSV
   - Os dados do Censo da Educação Superior devem estar no formato CSV

4. **Explore as funcionalidades:**
   - Navegue pelas diferentes seções usando o menu lateral
   - Configure e execute modelos bayesianos
   - Visualize resultados interativamente
   - Exporte relatórios e análises

## 📁 Estrutura do Projeto

```
InferenciaBayesiana1/
├── app.py                 # Aplicação principal do Streamlit
├── data_loader.py         # Módulo para carregamento de dados
├── bayesian_models.py     # Implementação dos modelos bayesianos
├── visualizations.py      # Módulo de visualizações interativas
├── utils.py              # Funções utilitárias
├── config.py             # Configurações do dashboard
├── requirements.txt      # Dependências do projeto
├── .gitignore           # Arquivos ignorados pelo Git
├── README.md            # Este arquivo
└── LICENSE              # Licença do projeto
```

## 📊 Dados

Este projeto foi desenvolvido para trabalhar com dados do **Censo da Educação Superior 2023** do INEP/MEC. Os dados podem ser obtidos em:

🔗 [Portal de Dados Abertos do INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior)

### Formato dos Dados
- **Formato**: CSV (UTF-8 ou Latin-1)
- **Separador**: Vírgula (,) ou ponto-e-vírgula (;)
- **Tamanho máximo**: 200MB
- **Colunas esperadas**: Variáveis do censo educacional (matrículas, cursos, instituições, etc.)

## 🔧 Configuração Avançada

### Modelos Bayesianos
Configure os parâmetros dos modelos no arquivo `config.py`:

```python
BAYESIAN_CONFIG = {
    'default_samples': 2000,    # Número de amostras MCMC
    'default_chains': 2,        # Número de cadeias
    'default_tune': 1000,       # Passos de tuning
    'target_accept': 0.8,       # Taxa de aceitação alvo
    'max_treedepth': 10         # Profundidade máxima da árvore
}
```

### Visualizações
Personalize cores e temas:

```python
VIZ_CONFIG = {
    'default_theme': 'plotly_white',
    'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c'],
    'default_height': 500,
    'default_width': 800
}
```

## 🧪 Testes

Para validar a instalação, você pode usar dados de exemplo:

```python
from utils import Utils

# Gerar dados de exemplo
sample_data = Utils.generate_sample_data(n_rows=1000)
print(sample_data.head())
```

## 📚 Exemplos de Uso

### Análise Exploratória
```python
# Carregar dados
data_loader = DataLoader()
data = data_loader.load_csv('censo_educacao_superior_2023.csv')

# Validar qualidade
validation = data_loader.validate_data()
print(validation)
```

### Modelo Bayesiano
```python
# Configurar modelo de regressão linear
model = BayesianModels()
results = model.linear_regression(X, y, n_samples=3000, n_chains=4)

# Verificar convergência
print(results['diagnostics'])
```

### Visualizações
```python
# Criar gráfico interativo
viz = Visualizations()
fig = viz.create_scatter_plot(data, 'matriculas', 'nota_enade', 
                             color_col='regiao')
fig.show()
```

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença especificada no arquivo [LICENSE](LICENSE).

## 👨‍💻 Autor

**Robson Jobs**
- 📧 Email: [seu-email@exemplo.com]
- 🐙 GitHub: [@jobsrobson](https://github.com/jobsrobson)

## 🙏 Agradecimentos

- **INEP/MEC** pelos dados do Censo da Educação Superior
- **Comunidade PyMC** pelas ferramentas de modelagem bayesiana
- **Streamlit** pelo framework de dashboard
- **Professores e colegas** da disciplina de Inferência Bayesiana

## 📋 Roadmap

- [ ] Implementação de mais modelos bayesianos avançados
- [ ] Integração com APIs de dados educacionais
- [ ] Módulo de machine learning bayesiano
- [ ] Visualizações geoespaciais
- [ ] Deploy automático em nuvem
- [ ] Testes automatizados
- [ ] Documentação interativa

## 🐛 Problemas Conhecidos

- PyMC pode apresentar warnings em algumas configurações
- Arquivos muito grandes (>200MB) podem causar lentidão
- Alguns gráficos bayesianos ainda estão em desenvolvimento

Para reportar bugs ou solicitar features, abra uma [issue](https://github.com/jobsrobson/InferenciaBayesiana1/issues).

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!
