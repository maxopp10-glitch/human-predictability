import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager
import gspread
from google.oauth2.service_account import Credentials

# =========================
# CONFIGURAÇÕES
# =========================

MAX_RESPOSTAS_SEMANA = 3

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

# =========================
# GOOGLE SHEETS
# =========================

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    st.secrets["sheets"]["sheet_id"]
).sheet1


def carregar_dados():
    dados = sheet.get_all_records()
    return pd.DataFrame(dados)


def salvar_resposta(nova_resposta):
    sheet.append_row(nova_resposta)


# =========================
# COOKIES
# =========================

cookies = EncryptedCookieManager(
    prefix="human_predictability/",
    password="projeto_ml_max_2026"
)

if not cookies.ready():
    st.stop()

# =========================
# CABEÇALHO
# =========================

st.title("Human Predictability")

st.subheader("Experimentos de escolhas simples")

st.write(
    "Objetivo: estudar se escolhas humanas simples apresentam padrões previsíveis ao longo do tempo."
)

# =========================
# ID ANÔNIMO
# =========================

user_id = cookies.get("user_id")

if user_id is None:
    user_id = "USER_" + str(uuid.uuid4())[:8].upper()
    cookies["user_id"] = user_id
    cookies.save()

st.info(f"Seu ID anônimo é: {user_id}")

# =========================
# PERFIL DO PARTICIPANTE
# =========================

idade_cookie = cookies.get("idade")
sexo_cookie = cookies.get("sexo")

if idade_cookie is None or sexo_cookie is None:
    st.subheader("Dados iniciais")

    idade = st.number_input(
        "Qual sua idade?",
        min_value=10,
        max_value=100,
        step=1
    )

    sexo = st.selectbox(
        "Sexo (opcional)",
        [
            "Prefiro não informar",
            "Masculino",
            "Feminino"
        ]
    )

    if st.button("Salvar dados iniciais"):
        cookies["idade"] = str(idade)
        cookies["sexo"] = sexo
        cookies.save()

        st.success("Dados iniciais salvos com sucesso!")
        st.rerun()

    st.stop()

else:
    idade = int(idade_cookie)
    sexo = sexo_cookie

# =========================
# SEMANA ATUAL
# =========================

agora = datetime.now()
semana_ano = f"{agora.year}-{agora.isocalendar().week}"

# =========================
# CARREGAR DADOS
# =========================

df_respostas = carregar_dados()

# =========================
# FUNÇÃO DE LIMITE SEMANAL
# =========================

def contar_respostas_semanais(df, user_id, semana_ano, experimento):
    if df.empty:
        return 0

    colunas_necessarias = ["user_id", "semana_ano", "tipo_experimento"]

    if not all(col in df.columns for col in colunas_necessarias):
        return 0

    respostas_filtradas = df[
        (df["user_id"] == user_id) &
        (df["semana_ano"] == semana_ano) &
        (df["tipo_experimento"] == experimento)
    ]

    return len(respostas_filtradas)

# =========================
# CONTROLE DO EXPERIMENTO
# =========================

if "experimento_iniciado" not in st.session_state:
    st.session_state.experimento_iniciado = False

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "experimento_atual" not in st.session_state:
    st.session_state.experimento_atual = None

# =========================
# FORMULÁRIO DO EXPERIMENTO
# =========================

if not st.session_state.experimento_iniciado:
    st.subheader("Escolha o experimento")

    experimento = st.selectbox(
        "Experimento",
        [
            "numero_0_100",
            "cor",
            "cara_coroa",
            "letra",
            "direcao",
            "forma_geometrica",
            "animal"
        ]
    )

    total_respostas_semana = contar_respostas_semanais(
        df_respostas,
        user_id,
        semana_ano,
        experimento
    )

    st.write(
        f"Respostas nesta semana para este experimento: "
        f"**{total_respostas_semana}/{MAX_RESPOSTAS_SEMANA}**"
    )

    pode_responder_experimento = total_respostas_semana < MAX_RESPOSTAS_SEMANA

    if pode_responder_experimento:
        st.write("Quando estiver pronto, clique para iniciar o experimento.")

        if st.button("Iniciar experimento"):
            st.session_state.experimento_iniciado = True
            st.session_state.start_time = datetime.now()
            st.session_state.experimento_atual = experimento
            st.rerun()

    else:
        st.warning(
            "Você atingiu o limite semanal para este experimento. "
            "Escolha outro experimento ou volte na próxima semana."
        )

