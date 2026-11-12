import os

# "AUTO" procura automaticamente a webcam conectada (índices 0, 1, 2, 3)
# Se usar câmera IP no celular, coloque o link entre aspas (ex: "http://192.168.1.50:8080/video")
CAMERA_SOURCE = "AUTO"

# Configurações da IA (YOLOv8)
YOLO_MODEL_PATH = "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.40
TARGET_SIZE = 320
SKIP_FRAMES = 1          # 1 = rastreia todos os quadros da câmera sem atraso
LINE_Y_RATIO = 0.5       # Altura da linha azul (0.5 = meio da imagem)

# True = Abre a janela da câmera mostrando a detecção e o placar ao vivo
SHOW_VIDEO = True

# Configurações de Negócio
CAPACIDADE_CAIXA_HORA = 20
TEMPO_MEDIO_LOJA_MIN = 30
TAXA_CONVERSAO = 0.8

# Configurações de Alerta (Telegram)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_BOT_TOKEN_AQUI")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "SEU_CHAT_ID_AQUI")
ALERT_THRESHOLD_PER_MIN = 15.0
ALERT_WINDOW_MINUTES = 3
ALERT_COOLDOWN_MINUTES = 10

# Endpoint do Backend FastAPI
BACKEND_API_URL = "http://127.0.0.1:8000/api/evento"