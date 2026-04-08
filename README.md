# 📦 Sistema de Devoluções — MIC

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-CC2927?style=for-the-badge&logo=databricks&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Status](https://img.shields.io/badge/Status-Em%20Produção-brightgreen?style=for-the-badge)

> Sistema web desenvolvido para gerenciar o fluxo completo de devoluções de mercadorias, desde o lançamento pelo vendedor até a finalização pelo financeiro — com controle de acesso por perfil, upload de notas fiscais e geração de relatórios em PDF.

🌐 **[Acesse o sistema em produção](https://andredevolucoes.pythonanywhere.com/)**

---

## 🖥️ Screenshots

<table>
  <tr>
    <td align="center"><b>Tela de Login</b></td>
    <td align="center"><b>Dashboard — Vendedor</b></td>
  </tr>
  <tr>
    <td><img src="./screenshots/login.PNG" alt="Login" width="400"/></td>
    <td><img src="./screenshots/dashboard-vendedor.png" alt="Dashboard Vendedor" width="400"/></td>
  </tr>
  <tr>
    <td align="center"><b>Nova Devolução</b></td>
    <td align="center"><b>Dashboard — Gerente</b></td>
  </tr>
  <tr>
    <td><img src="./screenshots/nova-devolucao.png" alt="Nova Devolução" width="400"/></td>
    <td><img src="./screenshots/dashboard-gerente.png" alt="Dashboard Gerente" width="400"/></td>
  </tr>
  <tr>
    <td align="center"><b>Gestão de Usuários</b></td>
    <td align="center"><b>Geração de Relatório PDF</b></td>
  </tr>
  <tr>
    <td><img src="./screenshots/usuarios.png" alt="Usuários" width="400"/></td>
    <td><img src="./screenshots/relatorio.png" alt="Relatório" width="400"/></td>
  </tr>
</table>

---

## 🚀 Funcionalidades

- 🔐 **Autenticação** com login e controle de sessão
- 👥 **Controle de acesso por perfil**: Vendedor, Conferente, Gerente e Financeiro
- 📋 **Fluxo completo de devolução** com etapas rastreáveis:
  - `Aguardando Validação` → `Aguardando Aprovação` → `Aguardando Chegada` → `Aguardando Baixa no Boleto` → `Finalizado`
- 📎 **Upload de notas fiscais em PDF** vinculadas à devolução
- 🔍 **Busca e filtros** por cliente, NF do cliente e NF interna
- 📊 **Geração de relatório em PDF** por período (exclusivo para gerentes)
- ✏️ **Edição de devoluções** enquanto ainda estão na etapa inicial
- 🕐 **Registro de datas e responsáveis** em cada etapa do fluxo

---

## 🏗️ Estrutura do Projeto

```
devolucoes_app/
├── app.py              # Rotas e lógica principal da aplicação
├── models.py           # Modelos do banco de dados (Usuario, Devolucao, DevolucaoPDF)
├── config.py           # Configurações da aplicação
├── Procfile            # Configuração para deploy
├── requirements.txt    # Dependências do projeto
├── static/             # Arquivos estáticos (CSS, uploads)
├── screenshots/        # Screenshots do sistema
└── templates/          # Templates HTML (Jinja2)
```

---

## ⚙️ Como rodar localmente

### Pré-requisitos

- Python 3.10+
- pip

### Instalação

```bash
# Clone o repositório
git clone https://github.com/andregabriel-dev/devolucoes_app.git
cd devolucoes_app

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Inicie a aplicação
python app.py
```

Acesse em: `http://localhost:5000`

> Na primeira execução, o sistema cria automaticamente o banco de dados e os usuários padrão.

---

## 👤 Perfis de Acesso

| Perfil | Permissões |
|--------|-----------|
| **Vendedor** | Lança novas devoluções, acompanha status, recebe mercadorias |
| **Conferente** | Confere e valida as devoluções lançadas |
| **Gerente** | Aprova envios, gerencia usuários, gera relatórios em PDF |
| **Financeiro** | Realiza a baixa do boleto e finaliza o processo |

---

## 🔄 Fluxo de Status

```
Nova Devolução (Vendedor)
        ↓
Aguardando Validação
        ↓
Aguardando Aprovação (Conferente)
        ↓
Aguardando Chegada (Gerente)
        ↓
Aguardando Baixa no Boleto (Vendedor/Conferente)
        ↓
Finalizado (Financeiro)
```

---

## 🛠️ Tecnologias Utilizadas

- **[Flask](https://flask.palletsprojects.com/)** — Framework web
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM para banco de dados
- **[ReportLab](https://www.reportlab.com/)** — Geração de relatórios em PDF
- **[Werkzeug](https://werkzeug.palletsprojects.com/)** — Segurança de senhas e upload de arquivos
- **[PythonAnywhere](https://www.pythonanywhere.com/)** — Hospedagem em produção
- **Jinja2** — Templates HTML dinâmicos

---

## 👨‍💻 Autor

Desenvolvido por **André Gabriel**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/andré-gabriel-6a2333208/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/andregabriel-dev)
