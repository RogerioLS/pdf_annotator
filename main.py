# main.py - PDF Annotator com melhorias (limpar canvas sem erro + OCR)

import streamlit as st
from streamlit_drawable_canvas import st_canvas
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import os
import pandas as pd
from storage import save_annotations, load_annotations
from text_extractor import extract_text_from_annotations, export_dataframe_to_csv
from ocr_extractor import extrair_texto_com_ocr

st.set_page_config(layout="wide")
st.title("📄 PDF Annotator com Grade Visual (CV2 + PyMuPDF + OCR)")

if "annotations" not in st.session_state:
    st.session_state.annotations = []

if "clear_canvas" not in st.session_state:
    st.session_state.clear_canvas = False

if "ocr_boxes" not in st.session_state:
    st.session_state.ocr_boxes = []

os.makedirs("data/pdfs", exist_ok=True)
os.makedirs("data/imagens", exist_ok=True)
os.makedirs("data/tabelas", exist_ok=True)

def pdf_to_image(path, page_number=0, zoom=1.75):
    doc = fitz.open(path)
    page = doc[page_number]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img


def detectar_linhas_e_colunas(pil_image):
    image = np.array(pil_image)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    thresh = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)

    horizontal = thresh.copy()
    horizontalsize = int(horizontal.shape[1] / 30)
    horizontal_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize, 1))
    horizontal = cv2.erode(horizontal, horizontal_structure)
    horizontal = cv2.dilate(horizontal, horizontal_structure)

    vertical = thresh.copy()
    verticalsize = int(vertical.shape[0] / 30)
    vertical_structure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
    vertical = cv2.erode(vertical, vertical_structure)
    vertical = cv2.dilate(vertical, vertical_structure)

    contours_h, _ = cv2.findContours(horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_v, _ = cv2.findContours(vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output = image.copy()
    cv2.drawContours(output, contours_h, -1, (0, 0, 255), 1)
    cv2.drawContours(output, contours_v, -1, (0, 255, 0), 1)

    return Image.fromarray(output)

def desenhar_caixas_ocr(image_pil, boxes):
    img = np.array(image_pil.copy())
    for box in boxes:
        x0, y0, x1, y1 = box["box"]
        cv2.rectangle(img, (x0, y0), (x1, y1), (255, 0, 0), 1)
    return Image.fromarray(img)


uploaded_file = st.file_uploader("Envie um PDF para anotar", type=["pdf"])

if uploaded_file:
    pdf_path = os.path.join("data/pdfs", uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    doc = fitz.open(pdf_path)
    total_paginas = len(doc)
    pagina = st.number_input("Página para visualizar", 1, total_paginas, 1)

    img_raw = pdf_to_image(pdf_path, page_number=pagina - 1)
    img_grade = detectar_linhas_e_colunas(img_raw)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🧹 Limpar Marcações"):
            st.session_state.clear_canvas = True
            st.session_state.annotations = []

    with col2:
        if st.button("📂 Carregar Marcações Salvas"):
            st.session_state.annotations = load_annotations(uploaded_file.name, pagina)
            st.success("Marcações carregadas!")

    initial_drawing = {"objects": []} if st.session_state.clear_canvas else None

    st.subheader("🔍 Marque as regiões de interesse na imagem abaixo")
    canvas_result = st_canvas(
        fill_color="rgba(0, 255, 0, 0.3)",
        stroke_color="green",
        stroke_width=2,
        background_image=desenhar_caixas_ocr(img_grade, st.session_state.ocr_boxes) if st.session_state.ocr_boxes else img_grade,
        update_streamlit=True,
        height=img_grade.height,
        width=img_grade.width,
        drawing_mode="rect",
        key=f"canvas_{pagina}",
        initial_drawing=initial_drawing,
    )

    st.session_state.clear_canvas = False

    new_annotations = []
    if canvas_result.json_data and "objects" in canvas_result.json_data:
        for i, obj in enumerate(canvas_result.json_data["objects"]):
            if obj.get("type") == "rect":
                label = f"campo_{i}"
                tipo = "valor"
                new_annotations.append({
                    "left": obj["left"],
                    "top": obj["top"],
                    "width": obj["width"],
                    "height": obj["height"],
                    "label": label,
                    "tipo": tipo
                })
        st.session_state.annotations = new_annotations

    st.write(f"🔢 {len(st.session_state.annotations)} marcações detectadas nesta página.")

    if st.session_state.annotations:
        st.subheader("✏️ Editar marcações")
        tipos_possiveis = ["valor", "linha", "coluna", "outro"]
        for idx, annot in enumerate(st.session_state.annotations):
            col1, col2 = st.columns([2, 1])
            with col1:
                new_label = st.text_input(f"Label para marcação {idx+1}", value=annot["label"], key=f"label_{idx}")
                annot["label"] = new_label
            with col2:
                new_tipo = st.selectbox(f"Tipo", tipos_possiveis, index=tipos_possiveis.index(annot["tipo"]) if annot["tipo"] in tipos_possiveis else 0, key=f"tipo_{idx}")
                annot["tipo"] = new_tipo

    with st.expander("🧠 OCR da Página com PaddleOCR"):
        confianca_minima = st.slider("Confiança mínima para mostrar resultado", 0.0, 1.0, 0.6, step=0.05)

        if st.button("🔍 Executar OCR da Página Atual"):
            image_path = os.path.join("data/imagens", f"{uploaded_file.name}_page_{pagina}.png")
            img_raw.save(image_path)
            boxes = extrair_texto_com_ocr(image_path)
            boxes_filtrados = [b for b in boxes if b["confiança"] >= confianca_minima]
            st.session_state.ocr_boxes = boxes_filtrados
            st.success(f"{len(boxes_filtrados)} caixas com confiança ≥ {confianca_minima} detectadas")
            st.dataframe(pd.DataFrame(boxes_filtrados))

        if st.session_state.ocr_boxes:
            if st.button("🖍️ Marcar todos no Canvas"):
                anotacoes_ocr = []
                for i, box in enumerate(st.session_state.ocr_boxes):
                    x0, y0, x1, y1 = box["box"]
                    anotacoes_ocr.append({
                        "left": x0,
                        "top": y0,
                        "width": x1 - x0,
                        "height": y1 - y0,
                        "label": f"ocr_{i}",
                        "tipo": "valor"
                    })
                st.session_state.annotations.extend(anotacoes_ocr)
                st.success("Marcações do OCR adicionadas com sucesso!")

    if st.button("💾 Salvar Marcações"):
        save_annotations(uploaded_file.name, pagina, st.session_state.annotations)
        st.success("Marcações salvas com sucesso!")

    if st.button("📤 Extrair Texto e Exportar CSV"):
        df = extract_text_from_annotations(pdf_path, pagina, st.session_state.annotations)
        st.dataframe(df)
        csv_path = os.path.join("data/tabelas", f"{uploaded_file.name}_page_{pagina}.csv")
        export_dataframe_to_csv(df, csv_path)
        st.download_button("📥 Baixar CSV", data=df.to_csv(index=False, encoding="utf-8-sig"), file_name=os.path.basename(csv_path), mime="text/csv")