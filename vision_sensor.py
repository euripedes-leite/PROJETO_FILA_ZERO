import os
import cv2
import requests
from ultralytics import YOLO
import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resolver_caminho(arquivo: str) -> str:
    """Garante que o arquivo seja encontrado na pasta do projeto."""
    if os.path.isabs(arquivo) or arquivo.startswith(("http://", "https://", "rtsp://")):
        return arquivo
    return os.path.join(BASE_DIR, arquivo)

def notificar_backend(tipo: str, entradas: int, saidas: int):
    payload = {
        "tipo_evento": tipo,
        "entradas_total": entradas,
        "saidas_total": saidas,
        "lotacao_atual": max(0, entradas - saidas)
    }
    try:
        requests.post(config.BACKEND_API_URL, json=payload, timeout=0.5)
        print(f"[SENSOR] {tipo} | Entradas: {entradas} | Saídas: {saidas} | Na Loja: {payload['lotacao_atual']}")
    except Exception:
        print(f"[AVISO] {tipo} contado no vídeo, mas o servidor (Terminal 1) está desligado.")

def run_sensor():
    caminho_modelo = resolver_caminho(config.YOLO_MODEL_PATH)
    caminho_video = resolver_caminho(config.CAMERA_SOURCE)

    print(f"[SENSOR] Carregando modelo {config.YOLO_MODEL_PATH}...")
    model = YOLO(caminho_modelo)

    cap = cv2.VideoCapture(caminho_video)
    if not cap.isOpened():
        print(f"[ERRO] Não foi possível abrir o vídeo: {caminho_video}")
        return

    entradas = 0
    saidas = 0
    pessoas_rastreadas = {}
    frame_count = 0

    print("[SENSOR] Vídeo em loop iniciado! Pressione a tecla 'Q' na janela do vídeo para encerrar.")

    while True:
        sucesso, frame = cap.read()

        # Quando o vídeo chega ao fim, volta ao início em loop contínuo
        if not sucesso:
            print("[SENSOR] Reiniciando ciclo do vídeo em loop...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            pessoas_rastreadas.clear()
            continue

        frame_count += 1
        if frame_count % config.SKIP_FRAMES != 0:
            continue

        altura, largura = frame.shape[:2]
        linha_y = int(altura * config.LINE_Y_RATIO)

        # Rastreamento de pessoas com YOLOv8
        results = model.track(
            frame,
            imgsz=config.TARGET_SIZE,
            persist=True,
            classes=[0],
            conf=config.CONFIDENCE_THRESHOLD,
            verbose=False
        )

        annotated_frame = results[0].plot()
        cor_linha = (255, 0, 0)  # Azul padrão
        espessura_linha = 3

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box
                cy = int((y1 + y2) / 2)
                cx = int((x1 + x2) / 2)

                # Ponto amarelo no centro da pessoa
                cv2.circle(annotated_frame, (cx, cy), 5, (0, 255, 255), -1)

                if track_id in pessoas_rastreadas:
                    posicao_anterior_y = pessoas_rastreadas[track_id]

                    # Desceu cruzando a linha -> SAÍDA
                    if posicao_anterior_y < linha_y and cy >= linha_y:
                        saidas += 1
                        cor_linha = (0, 0, 255)  # Pisca vermelho
                        espessura_linha = 6
                        notificar_backend("SAIDA", entradas, saidas)

                    # Subiu cruzando a linha -> ENTRADA
                    elif posicao_anterior_y > linha_y and cy <= linha_y:
                        entradas += 1
                        cor_linha = (0, 255, 0)  # Pisca verde
                        espessura_linha = 6
                        notificar_backend("ENTRADA", entradas, saidas)

                pessoas_rastreadas[track_id] = cy

        # Desenha a linha virtual e o placar na janela do vídeo
        cv2.line(annotated_frame, (0, linha_y), (largura, linha_y), cor_linha, espessura_linha)

        lotacao = max(0, entradas - saidas)
        cv2.putText(annotated_frame, f"Entradas: {entradas}", (25, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        cv2.putText(annotated_frame, f"Saidas: {saidas}", (25, 95), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        cv2.putText(annotated_frame, f"Na Loja: {lotacao}", (25, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

        if config.SHOW_VIDEO:
            frame_redimensionado = cv2.resize(annotated_frame, (960, 540))
            cv2.imshow("Fila Zero - Sensor de Fluxo (Loop)", frame_redimensionado)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_sensor()