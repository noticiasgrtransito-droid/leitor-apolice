# app.py
import re
import io
import pandas as pd
import streamlit as st
import PyPDF2

st.set_page_config(page_title="Leitor de Apólices — Extração de Dados em PDF", page_icon="📄")
st.title("📄 Leitor de Apólices — Extração de Dados em PDF")
st.write("Envie um PDF e o aplicativo tentará identificar automaticamente os principais campos da apólice (Segurado, Seguradora, Corretora, Vigência, Ramo, LMG etc).")

def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        try:
            text += page.extract_text() + "\n"
        except:
            pass
    return text

# Função para buscar padrões
def find_value(label, text, after_chars=100):
    pattern = rf"{label}[:\s\-]*([^\n]{{1,{after_chars}}})"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

st.sidebar.header("📤 Upload do PDF")
uploaded_file = st.sidebar.file_uploader("Selecione o arquivo PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Lendo o PDF..."):
        text = extract_text_from_pdf(uploaded_file)

    st.success("✅ PDF lido com sucesso!")

    campos = {
        "CNPJ Segurado": r"CNPJ.*?(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})",
        "Vigência": r"Vig[eê]ncia[:\s\-]*([0-9A-Za-z\s/ até]+)",
        "Ramo": r"Ramo[:\s\-]*([A-Z\s]+)",
        "Nome Seguradora": r"Seguradora[:\s\-]*([A-Z0-9\s\.\-&]+)",
        "CNPJ Seguradora": r"Seguradora.*?(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})",
        "Nome Corretora": r"Corretora[:\s\-]*([A-Z0-9\s\.\-&]+)",
        "CNPJ Corretora": r"Corretora.*?(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})",
        "Código Susep Corretora": r"Susep[:\s\-]*([0-9]+)",
        "Código Susep Apólice": r"Susep[:\s\-]*([0-9]+)",
        "Número da Apólice": r"Ap[oó]lice[:\s\-]*([A-Z0-9\/\.\-]+)",
        "Produto de Higiene e Limpeza / Cosméticos": r"(Higiene|Limpeza|Cosm[eé]tico|Perfume|Perfumaria)",
        "Artigos de Higiene e Limpeza / Cosméticos": r"(Higiene|Limpeza|Cosm[eé]tico|Perfume|Perfumaria)",
        "Limite Máximo de Garantia": r"Limite M[aá]ximo.*?([\d\.,]+)",
        "LMG": r"\bLMG\b[:\s\-]*([\d\.,]+)"
    }

    resultados = []
    for campo, padrao in campos.items():
        valor = ""
        match = re.search(padrao, text, re.IGNORECASE)
        if match:
            valor = match.group(1).strip()
        resultados.append({"Campo": campo, "Valor Encontrado": valor})

    df = pd.DataFrame(resultados)
    st.subheader("📊 Resultados extraídos")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar resultados em CSV",
        data=csv,
        file_name="dados_apolice.csv",
        mime="text/csv"
    )
else:
    st.info("📂 Envie um arquivo PDF para começar.")
