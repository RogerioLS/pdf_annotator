# pdf_annotator
Interactive tool to annotate PDFs, extract structured table data from marked regions using PyMuPDF and OpenCV, with a Streamlit interface.

# 📄 PDF Annotator com Grade Visual (CV2 + PyMuPDF + Streamlit)

## 🎯 Objetivo

Ferramenta interativa para **anotar PDFs**, **extrair textos de regiões específicas** e **exportar os dados em formato estruturado (CSV)**.  
O sistema combina **OpenCV**, **PyMuPDF** e **Streamlit** para permitir uma experiência visual e intuitiva de marcação manual — ideal para documentos financeiros, relatórios e extratos bancários.

---

## 🧠 Visão Geral

O usuário faz upload de um PDF, o sistema converte a página em imagem e aplica uma **grade de linhas e colunas** para facilitar a identificação de regiões.  
Com o `streamlit-drawable-canvas`, o usuário pode **desenhar retângulos** sobre os campos desejados, salvar essas marcações e, em seguida, **extrair o texto** contido nelas.

---

## ⚙️ Stack Tecnológica

| Componente | Função |
|-------------|--------|
| **Streamlit** | Interface visual interativa |
| **streamlit-drawable-canvas** | Ferramenta para desenhar retângulos sobre o PDF |
| **PyMuPDF (fitz)** | Leitura de PDFs e extração de texto |
| **OpenCV (cv2)** | Detecção e exibição de linhas/colunas no PDF |
| **Pandas** | Estruturação e exportação de dados extraídos |
| **JSON + CSV** | Persistência e exportação das marcações e dados |

---

## 🗂️ Estrutura do Projeto

```
pdf_annotator/
├── app/
│   ├── main.py               # Aplicação principal (Streamlit)
│   ├── text_extractor.py     # Extração de texto via PyMuPDF
│   ├── storage.py            # Salvamento e carregamento das marcações JSON
│   └── ...
├── data/
│   ├── pdfs/                 # PDFs enviados
│   ├── imagens/              # Páginas convertidas em imagens
│   ├── marcacoes/            # Marcações salvas (JSON)
│   └── tabelas/              # Tabelas exportadas (CSV)
├── requirements.txt
└── README.md
```

---

## 🚀 Como Usar

1. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   ```

2. **Executar a aplicação**
   ```bash
   streamlit run app/main.py
   ```

3. **Fluxo no aplicativo**
   - Faça **upload** de um PDF.
   - Escolha a **página** que deseja visualizar.
   - O sistema aplicará uma **grade visual (linhas e colunas)**.
   - Desenhe **retângulos** sobre os campos de interesse.
   - Clique em **💾 Salvar Marcações**.
   - Clique em **📤 Extrair Texto e Exportar CSV** para gerar os dados estruturados.

---

## 📦 Funcionalidades Atuais

✅ Upload de PDFs  
✅ Visualização de páginas com grade visual (OpenCV)  
✅ Desenho interativo de regiões (Canvas)  
✅ Salvamento e carregamento de marcações em JSON  
✅ Extração de texto das regiões via PyMuPDF  
✅ Exportação para CSV  
✅ Compatível com múltiplas páginas do mesmo documento  

---

## 📊 Exemplo de Saída (CSV)

| label | tipo  | texto | página | x | y | w | h |
|-------|-------|-------|--------|---|---|---|---|
| campo_0 | valor | Fundo XP RF Ref DI | 1 | 125.5 | 302.1 | 240.0 | 45.2 |
| campo_1 | valor | Vencimento: 31/12/2025 | 1 | 370.2 | 355.7 | 180.0 | 40.0 |

---

## 🚧 Próximos Passos

### 🔧 Melhorias Imediatas

1. **Limpar canvas ao abrir**
   - Adicionar botão “Limpar Marcações” para evitar artefatos invisíveis.

2. **Permitir edição do label e tipo das marcações**
   - Mostrar formulário dinâmico com `text_input` e `selectbox` após desenhar.

3. **Recarregar marcações no canvas**
   - Mostrar visualmente as marcações salvas ao abrir a página.

4. **Melhorar extração de texto**
   - Permitir teste rápido de extração individual por bounding box.

---

## 🧩 Futuras Expansões

| Fase | Descrição |
|------|------------|
| **Fase 2** | Suporte a múltiplas páginas simultaneamente |
| **Fase 3** | Sistema multiusuário leve (várias pessoas anotando PDFs) |
| **Fase 4** | Migração para stack Web (FastAPI + React) |
| **Modo OCR** | Integrar PaddleOCR para PDFs escaneados |
| **Auto-sugestão** | Gerar marcações automáticas baseadas em contornos detectados |

---

## 👨‍💻 Autor

Desenvolvido por [Rogerio Silva](mailto:risco.gauss@gausscapital.com.br)  
**Gauss Capital - Área de Risco / Automação**

---