else:
    experimento = st.session_state.experimento_atual

    if experimento == "numero_0_100":
        st.write("Escolha rapidamente um número de 0 a 100.")

        resposta = st.number_input(
            "Qual número você escolheu?",
            min_value=0,
            max_value=100,
            step=1
        )

    elif experimento == "cor":
        st.write("Escolha rapidamente uma cor.")

        resposta = st.selectbox(
            "Qual cor você escolheu?",
            [
                "Azul",
                "Vermelho",
                "Verde",
                "Amarelo",
                "Preto",
                "Branco"
            ]
        )

    elif experimento == "cara_coroa":
        st.write("Escolha rapidamente uma opção.")

        resposta = st.selectbox(
            "Cara ou coroa?",
            [
                "Cara",
                "Coroa"
            ]
        )

    elif experimento == "letra":
        st.write("Escolha rapidamente uma letra.")

        resposta = st.selectbox(
            "Qual letra você escolheu?",
            [
                "A", "B", "C", "D", "E", "F", "G",
                "H", "I", "J", "K", "L", "M", "N",
                "O", "P", "Q", "R", "S", "T", "U",
                "V", "W", "X", "Y", "Z"
            ]
        )

    elif experimento == "direcao":
        st.write("Escolha rapidamente uma direção.")

        resposta = st.selectbox(
            "Qual direção você escolheu?",
            [
                "Norte",
                "Sul",
                "Leste",
                "Oeste"
            ]
        )

    elif experimento == "forma_geometrica":
        st.write("Escolha rapidamente uma forma geométrica.")

        resposta = st.selectbox(
            "Qual forma você escolheu?",
            [
                "Circulo",
                "Quadrado",
                "Triangulo",
                "Retangulo",
                "Estrela",
                "Losango"
            ]
        )

    elif experimento == "animal":
        st.write("Escolha rapidamente um animal.")

        resposta = st.selectbox(
            "Qual animal você escolheu?",
            [
                "Cachorro",
                "Gato",
                "Leao",
                "Lobo",
                "Aguia",
                "Golfinho"
            ]
        )

    if st.button("Enviar resposta"):
        agora = datetime.now()

        tempo_resposta = (
            agora - st.session_state.start_time
        ).total_seconds()

        nova_resposta = [
            user_id,
            idade,
            sexo,
            experimento,
            resposta,
            agora.strftime("%Y-%m-%d %H:%M:%S"),
            agora.hour,
            agora.strftime("%A"),
            semana_ano,
            round(tempo_resposta, 2)
        ]

        salvar_resposta(nova_resposta)

        st.session_state.experimento_iniciado = False
        st.session_state.start_time = None
        st.session_state.experimento_atual = None

        st.success("Resposta registrada com sucesso!")
        st.rerun()

# =========================
# RESUMO DO DATASET
# =========================

st.divider()

st.subheader("Resumo parcial do experimento")

df = carregar_dados()

if not df.empty:
    st.write(f"Total de respostas coletadas: **{len(df)}**")
    st.write(f"Total de usuários anônimos: **{df['user_id'].nunique()}**")

    if "tipo_experimento" in df.columns and "resposta" in df.columns:
        st.write("Respostas por tipo de experimento:")
        st.dataframe(
            df.groupby(["tipo_experimento", "resposta"])
            .size()
            .reset_index(name="quantidade")
        )

    with st.expander("Visualizar dados coletados"):
        st.dataframe(df)

else:
    st.write("Ainda não há respostas coletadas.")