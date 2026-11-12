# 🛒 Fila Zero — Supervisório de Fluxo de Visitantes e Dimensionamento de Caixas

Sistema de monitoramento inteligente para supermercados e varejo baseado em **Visão Computacional (YOLOv8)**, **FastAPI** e **SQLite**. O software contabiliza em tempo real o fluxo de entrada e saída de clientes, calcula a lotação instantânea da loja, recomenda a quantidade ideal de caixas abertos para evitar filas e armazena o histórico diário para análise de movimentação.

---

## ✨ Funcionalidades Principais

* **Contagem Bidirecional por Visão Computacional:** Detecta e rastreia pessoas cruzando uma linha virtual configurável, diferenciando automaticamente **Entradas** e **Saídas**.
* **Dimensionamento Dinâmico de Caixas:** Calcula em tempo real quantos operadores de checkout precisam estar ativos com base na lotação atual, taxa de conversão em compras e capacidade de atendimento por hora.
* **Dashboard Web em Tempo Real (WebSocket):**
  * **📡 Monitoramento Ao Vivo & Caixas:** KPIs instantâneos, alerta visual de aumento de fluxo, gráfico dinâmico e painel de simulação para testes sem câmera.
  * **📅 Movimentação por Dia & Semana:** Consulta por data específica no calendário, distribuição horária (07h às 22h) e ranking dos dias da semana mais movimentados.
  * **🗄️ Registros do Banco (SQLite):** Visualização direta do consolidado diário e dos últimos eventos capturados pelo sensor.
* **Persistência Local Automática:** Grava todos os eventos e resumos diários no banco de dados `mercado_analytics.db`.

---

## 🛠️ Tecnologias Utilizadas

* **Visão Computacional:** Python, OpenCV e Ultralytics YOLOv8 (`yolov8n.pt`)
* **Backend & Tempo Real:** FastAPI, Uvicorn e WebSockets
* **Banco de Dados:** SQLite3
* **Frontend & Gráficos:** HTML5, Tailwind CSS e Chart.js

---

## 📁 Estrutura do Projeto

| Arquivo | Descrição |
| :--- | :--- |
| `config.py` | Centraliza as configurações da câmera/vídeo, sensibilidade da IA, altura da linha e parâmetros de cálculo dos caixas. |
| `vision_sensor.py` | Módulo de visão computacional que processa o vídeo ou webcam e envia os eventos de cruzamento para a API. |
| `main_api.py` | Servidor backend FastAPI que gerencia o banco SQLite, calcula a demanda de caixas e atualiza o painel via WebSocket. |
| `database.py` | Cria e gerencia as tabelas `fluxo_eventos` e `resumo_diario` no arquivo `mercado_analytics.db`. |
| `index.html` | Interface web interativa com abas de monitoramento ao vivo, gráficos analíticos e consulta histórica. |
| `requirements.txt` | Lista de bibliotecas Python necessárias para executar o projeto. |

---

## 🚀 Como Instalar e Executar

### Pré-requisitos
* **Python 3.10 ou superior** instalado no computador.

### 1. Baixar o projeto
Clone o repositório ou clique em **`<> Code` > `Download ZIP`** no GitHub e extraia a pasta no seu computador.

### 2. Criar e ativar o ambiente virtual (`venv`)
Abra o terminal dentro da pasta do projeto e execute:

**No Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
