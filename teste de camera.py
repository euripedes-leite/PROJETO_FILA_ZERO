import cv2
from ultralytics import YOLO

# 1. Carrega o modelo YOLOv8 (versão nano, mais rápida)
model = YOLO("yolov8n.pt")

# 2. Inicia a captura da webcam
# O número 0 representa a câmera padrão do notebook. 
# Se tiver uma webcam externa, pode tentar mudar para 1 ou 2.
cap = cv2.VideoCapture(0)

print("Iniciando a câmera. Pressione 'q' na janela de vídeo para sair.")

while True:
    # Captura frame por frame da câmera
    sucesso, frame = cap.read()
    
    # Se der erro na leitura (ex: câmera em uso por outro app), ele para
    if not sucesso:
        print("Erro: Não foi possível acessar a câmera do notebook.")
        break

    # 3. Executa a IA no frame
    # O parâmetro classes=[0] força o YOLO a detectar APENAS pessoas.
    resultados = model(frame, stream=True, classes=[0])

    # 4. Desenha as caixas ao redor das pessoas detectadas
    for resultado in resultados:
        frame_anotado = resultado.plot()

    # 5. Exibe o resultado ao vivo
    cv2.imshow("IA - Identificando Pessoas (Webcam)", frame_anotado)

    # 6. Aguarda a tecla 'q' ser pressionada para encerrar o programa
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Limpeza: libera a câmera e fecha as janelas do sistema
cap.release()
cv2.destroyAllWindows()