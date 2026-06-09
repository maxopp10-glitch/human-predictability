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

@st.cache_resource
def conectar_planilha():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(
        st.secrets["sheets"]["sheet_id"]
    ).sheet1

    return sheet


@st.cache_data(ttl=60)
def carregar_dados():
    sheet = conectar_planilha()
    dados = sheet.get_all_records()
    return pd.DataFrame(dados)


def salvar_resposta(nova_resposta):
    sheet = conectar_planilha()
    sheet.append_row(nova_resposta, value_input_option="USER_ENTERED")
    carregar_dados.clear()


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

try:
    df_respostas = carregar_dados()
except Exception:
    st.error("Não foi possível carregar os dados da planilha neste momento.")
    df_respostas = pd.DataFrame()

# =========================
# CONTADOR GLOBAL
# =========================

if not df_respostas.empty and "user_id" in df_respostas.columns:
    total_respostas_global = len(df_respostas)
    total_participantes_global = df_respostas["user_id"].nunique()
else:
    total_respostas_global = 0
    total_participantes_global = 0

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="Participantes",
        value=total_participantes_global
    )

with col2:
    st.metric(
        label="Respostas",
        value=total_respostas_global
    )

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
    resposta_valida = True
    resposta = None

    if experimento == "numero_0_100":
        st.write("Escolha rapidamente um número de 0 a 100.")

        numero_digitado = st.text_input(
            "Qual número você escolheu?",
            placeholder="Digite um número entre 0 e 100"
        )

        if numero_digitado.strip() == "":
            resposta_valida = False
            st.info("Digite um número para enviar sua resposta.")

        else:
            try:
                numero_convertido = int(numero_digitado)

                if 0 <= numero_convertido <= 100:
                    resposta = numero_convertido
                else:
                    resposta_valida = False
                    st.warning("O número precisa estar entre 0 e 100.")

            except ValueError:
                resposta_valida = False
                st.warning("Digite apenas números inteiros, sem letras ou símbolos.")

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

    if st.button("Enviar resposta", disabled=not resposta_valida):
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
# DASHBOARD
# =========================

st.divider()

st.subheader("Resultados em tempo real")

colunas_dashboard = [
    "user_id",
    "idade",
    "sexo",
    "tipo_experimento",
    "resposta",
    "timestamp",
    "hora",
    "dia_semana",
    "semana_ano",
    "tempo_resposta_segundos"
]

if df_respostas.empty:
    st.write("Ainda não há respostas coletadas.")

elif not all(col in df_respostas.columns for col in colunas_dashboard):
    st.warning(
        "A planilha ainda não possui todas as colunas esperadas para exibir o dashboard."
    )

    st.write("Colunas esperadas:")
    st.write(colunas_dashboard)

    st.write("Colunas encontradas:")
    st.write(list(df_respostas.columns))

else:
    ultima_atualizacao = df_respostas["timestamp"].max()
    st.caption(f"Última resposta registrada: {ultima_atualizacao}")

    st.write("Respostas por experimento")

    respostas_por_experimento = (
        df_respostas["tipo_experimento"]
        .value_counts()
        .reset_index()
    )

    respostas_por_experimento.columns = [
        "tipo_experimento",
        "quantidade"
    ]

    st.bar_chart(
        respostas_por_experimento.set_index("tipo_experimento")
    )

    st.divider()

    st.write("Distribuição por experimento")

    experimentos_disponiveis = sorted(
        df_respostas["tipo_experimento"].dropna().unique()
    )

    experimento_dashboard = st.selectbox(
        "Selecione um experimento para visualizar",
        experimentos_disponiveis
    )

    df_experimento = df_respostas[
        df_respostas["tipo_experimento"] == experimento_dashboard
    ]

    contagem_respostas = (
        df_experimento["resposta"]
        .value_counts()
        .reset_index()
    )

    contagem_respostas.columns = [
        "resposta",
        "quantidade"
    ]

    if experimento_dashboard == "numero_0_100":
        contagem_respostas["resposta"] = pd.to_numeric(
            contagem_respostas["resposta"],
            errors="coerce"
        )

        contagem_respostas = contagem_respostas.sort_values("resposta")

    else:
        contagem_respostas = contagem_respostas.sort_values(
            "quantidade",
            ascending=False
        )

    st.bar_chart(
        contagem_respostas.set_index("resposta")
    )

    st.write("Tabela de frequência")

    total_experimento = contagem_respostas["quantidade"].sum()

    contagem_respostas["percentual"] = (
        contagem_respostas["quantidade"] / total_experimento * 100
    ).round(2)

    st.dataframe(contagem_respostas)

    st.divider()

    st.write("Tempo médio de resposta por experimento")

    df_respostas["tempo_resposta_segundos"] = (
        df_respostas["tempo_resposta_segundos"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )

    df_respostas["tempo_resposta_segundos"] = pd.to_numeric(
        df_respostas["tempo_resposta_segundos"],
        errors="coerce"
    )

    tempo_medio = (
        df_respostas
        .groupby("tipo_experimento")["tempo_resposta_segundos"]
        .mean()
        .round(2)
        .reset_index()
    )

    tempo_medio.columns = [
        "tipo_experimento",
        "tempo_medio_segundos"
    ]

    st.bar_chart(
        tempo_medio.set_index("tipo_experimento")
    )

    st.dataframe(tempo_medio)