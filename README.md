# 💰 FINANTEC - Gestão Financeira Inteligente

> 💡 Sistema web completo para controle de finanças pessoais, acompanhamento de metas, registro de movimentações e simulação de investimentos.

O **FINANTEC** é uma aplicação desenvolvida em Python (Flask) projetada para ajudar os usuários a organizarem sua vida financeira. Com uma interface limpa e responsiva (Bootstrap 5), o sistema permite gerenciar carteiras, acompanhar gráficos de evolução de patrimônio e planejar objetivos de longo prazo.

---

## 🚀 Funcionalidades Principais

* **Dashboard Financeiro:** Visão geral rápida dos seus saldos, extratos recentes e atalhos rápidos.
* **Múltiplas Carteiras:** Gestão do saldo principal separadamente do saldo guardado para metas.
* **Controle de Metas:** Crie objetivos (ex: "Viagem", "Carro Novo"), defina prazos e acompanhe o progresso através de barras de evolução.
* **Gestão de Movimentações:** * Registro de Novas Receitas (Entradas).
    * Registro de Novas Despesas (Saídas).
    * Transferências internas entre o Saldo Principal e suas Metas.
* **Simulador de Investimentos:** Projete como o seu saldo atual (ou um valor customizado) renderia em opções como Tesouro Selic, CDB (100% CDI) e Poupança.
* **Análise Visual (Gráficos):** Gráficos dinâmicos gerados com Chart.js para visualizar o Fluxo de Caixa (Receitas vs Despesas), o Progresso das Metas e a Tendência Histórica do seu dinheiro.
* **Segurança e Perfil:** Sistema completo de autenticação com senhas criptografadas (Bcrypt), edição de dados pessoais e opção de exclusão de conta.

---

## 🛠️ Tecnologias Utilizadas

### **Backend (Servidor & Lógica)**
* **Python 3:** Linguagem base da aplicação.
* **Flask:** Microframework web estrutural.
* **Flask-SQLAlchemy:** ORM (Object-Relational Mapping) para manipulação do banco de dados.
* **Flask-Bcrypt:** Criptografia e hash seguro de senhas.
* **PostgreSQL:** Banco de dados relacional em nuvem (hospedado via Neon DB).

### **Frontend (Interface & Visual)**
* **HTML5 / CSS3:** Estrutura e estilização.
* **Jinja2:** Motor de templates do Flask para renderização dinâmica (Server-Side Rendering).
* **Bootstrap 5:** Framework CSS para componentes e responsividade.
* **Bootstrap Icons:** Biblioteca de ícones.
* **Chart.js:** Biblioteca JavaScript para geração de gráficos dinâmicos.

---

## 📂 Estrutura de Pastas

```text
finantec/
├── app.py                  # Arquivo principal (Rotas e inicialização do Flask)
├── models.py               # Definição das tabelas do Banco de Dados (SQLAlchemy)
├── requirements.txt        # Dependências do projeto
├── README.md               # Documentação
└── templates/              # Telas e interfaces da aplicação (HTML/Jinja2)
    ├── cadastro.html
    ├── dashboard.html
    ├── editar_meta.html
    ├── graficos.html
    ├── Investimentos.html
    ├── login.html
    ├── metas.html
    ├── perfil.html
    └── transferir.html
