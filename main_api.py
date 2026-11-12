import math
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

import config
from database import init_db, log_evento, get_connection

app = FastAPI(title="Fila Zero - Fluxo e Dimensionamento", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

estado_loja = {
    "entradas_total": 0,
    "saidas_total": 0,
    "lotacao_atual": 0,
    "caixas_recomendados": 1
}

DIAS_SEMANA_PT = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]

class EventoPayload(BaseModel):
    tipo_evento: str
    entradas_total: int
    saidas_total: int
    lotacao_atual: int

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

def calcular_caixas_necessarios(lotacao: int) -> int:
    if lotacao <= 0:
        return 1
    clientes_em_compras = lotacao * config.TAXA_CONVERSAO
    tempo_permanencia_horas = config.TEMPO_MEDIO_LOJA_MIN / 60.0
    demanda_atendimento_hora = clientes_em_compras / tempo_permanencia_horas
    caixas = math.ceil(demanda_atendimento_hora / config.CAPACIDADE_CAIXA_HORA)
    return max(1, caixas)

@app.post("/api/evento")
async def receber_evento(payload: EventoPayload):
    global estado_loja
    estado_loja["entradas_total"] = payload.entradas_total
    estado_loja["saidas_total"] = payload.saidas_total
    estado_loja["lotacao_atual"] = payload.lotacao_atual
    estado_loja["caixas_recomendados"] = calcular_caixas_necessarios(payload.lotacao_atual)

    log_evento(payload.tipo_evento, payload.lotacao_atual)
    await manager.broadcast(estado_loja)
    return {"status": "sucesso", "estado": estado_loja}

@app.get("/api/status")
def obter_status():
    return estado_loja

@app.get("/api/analytics/geral")
def obter_analytics_geral():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT CAST(strftime('%w', timestamp) AS INTEGER) as dia_num, COUNT(*) as total
        FROM fluxo_eventos
        WHERE tipo_evento = 'ENTRADA'
        GROUP BY dia_num
    """)
    mapa_semana = {row["dia_num"]: row["total"] for row in cursor.fetchall()}
    visitas_por_semana = [
        {"dia": DIAS_SEMANA_PT[i], "total": mapa_semana.get(i, 0)}
        for i in range(7)
    ]

    dia_mais_movimentado = max(visitas_por_semana, key=lambda x: x["total"])

    cursor.execute("""
        SELECT DATE(timestamp) as data, COUNT(*) as total
        FROM fluxo_eventos
        WHERE tipo_evento = 'ENTRADA'
        GROUP BY data
        ORDER BY data DESC
        LIMIT 14
    """)
    visitas_por_data = [dict(row) for row in cursor.fetchall()]
    visitas_por_data.reverse()

    cursor.execute("""
        SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hora, COUNT(*) as total
        FROM fluxo_eventos
        WHERE tipo_evento = 'ENTRADA'
        GROUP BY hora
        ORDER BY total DESC
        LIMIT 1
    """)
    pico_row = cursor.fetchone()
    horario_pico = f"{pico_row['hora']:02d}:00" if pico_row else "--:--"
    visitas_pico = pico_row["total"] if pico_row else 0

    conn.close()
    return {
        "visitas_por_semana": visitas_por_semana,
        "dia_mais_movimentado": dia_mais_movimentado,
        "visitas_por_data": visitas_por_data,
        "horario_pico": horario_pico,
        "visitas_pico": visitas_pico
    }

@app.get("/api/analytics/dia")
def consultar_dia_especifico(data: str = Query(..., description="Data no formato YYYY-MM-DD")):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tipo_evento, COUNT(*) as total
        FROM fluxo_eventos
        WHERE DATE(timestamp) = ?
        GROUP BY tipo_evento
    """, (data,))
    totais = {row["tipo_evento"]: row["total"] for row in cursor.fetchall()}
    total_entradas = totais.get("ENTRADA", 0)
    total_saidas = totais.get("SAIDA", 0)

    cursor.execute("""
        SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hora, COUNT(*) as total
        FROM fluxo_eventos
        WHERE tipo_evento = 'ENTRADA' AND DATE(timestamp) = ?
        GROUP BY hora
    """, (data,))
    mapa_horas = {row["hora"]: row["total"] for row in cursor.fetchall()}

    fluxo_horario = [
        {"hora": f"{h:02d}:00", "total": mapa_horas.get(h, 0)}
        for h in range(7, 23)
    ]

    pico_dia = max(fluxo_horario, key=lambda x: x["total"]) if total_entradas > 0 else {"hora": "--:--", "total": 0}

    dt = datetime.strptime(data, "%Y-%m-%d")
    dia_semana_nome = DIAS_SEMANA_PT[(dt.weekday() + 1) % 7]

    conn.close()
    return {
        "data": data,
        "dia_semana": dia_semana_nome,
        "total_visitas": total_entradas,
        "total_saidas": total_saidas,
        "horario_pico": pico_dia["hora"],
        "visitas_no_pico": pico_dia["total"],
        "fluxo_horario": fluxo_horario
    }

