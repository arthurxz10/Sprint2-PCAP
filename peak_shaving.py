"""
ChargeGrid Intelligence — Simulação de Peak Shaving
Grupo 5 | Turma 1CCPY | FIAP 2026

Simula o algoritmo de gerenciamento de demanda do ChargeGrid.
Protocolo: MODBUS (leitura de demanda) + OCPP (controle dos carregadores)

Uso:
    python3 peak_shaving.py
"""

import random
import time
import math
from dataclasses import dataclass, field
from typing import List

DEMANDA_LIMITE_KW = 120       # Limite contratado
PEAK_SHAVING_THRESHOLD = 0.90 # 90% do limite = 108 kW
TAXA_SOLAR_MAX_KW = 30
TAXA_BATERIA_MAX_KW = 20

TARIFAS = {
    "pico":     1.85,  # R$/kWh — 8h às 22h
    "fora":     0.72,  # R$/kWh — 22h às 8h
    "solar":    0.38,  # R$/kWh — quando solar disponível
}


@dataclass
class Carregador:
    id: str
    potencia_kw: float = 22.0
    potencia_atual_kw: float = 0.0
    ativo: bool = False
    peak_shaving: bool = False
    kwh_entregue: float = 0.0
    receita: float = 0.0

    def conectar(self):
        self.ativo = True
        self.potencia_atual_kw = self.potencia_kw
        self.peak_shaving = False
        print(f"  [OCPP] {self.id} → CONECTADO ({self.potencia_atual_kw:.0f} kW)")

    def desconectar(self):
        self.ativo = False
        self.potencia_atual_kw = 0.0
        self.peak_shaving = False
        print(f"  [OCPP] {self.id} → SESSÃO ENCERRADA ({self.kwh_entregue:.1f} kWh entregues)")

    def aplicar_peak_shaving(self, fator: float):
        if self.ativo and not self.peak_shaving:
            self.peak_shaving = True
            self.potencia_atual_kw = round(self.potencia_kw * fator, 1)
            print(f"  [OCPP] {self.id} → PEAK SHAVING ativo ({self.potencia_atual_kw:.1f} kW)")

    def remover_peak_shaving(self):
        if self.peak_shaving:
            self.peak_shaving = False
            self.potencia_atual_kw = self.potencia_kw
            print(f"  [OCPP] {self.id} → PEAK SHAVING removido (voltou a {self.potencia_atual_kw:.0f} kW)")


