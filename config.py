import os

# Nome do arquivo de vídeo na pasta do projeto
CAMERA_SOURCE = "shopping.mp4"

# Configurações da IA (YOLOv8)
YOLO_MODEL_PATH = "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.40
TARGET_SIZE = 320
SKIP_FRAMES = 2          # Processa 1 a cada 2 quadros para manter o vídeo fluido
LINE_Y_RATIO = 0.5       # Altura da linha azul (0.5 = meio exato da tela)

# True = Mostra a janela do vídeo com as caixas, linha e placar ao vivo
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