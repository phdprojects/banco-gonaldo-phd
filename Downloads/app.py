import streamlit as st
import time
import random
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Banco Gonaldo PhD", layout="centered")

# =========================
# 🎨 ESTILO MAINFRAME
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&display=swap');

.stApp { background-color: black; }

.terminal {
    font-family: 'IBM Plex Mono', monospace;
    color: #00FF00;
    font-size: 14px;
    white-space: pre-wrap;
}

input {
    background: black !important;
    color: #00FF00 !important;
    border-bottom: 1px solid #00FF00 !important;
}

.fingerprint {
    width:120px;height:120px;
    border:2px solid #00FF00;
    border-radius:50%;
    margin:auto;
    animation:pulse 1.5s infinite;
}

@keyframes pulse {
    0%{box-shadow:0 0 5px #0f0;}
    50%{box-shadow:0 0 20px #0f0;}
    100%{box-shadow:0 0 5px #0f0;}
}
</style>
""", unsafe_allow_html=True)

# =========================
# ⏳ LOADING
# =========================
def loading_sim(msg="A PROCESSAR"):
    placeholder = st.empty()
    frames = ["[■□□□□]", "[■■□□□]", "[■■■□□]", "[■■■■□]", "[■■■■■]"]
    for i in range(5):
        placeholder.markdown(f"### > {msg} {frames[i]}")
        time.sleep(0.3)
    placeholder.markdown(f"### > {msg} COMPLETO ✓")
    time.sleep(0.4)
    placeholder.empty()

def loading_bank(msg="A PROCESSAR"):
    placeholder = st.empty()
    steps = [
        msg,
        "VALIDANDO CREDENCIAIS...",
        "ENCRIPTANDO DADOS...",
        "LIGANDO AO SERVIDOR CENTRAL...",
        "CONSULTANDO LEDGER...",
        "SINCRONIZANDO SISTEMA...",
        "OPERAÇÃO AUTORIZADA ✓"
    ]
    for s in steps:
        placeholder.markdown(f"<div class='terminal'> > {s}</div>", unsafe_allow_html=True)
        time.sleep(0.4)
    placeholder.empty()

# =========================
# 🔧 CORE
# =========================
def gerar_conta():
    conta = str(random.randint(10000000, 99999999))
    iban = f"PT50 0007 0000 {conta[:4]} {conta[4:]} 8045"
    pin = str(random.randint(1000, 9999))
    return conta, iban, pin

def gerar_cartao(nome):
    partes = nome.split()
    primeiro = partes[0]
    ultimo = partes[-1] if len(partes) > 1 else ""

    cartao = " ".join([str(random.randint(1000,9999)) for _ in range(4)])
    validade = f"{random.randint(1,12):02d}/{random.randint(26,30)}"
    cvv = str(random.randint(100,999))

    nome_cartao = f"{primeiro} {ultimo}".upper()
    return nome_cartao, cartao, validade, cvv

def gerar_pdf(nome, conta, iban, cartao, validade, cvv, pin):
    doc = SimpleDocTemplate("conta_bancaria.pdf")
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("BANCO GONALDO PhD", styles['Title']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"CLIENTE: {nome}", styles['Normal']))
    content.append(Paragraph(f"CONTA: {conta}", styles['Normal']))
    content.append(Paragraph(f"IBAN: {iban}", styles['Normal']))

    content.append(Spacer(1, 10))
    content.append(Paragraph("DADOS DO CARTÃO", styles['Heading2']))

    content.append(Paragraph(f"CARTÃO: {cartao}", styles['Normal']))
    content.append(Paragraph(f"VALIDADE: {validade}", styles['Normal']))
    content.append(Paragraph(f"CVV: {cvv}", styles['Normal']))
    content.append(Paragraph(f"PIN: {pin}", styles['Normal']))

    doc.build(content)

def encontrar_conta(ref):
    for c, d in st.session_state.db.items():
        if ref == c or ref == d["iban"]:
            return c, d
    return None, None

def log(conta, op, val):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    d = st.session_state.db[conta]
    d['extrato'].append(f"{now} | {op} | {val:+.2f} EUR | SALDO: {d['saldo']:.2f}")

def print_terminal(txt):
    st.markdown(f"<div class='terminal'>{txt}</div>", unsafe_allow_html=True)

# =========================
# 💾 DB
# =========================
if "db" not in st.session_state:
    st.session_state.db = {}

if "sessao" not in st.session_state:
    st.session_state.sessao = {"logado": False}

# =========================
# 🔐 LOGIN
# =========================
if not st.session_state.sessao["logado"]:

    print_terminal("""
============================================================
 BANCO GONALDO PhD - CORE BANKING SYSTEM
============================================================
 1 - LOGIN (ID + EMAIL)
 2 - LOGIN BIOMÉTRICO
------------------------------------------------------------
""")

    cmd = st.text_input("SYSTEM >")

    if cmd == "1":
        uid = st.text_input("ID:")
        email = st.text_input("EMAIL:")

        if st.button("AUTENTICAR"):
            loading_bank("VALIDANDO ACESSO")
            if uid == "0001" and email == "gonaldo@bancophd.pt":
                st.session_state.sessao["logado"] = True
                st.rerun()
            else:
                st.error("CREDENCIAIS INVÁLIDAS")

    elif cmd == "2":
        st.markdown("""
        <div style="text-align:center;color:#00FF00;">
            <div class="fingerprint"></div>
            <p>[ SCAN BIOMÉTRICO ]</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("INICIAR"):
            loading_bank("VALIDANDO BIOMETRIA")
            st.session_state.sessao["logado"] = True
            st.rerun()

# =========================
# 🏦 SISTEMA
# =========================
else:

    print_terminal("""
================ MENU PRINCIPAL ================

[1] CONSULTAR SALDO
[2] OPERAÇÕES FINANCEIRAS
[3] ABERTURA DE CONTA
[4] GESTÃO DE CLIENTES
[5] EXTRATO
[6] LOGOUT

===============================================
""")

    cmd = st.text_input("COMMAND >")

    # SALDO
    if cmd == "1":
        ref = st.text_input("CONTA / IBAN:")
        if st.button("CONSULTAR"):
            loading_sim("CONSULTANDO SALDO")
            c, d = encontrar_conta(ref)
            if d:
                st.metric("DISPONÍVEL", f"{d['saldo']:.2f} EUR")
            else:
                st.error("CONTA NÃO ENCONTRADA")

    # OPERAÇÕES
    elif cmd == "2":

        print_terminal("[1] DEPÓSITO | [2] LEVANTAMENTO | [3] TRANSFERÊNCIA")

        op = st.text_input("OP >")
        ref = st.text_input("CONTA:")
        valor = st.number_input("VALOR:", min_value=0.01)

        c, d = encontrar_conta(ref)

        if op == "1" and st.button("EXECUTAR"):
            if d:
                loading_bank("PROCESSANDO DEPÓSITO")
                d["saldo"] += valor
                log(c, "DEPÓSITO", valor)
                st.success("DEPÓSITO OK")

        elif op == "2":
            pin = st.text_input("PIN:", type="password")
            if st.button("EXECUTAR"):
                if d and pin == d["pin"] and valor <= d["saldo"]:
                    loading_bank("PROCESSANDO LEVANTAMENTO")
                    d["saldo"] -= valor
                    log(c, "LEVANTAMENTO", -valor)
                    st.success("LEVANTAMENTO OK")
                else:
                    st.error("ERRO")

        elif op == "3":
            destino = st.text_input("IBAN DESTINO:")
            if st.button("EXECUTAR"):
                dc, dd = encontrar_conta(destino)
                if d and dd and valor <= d["saldo"]:
                    loading_bank("EXECUTANDO TRANSFERÊNCIA")
                    d["saldo"] -= valor
                    dd["saldo"] += valor
                    log(c, "TRF SAÍDA", -valor)
                    log(dc, "TRF ENTRADA", valor)
                    st.success("TRANSFERÊNCIA OK")

    # CRIAR CONTA
    elif cmd == "3":

        print_terminal("[1] PARTICULAR | [2] EMPRESA")
        tipo = st.text_input("TIPO >")

        if tipo in ["1", "2"]:
            loading_sim("CARREGANDO FORMULÁRIO")

            nome = st.text_input("NOME:")
            nif = st.text_input("NIF:")
            email = st.text_input("EMAIL:")

            if st.button("CRIAR CONTA"):
                loading_bank("CRIANDO REGISTO DE CLIENTE")

                conta, iban, pin = gerar_conta()
                nome_cartao, cartao, validade, cvv = gerar_cartao(nome)

                st.session_state.db[conta] = {
                    "nome": nome,
                    "nif": nif,
                    "email": email,
                    "iban": iban,
                    "saldo": 0.0,
                    "pin": pin,
                    "cartao": cartao,
                    "validade": validade,
                    "cvv": cvv,
                    "extrato": [f"{datetime.now()} | CONTA CRIADA"]
                }

                print_terminal(f"""
CONTA CRIADA

NOME: {nome}
CONTA: {conta}
IBAN: {iban}

CARTÃO:
{nome_cartao}
{cartao}

VALIDADE: {validade}
CVV: {cvv}
PIN: {pin}
""")

                if st.button("GERAR PDF"):
                    gerar_pdf(nome, conta, iban, cartao, validade, cvv, pin)

                    with open("conta_bancaria.pdf", "rb") as f:
                        st.download_button("📄 DOWNLOAD PDF", f, file_name="conta.pdf")

    # GESTÃO
    elif cmd == "4":
        loading_bank("A GERAR LISTAGEM")
        for c, d in st.session_state.db.items():
            print_terminal(f"{d['nome']} | {c} | {d['iban']} | {d['saldo']:.2f}")

    # EXTRATO
    elif cmd == "5":
        ref = st.text_input("CONTA / IBAN:")
        if st.button("VER EXTRATO"):
            loading_sim("GERANDO EXTRATO")
            c, d = encontrar_conta(ref)
            if d:
                for l in reversed(d["extrato"]):
                    print_terminal(l)

    # LOGOUT
    elif cmd == "6":
        st.session_state.sessao = {"logado": False}
        st.rerun()