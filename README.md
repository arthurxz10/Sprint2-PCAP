# ⚡ ChargeGrid Intelligence — EV Challenge GoodWe 2026

**Grupo 5 | Turma 1CCPY | FIAP 2026**

> Plataforma inteligente de gerenciamento de carregamento de veículos elétricos para ambientes comerciais, desenvolvida como resposta ao desafio GoodWe HCA G2.

---

## 👥 Equipe

| Nome | RM |
|---|---|
| Jair Ferreira dos Santos Neto | 569682 |
| Matheus da Costa Gonçalves | 570756 |
| Yan Luiz Neves Lemos | 571717 |
| Arthur dos Santos Bezerra | 569721 |
| Carlos Henrique Fratezi | 571792 |

---

## 🎯 Problema

A GoodWe está expandindo suas soluções de carregamento de VE do ambiente residencial para o comercial. O **ChargeGrid Intelligence** enfrenta quatro desafios centrais:

- **Sobrecarga de demanda:** múltiplas recargas simultâneas causam ultrapassagem da demanda contratada, gerando multas
- **Falta de padronização:** equipamentos de diferentes fabricantes usam protocolos incompatíveis
- **Ausência de cobrança:** falta de sistema integrado de tarifação e pagamento digital
- **Ineficiência energética:** energia solar e bateria não são priorizadas, elevando o custo operacional

---

## 💡 Solução

O ChargeGrid Intelligence é uma plataforma com quatro módulos integrados:

```
┌─────────────────────────────────────────────────────────┐
│                 ChargeGrid Intelligence                  │
├──────────────┬──────────────┬──────────────┬────────────┤
│   Controle   │ Protocolos   │  Tarifação   │    IA /    │
│  de Demanda  │   Abertos    │ e Pagamento  │ Dashboard  │
│              │              │              │            │
│ Peak shaving │ OCPP 1.6/2.0 │ R$/kWh ou   │ Predição   │
│ automático   │ MODBUS       │ R$/min +Pix  │ de demanda │
│ via GoodWe   │ MQTT         │ + Cartão     │ Chatbot PT │
│ HCA G2       │ telemetria   │ dinâmica     │ Otimização │
└──────────────┴──────────────┴──────────────┴────────────┘
```

---

## 🗂️ Estrutura do Repositório

```
chargegrid-intelligence/
├── README.md                  # Este arquivo
├── docs/
│   ├── sprint1-pesquisa.pdf   # Documentação da Sprint 1
│   ├── sprint2-poc.md         # Documentação da Sprint 2
│   └── arquitetura.png        # Diagrama de arquitetura
├── poc/
│   └── dashboard/             # Prova de conceito — dashboard interativo
│       ├── index.html         # Dashboard principal (abre no navegador)
│       └── README.md          # Instruções do dashboard
├── simulacao/
│   └── peak_shaving.py        # Simulação do algoritmo de peak shaving
└── entrega/
    ├── sprint1.txt            # Arquivo de entrega Sprint 1
    └── sprint2.txt            # Arquivo de entrega Sprint 2
```

---

## 🚀 Prova de Conceito — Sprint 2

### O que foi desenvolvido

Um **dashboard interativo** simulando o funcionamento completo do ChargeGrid Intelligence:

| Funcionalidade | Descrição |
|---|---|
| Monitoramento em tempo real | Gráfico de demanda atualizado a cada segundo |
| Peak shaving automático | Ativado quando demanda ultrapassa 90% do limite contratado (108 kW) |
| 6 carregadores simultâneos | Status via OCPP — carregando, aguardando, peak shaving |
| Tarifação dinâmica | Pico (R$1,85), Fora-pico (R$0,72), Solar (R$0,38) por kWh |
| Orquestração de energia | Prioridade: Solar → Bateria → Rede elétrica |
| Recomendações de IA | Análise preditiva com alertas contextuais em português |
| Faturamento em tempo real | kWh entregue, sessões concluídas, receita acumulada |

### Como executar a PoC

1. Clone o repositório:
```bash
git clone https://github.com/arthurxz10/chargegrid-intelligence.git
cd chargegrid-intelligence
```

2. Abra o dashboard:
```bash
# Opção 1: Direto no navegador
open poc/dashboard/index.html

# Opção 2: Servidor local
python3 -m http.server 8000
# Acesse: http://localhost:8000/poc/dashboard/
```

3. Para rodar a simulação de peak shaving em Python:
```bash
python3 simulacao/peak_shaving.py
```

---

## 🏗️ Arquitetura do Sistema

```
                     ┌─────────────────┐
                     │   Dashboard IA  │
                     │  (Português)    │
                     └────────┬────────┘
                              │ MQTT
              ┌───────────────┼───────────────┐
              │               │               │
     ┌────────┴──────┐ ┌──────┴──────┐ ┌─────┴──────┐
     │   Módulo de   │ │  Módulo de  │ │  Módulo de │
     │   Demanda     │ │  Tarifação  │ │    IA      │
     │ Peak Shaving  │ │  Pix/Cartão │ │  Predição  │
     └────────┬──────┘ └──────┬──────┘ └─────┬──────┘
              │               │               │
              └───────────────┼───────────────┘
                              │ MODBUS / OCPP
              ┌───────────────┼───────────────┐
              │               │               │
     ┌────────┴──────┐ ┌──────┴──────┐ ┌─────┴──────┐
     │  GoodWe HCA   │ │  Carregador │ │  Inversor  │
     │     G2 #1     │ │   Ext. #2   │ │  GoodWe   │
     └───────────────┘ └─────────────┘ └────────────┘
```

### Fluxo lógico do peak shaving

```
Sensor lê demanda (kW)
        │
        ▼
  Demanda > 108 kW? ──NÃO──► Operação normal
        │
       SIM
        │
        ▼
Ativa peak shaving nos
carregadores com menor
prioridade (OCPP throttle)
        │
        ▼
  Demanda ≤ 108 kW? ──NÃO──► Desliga carregador
        │
       SIM
        │
        ▼
  Gera alerta no dashboard
  + log MQTT + notificação
```

---

## 📊 Resultados Projetados

| Indicador | Resultado |
|---|---|
| Redução na conta de energia | 20–40% |
| Payback estimado | ~2 anos |
| Multas de demanda | R$ 0 |
| Compatibilidade com carregadores | 100% (OCPP 2.0) |
| Uptime da plataforma | >99.5% |

---

## 🔧 Tecnologias e Protocolos

- **OCPP 1.6 / 2.0** — comunicação com carregadores EV
- **MODBUS TCP** — leitura do inversor GoodWe HCA G2
- **MQTT** — telemetria em tempo real
- **Python 3** — simulação e automação
- **HTML / CSS / JavaScript** — dashboard interativo
- **Chart.js** — visualização de dados em tempo real

---

## 📎 Links

- 🎥 [Vídeo Sprint 2 — YouTube](https://youtube.com) *(adicionar link após gravação)*
- 📋 [Quadro Kanban — GitHub Projects](https://github.com/users/arthurxz10/projects/2)
- 📄 [Documentação Sprint 1](docs/sprint1-pesquisa.pdf)

---

## 📅 Sprints

| Sprint | Status | Descrição |
|---|---|---|
| Sprint 1 | ✅ Entregue | Pesquisa, problemas e soluções |
| Sprint 2 | 🔄 Em andamento | Prova de conceito funcional |
| Sprint 3 | 🔲 Pendente | — |

---

*FIAP 2026 · EV Challenge GoodWe · Grupo 5 · Turma 1CCPY*
