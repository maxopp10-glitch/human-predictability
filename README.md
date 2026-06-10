# Human Predictability

Projeto de Ciência de Dados para investigar se escolhas humanas simples apresentam padrões previsíveis ao longo do tempo.

## Objetivo

O projeto busca responder uma pergunta simples:

> As pessoas tendem a fazer as mesmas escolhas quando recebem perguntas extremamente simples?

Exemplos:

- Escolha um número entre 0 e 100
- Escolha uma cor
- Cara ou Coroa
- Escolha uma letra
- Escolha uma direção
- Escolha um animal
- Escolha uma forma geométrica

As respostas são coletadas anonimamente, armazenadas em Google Sheets e analisadas em tempo real através de um dashboard interativo.

---

## Aplicação Online

Acesse:

https://human-predictability-max.streamlit.app

---

## Funcionalidades

### Coleta de dados

- Identificação anônima por usuário
- Limite semanal de respostas por experimento
- Registro de:
  - resposta escolhida
  - horário
  - dia da semana
  - semana do ano
  - tempo de resposta
  - idade
  - sexo (opcional)

### Dashboard em tempo real

- Participantes totais
- Respostas totais
- Distribuição das respostas
- Resposta dominante
- Índice de previsibilidade
- Ranking de previsibilidade
- Tempo médio de resposta

---

## Tecnologias Utilizadas

### Frontend

- Streamlit

### Armazenamento

- Google Sheets

### Linguagem

- Python

### Bibliotecas

- pandas
- streamlit
- gspread
- google-auth
- streamlit-cookies-manager

---

## Estrutura do Projeto

```text
Human_Predictability_Project/

├── app/
│   └── app.py
│
├── src/
│   ├── train_model.py
│   └── predict.py
│
├── data/
│
├── requirements.txt
│
└── README.md
```

---

## Métricas Atuais

### Índice de Previsibilidade

Calculado como:

```text
(resposta mais frequente / total de respostas) * 100
```

Exemplo:

```text
Azul = 42%
```

Logo:

```text
Índice de previsibilidade = 42%
```

---

## Próximas Etapas

### Curto Prazo

- Dashboard de tendências temporais
- Evolução semanal das respostas
- Exportação automática dos dados

### Médio Prazo

- Treinamento de modelos de Machine Learning
- Identificação de padrões ocultos
- Predição de respostas futuras

### Longo Prazo

- API pública
- Banco de dados dedicado
- Dashboard avançado
- Publicação dos resultados

---

## Motivação

Este projeto foi criado para explorar uma questão interessante da psicologia comportamental:

> Quando acreditamos estar escolhendo livremente, estamos realmente escolhendo livremente?

Utilizando coleta de dados em larga escala e técnicas de Data Science, o projeto busca medir o grau de previsibilidade das escolhas humanas mais simples.

---

## Autor

Max Oppermann

- Engenharia de Materiais – UFRGS
- Data Analytics
- Machine Learning
- QA Automation