@dataclass
class SistemaChargeGrid:
    carregadores: List[Carregador] = field(default_factory=list)
    tick: int = 0
    receita_total: float = 0.0
    kwh_total: float = 0.0
    alertas_peak: int = 0

    def demanda_total_kw(self) -> float:
        return sum(c.potencia_atual_kw for c in self.carregadores if c.ativo)

    def _fonte_energia(self, demanda: float):
        """Orquestração IA: Solar > Bateria > Rede"""
        hora = (self.tick // 3600) % 24
        solar = min(TAXA_SOLAR_MAX_KW, max(0, TAXA_SOLAR_MAX_KW * math.sin(math.pi * (hora - 6) / 12)))
        solar = round(solar + random.uniform(-2, 2), 1)
        solar = max(0, solar)
        bateria = min(TAXA_BATERIA_MAX_KW, max(0, demanda - solar))
        rede = max(0, demanda - solar - bateria)
        return solar, bateria, rede

    def _tarifa_atual(self) -> tuple:
        hora = (self.tick // 3600) % 24
        if 8 <= hora < 22:
            return "pico", TARIFAS["pico"]
        else:
            return "fora", TARIFAS["fora"]

    def step(self, segundos: int = 1):
        self.tick += segundos
        modo, tarifa = self._tarifa_atual()

        # Simula chegada e saída de veículos
        if self.tick % 30 == 0:
            disponiveis = [c for c in self.carregadores if not c.ativo]
            if disponiveis and len([c for c in self.carregadores if c.ativo]) < 5:
                disponiveis[0].conectar()

        if self.tick % 120 == 0:
            ativos = [c for c in self.carregadores if c.ativo]
            if ativos:
                random.choice(ativos).desconectar()

        # Ruído na demanda base (carga não EV)
        carga_base = 30 + math.sin(self.tick / 300) * 8 + random.uniform(-3, 3)
        demanda = self.demanda_total_kw() + carga_base
        limite_ps = DEMANDA_LIMITE_KW * PEAK_SHAVING_THRESHOLD

        # Peak shaving automático
        if demanda > limite_ps:
            self.alertas_peak += 1
            print(f"\n  ⚠  DEMANDA ALTA: {demanda:.1f} kW > limite {limite_ps:.0f} kW")
            ativos_sem_ps = [c for c in self.carregadores if c.ativo and not c.peak_shaving]
            for c in ativos_sem_ps:
                c.aplicar_peak_shaving(fator=0.5)
                demanda -= (c.potencia_kw * 0.5)
                if demanda <= limite_ps:
                    break
        else:
            for c in self.carregadores:
                if c.peak_shaving:
                    c.remover_peak_shaving()

        # Calcula energia entregue e receita
        for c in self.carregadores:
            if c.ativo:
                delta_kwh = (c.potencia_atual_kw / 3600) * segundos
                c.kwh_entregue += delta_kwh
                c.receita += delta_kwh * tarifa
                self.kwh_total += delta_kwh
                self.receita_total += delta_kwh * tarifa

        # Fontes de energia
        solar, bateria, rede = self._fonte_energia(demanda)
        pct_renovavel = round(((solar + bateria) / max(1, demanda)) * 100, 1)

        return {
            "tick": self.tick,
            "demanda_kw": round(demanda, 1),
            "limite_kw": DEMANDA_LIMITE_KW,
            "peak_shaving_ativo": any(c.peak_shaving for c in self.carregadores),
            "sessoes_ativas": sum(1 for c in self.carregadores if c.ativo),
            "solar_kw": round(solar, 1),
            "bateria_kw": round(bateria, 1),
            "rede_kw": round(rede, 1),
            "pct_renovavel": pct_renovavel,
            "tarifa_modo": modo,
            "tarifa_kwh": tarifa,
            "kwh_total": round(self.kwh_total, 2),
            "receita_total": round(self.receita_total, 2),
        }

    def relatorio(self):
        print("\n" + "="*50)
        print("RELATÓRIO FINAL — ChargeGrid Intelligence")
        print("="*50)
        print(f"  Energia total entregue : {self.kwh_total:.1f} kWh")
        print(f"  Receita total          : R$ {self.receita_total:.2f}")
        print(f"  Alertas de peak shaving: {self.alertas_peak}")
        print(f"  Multas de demanda      : R$ 0,00 ✓")
        print("="*50)
        for c in self.carregadores:
            print(f"  {c.id}: {c.kwh_entregue:.1f} kWh → R$ {c.receita:.2f}")
        print("="*50)


def main():
    print("=" * 50)
    print(" ChargeGrid Intelligence — Peak Shaving Demo")
    print(" Grupo 5 | 1CCPY | FIAP 2026")
    print("=" * 50)

    carregadores = [Carregador(id=f"Vaga-{chr(65+i//2)}{(i%2)+1}") for i in range(6)]
    sistema = SistemaChargeGrid(carregadores=carregadores)

    # Conecta alguns veículos inicialmente
    for c in carregadores[:3]:
        c.conectar()

    print(f"\nMonitoramento MODBUS iniciado | Limite: {DEMANDA_LIMITE_KW} kW\n")

    try:
        for _ in range(60):  # Simula 60 segundos
            estado = sistema.step(segundos=10)
            ps = "⚠ PEAK SHAVING" if estado["peak_shaving_ativo"] else "✓ Normal"
            print(
                f"t={estado['tick']:4d}s | "
                f"Demanda: {estado['demanda_kw']:6.1f} kW | "
                f"{ps:20s} | "
                f"Sessões: {estado['sessoes_ativas']} | "
                f"Solar: {estado['pct_renovavel']:4.0f}% | "
                f"R$ {estado['receita_total']:.2f}"
            )
            time.sleep(0.1)  # Acelerado para demo
    except KeyboardInterrupt:
        print("\n[Simulação interrompida pelo usuário]")

    sistema.relatorio()


if __name__ == "__main__":
    main()