@app.get("/api/historico")
def obter_historico():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM fluxo_eventos ORDER BY id DESC LIMIT 30")
    eventos = [dict(row) for row in cursor.fetchall()]

    cursor.execute("""
        SELECT DATE(timestamp) as data,
               CAST(strftime('%w', timestamp) AS INTEGER) as dia_num,
               COUNT(*) as total_visitas
        FROM fluxo_eventos
        WHERE tipo_evento = 'ENTRADA'
        GROUP BY data
        ORDER BY data DESC
        LIMIT 15
    """)
    resumo_diario = [
        {
            "data": row["data"],
            "dia_semana": DIAS_SEMANA_PT[row["dia_num"]],
            "total_visitas": row["total_visitas"]
        }
        for row in cursor.fetchall()
    ]

    conn.close()
    return {"eventos": eventos, "resumo_diario": resumo_diario}

@app.post("/api/popular_demo")
def popular_historico_demo():
    conn = get_connection()
    cursor = conn.cursor()

    volume_por_dia_semana = {
        0: 210, 1: 145, 2: 160, 3: 195, 4: 180, 5: 290, 6: 380
    }
    horas_possiveis = list(range(8, 22))
    pesos_horarios = [4, 7, 12, 14, 10, 6, 5, 6, 9, 14, 18, 16, 10, 5]

    registros = []
    hoje = datetime.now()

    for dias_atras in range(6, -1, -1):
        dia_alvo = hoje - timedelta(days=dias_atras)
        dia_sem_sql = (dia_alvo.weekday() + 1) % 7
        qtd_visitas = volume_por_dia_semana[dia_sem_sql] + random.randint(-15, 20)

        lotacao_simulada = 0
        for _ in range(qtd_visitas):
            hora_escolhida = random.choices(horas_possiveis, weights=pesos_horarios, k=1)[0]
            minuto = random.randint(0, 59)
            segundo = random.randint(0, 59)
            ts_entrada = dia_alvo.replace(hour=hora_escolhida, minute=minuto, second=segundo)

            lotacao_simulada += 1
            registros.append((ts_entrada.strftime("%Y-%m-%d %H:%M:%S"), "ENTRADA", lotacao_simulada))

            ts_saida = ts_entrada + timedelta(minutes=random.randint(15, 40))
            lotacao_simulada = max(0, lotacao_simulada - 1)
            registros.append((ts_saida.strftime("%Y-%m-%d %H:%M:%S"), "SAIDA", lotacao_simulada))

    registros.sort(key=lambda x: x[0])
    cursor.executemany(
        "INSERT INTO fluxo_eventos (timestamp, tipo_evento, lotacao_momento) VALUES (?, ?, ?)",
        registros
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "registros_inseridos": len(registros)}

@app.post("/api/recalibrar")
async def recalibrar_contadores(novas_entradas: int = 0, novas_saidas: int = 0):
    global estado_loja
    estado_loja["entradas_total"] = novas_entradas
    estado_loja["saidas_total"] = novas_saidas
    estado_loja["lotacao_atual"] = max(0, novas_entradas - novas_saidas)
    estado_loja["caixas_recomendados"] = calcular_caixas_necessarios(estado_loja["lotacao_atual"])
    await manager.broadcast(estado_loja)
    return {"status": "recalibrado", "estado": estado_loja}

@app.websocket("/ws/fluxo")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await websocket.send_json(estado_loja)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)