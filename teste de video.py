import cv2
from ultralytics import YOLO

# Carrega o modelo
model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture("shopping.mp4")

# Variáveis para o nosso contador
entradas = 0
saidas = 0
pessoas_rastreadas = {} # Dicionário para guardar a posição anterior de cada pessoa (ID)

while True:
    sucesso, frame = cap.read()
    if not sucesso:
        print("Fim do vídeo!")
        break

    # Pega a altura e largura do vídeo para posicionar a linha
    altura, largura = frame.shape[:2]
    
    # Define a altura da linha imaginária (Aqui configuramos para o exato meio da tela)
    # Se quiser a linha mais para baixo, aumente esse valor (ex: altura // 2 + 100)
    linha_y = altura // 2 

    # 1. Usa o .track() ao invés do modelo normal. 
    # O 'persist=True' diz para a IA lembrar dos IDs das pessoas entre os frames
    results = model.track(frame, persist=True, classes=[0], conf=0.40)
    
    # 2. Pega a imagem já desenhada com as caixas do YOLO
    annotated_frame = results[0].plot()

    # 3. Desenha a nossa linha imaginária na cor Azul (BGR: 255, 0, 0)
    cv2.line(annotated_frame, (0, linha_y), (largura, linha_y), (255, 0, 0), 3)

    # Verifica se a IA detectou e conseguiu rastrear IDs nesse frame
    if results[0].boxes.id is not None:
        
        # Extrai as coordenadas das caixas e os IDs das pessoas
        boxes = results[0].boxes.xyxy.cpu().numpy()
        track_ids = results[0].boxes.id.cpu().numpy()
        
        for box, track_id in zip(boxes, track_ids):
            # Coordenadas da pessoa (x1,y1 é o topo esquerdo | x2,y2 é o fundo direito)
            x1, y1, x2, y2 = box
            
            # Calcula o centro Y da pessoa para saber exatamente onde ela está pisando/passando
            cy = int((y1 + y2) / 2)
            cx = int((x1 + x2) / 2)
            
            # Desenha um pontinho amarelo no centro da pessoa
            cv2.circle(annotated_frame, (cx, cy), 5, (0, 255, 255), -1)

            # --- LÓGICA DE CRUZAMENTO DA LINHA ---
            if track_id in pessoas_rastreadas:
                posicao_anterior_y = pessoas_rastreadas[track_id]
                
                # Se estava acima da linha e o centro desceu cruzando a linha -> SAÍDA
                if posicao_anterior_y < linha_y and cy >= linha_y:
                    saidas += 1
                    cv2.line(annotated_frame, (0, linha_y), (largura, linha_y), (0, 0, 255), 5) # Pisca vermelho
                    
                # Se estava abaixo da linha e o centro subiu cruzando a linha -> ENTRADA
                elif posicao_anterior_y > linha_y and cy <= linha_y:
                    entradas += 1
                    cv2.line(annotated_frame, (0, linha_y), (largura, linha_y), (0, 255, 0), 5) # Pisca verde
            
            # Atualiza a posição atual da pessoa na memória para o próximo frame
            pessoas_rastreadas[track_id] = cy

    # 4. Escreve o placar de Entradas e Saídas na tela
    cv2.putText(annotated_frame, f"Entradas: {entradas}", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
    cv2.putText(annotated_frame, f"Saidas: {saidas}", (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)

    # Redimensiona para caber na tela
    frame_redimensionado = cv2.resize(annotated_frame, (1024, 576))
    
    cv2.imshow("Teste YOLO - Contador de Fluxo", frame_redimensionado)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()