# 🚀 Guia de Início Rápido

## Instalação em 3 Passos

### 1. Clone e Configure
```bash
git clone https://github.com/jobsrobson/InferenciaBayesiana1.git
cd InferenciaBayesiana1
pip install -r requirements.txt
```

### 2. Execute o Dashboard
```bash
streamlit run app.py
```

### 3. Acesse no Navegador
- Abra: http://localhost:8501
- Upload seus dados CSV na barra lateral
- Explore as diferentes seções do menu

## 🎯 Demonstração Rápida

### Teste com Dados de Exemplo
```bash
python demo.py
```

Este script irá:
- ✅ Gerar dados de exemplo do censo educacional
- ✅ Demonstrar carregamento e validação de dados
- ✅ Criar visualizações interativas
- ✅ Aplicar filtros e exportar resultados

## 📊 Estrutura do Dashboard

### Páginas Disponíveis:
1. **🏠 Início**: Visão geral e status do sistema
2. **📊 Análise Exploratória**: Estatísticas e distribuições
3. **🔬 Modelos Bayesianos**: Configuração e execução de modelos
4. **📈 Visualizações**: Gráficos interativos personalizados
5. **🔍 Comparação de Modelos**: Métricas e diagnósticos
6. **📋 Relatórios**: Exportação e documentação
7. **ℹ️ Sobre**: Informações do projeto

## 🔧 Configuração Avançada

### Para Modelagem Bayesiana Completa:
```bash
pip install pymc arviz
```

### Personalizar Configurações:
Edite o arquivo `config.py` para:
- Alterar cores e temas
- Configurar parâmetros dos modelos
- Definir limites de dados
- Personalizar mensagens

## 📁 Formato dos Dados

### Dados Esperados (CSV):
- **Encoding**: UTF-8 ou Latin-1
- **Separador**: Vírgula (,) ou ponto-e-vírgula (;)
- **Tamanho máximo**: 200MB
- **Colunas sugeridas**:
  - Identificadores (universidade, curso, região)
  - Métricas numéricas (matrículas, vagas, notas)
  - Categorias (tipo de instituição, modalidade)

### Exemplo de Estrutura:
```csv
universidade,curso,regiao,matriculas,vagas,taxa_evasao,nota_enade,ano
USP,Engenharia,Sudeste,1500,200,0.15,4.2,2023
UNICAMP,Medicina,Sudeste,300,50,0.08,4.8,2023
```

## 🎮 Funcionalidades Principais

### 📊 Análise Exploratória
- Upload e preview de dados
- Estatísticas descritivas automáticas
- Detecção de outliers e valores ausentes
- Matriz de correlação interativa

### 🔬 Modelos Bayesianos
- Regressão Linear e Logística Bayesiana
- Modelos Hierárquicos
- Análise de Variância Bayesiana
- Diagnósticos de convergência

### 📈 Visualizações
- Gráficos de dispersão e histogramas
- Box plots e violin plots
- Mapas de calor
- Séries temporais
- Visualizações 3D

## ❗ Solução de Problemas

### Erro: "PyMC não está disponível"
```bash
pip install pymc arviz
```

### Erro: "Arquivo muito grande"
- Verifique se o arquivo tem menos de 200MB
- Use amostragem se necessário
- Divida em chunks menores

### Dashboard não abre
- Verifique se a porta 8501 está livre
- Tente: `streamlit run app.py --server.port 8502`

### Erro de encoding
- Salve o CSV em UTF-8
- Ou tente Latin-1 nas configurações

## 📞 Suporte

- 📖 **Documentação**: Veja README.md completo
- 🐛 **Bugs**: Abra uma issue no GitHub
- 💡 **Dúvidas**: Consulte a seção "Sobre" no dashboard
- 📧 **Contato**: Robson Jobs

---

🎉 **Pronto!** Seu dashboard de Inferência Bayesiana está funcionando!