import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager
import gspread
from google.oauth2.service_account import Credentials

MAX_RESPOSTAS_SEMANA = 3

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

EXPERIMENTOS = [
    "numero_0_100",
    "numero_1_10",
    "cor",
    "cara_coroa",
    "direcao",
    "forma_geometrica",
    "animal",
    "carta_baralho",
    "mes_ano",
    "estacao",
    "emoji",
    "clima"
]


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


cookies = EncryptedCookieManager(
    prefix="human_predictability/",
    password="projeto_ml_max_2026"
)

if not cookies.ready():
    st.stop()

st.title("Human Predictability")
st.subheader("Experimentos de escolhas simples")
st.write("Objetivo: estudar se escolhas humanas simples apresentam padrões previsíveis ao longo do tempo.")

user_id = cookies.get("user_id")

if user_id is None:
    user_id = "USER_" + str(uuid.uuid4())[:8].upper()
    cookies["user_id"] = user_id
    cookies.save()

st.info(f"Seu ID anônimo é: {user_id}")

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
        ["Prefiro não informar", "Masculino", "Feminino"]
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


agora = datetime.now()
semana_ano = f"{agora.year}-{agora.isocalendar().week}"

try:
    df_respostas = carregar_dados()
except Exception:
    st.error("Não foi possível carregar os dados da planilha neste momento.")
    df_respostas = pd.DataFrame()


if not df_respostas.empty and "user_id" in df_respostas.columns:
    total_respostas_global = len(df_respostas)
    total_participantes_global = df_respostas["user_id"].nunique()
else:
    total_respostas_global = 0
    total_participantes_global = 0

col1, col2 = st.columns(2)

with col1:
    st.metric(label="Participantes", value=total_participantes_global)

with col2:
    st.metric(label="Respostas", value=total_respostas_global)


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


if "experimento_iniciado" not in st.session_state:
    st.session_state.experimento_iniciado = False

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "experimento_atual" not in st.session_state:
    st.session_state.experimento_atual = None


if not st.session_state.experimento_iniciado:
    st.subheader("Escolha o experimento")

    experimento = st.selectbox(
        "Experimento",
        EXPERIMENTOS
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

    elif experimento == "numero_1_10":
        st.write("Escolha rapidamente um número de 1 a 10.")

        numero_digitado = st.text_input(
            "Qual número você escolheu?",
            placeholder="Digite um número entre 1 e 10"
        )

        if numero_digitado.strip() == "":
            resposta_valida = False
            st.info("Digite um número para enviar sua resposta.")
        else:
            try:
                numero_convertido = int(numero_digitado)

                if 1 <= numero_convertido <= 10:
                    resposta = numero_convertido
                else:
                    resposta_valida = False
                    st.warning("O número precisa estar entre 1 e 10.")

            except ValueError:
                resposta_valida = False
                st.warning("Digite apenas números inteiros, sem letras ou símbolos.")

    elif experimento == "cor":
        st.write("Escolha rapidamente uma cor.")
        resposta = st.selectbox(
            "Qual cor você escolheu?",
            ["Azul", "Vermelho", "Verde", "Amarelo", "Preto", "Branco"]
        )

    elif experimento == "cara_coroa":
        st.write("Escolha rapidamente uma opção.")
        resposta = st.selectbox(
            "Cara ou coroa?",
            ["Cara", "Coroa"]
        )

    elif experimento == "direcao":
        st.write("Escolha rapidamente uma direção.")
        resposta = st.selectbox(
            "Qual direção você escolheu?",
            ["Norte", "Sul", "Leste", "Oeste"]
        )

    elif experimento == "forma_geometrica":
        st.write("Escolha rapidamente uma forma geométrica.")
        resposta = st.selectbox(
            "Qual forma você escolheu?",
            ["Circulo", "Quadrado", "Triangulo", "Retangulo", "Estrela", "Losango"]
        )

    elif experimento == "animal":
        st.write("Escolha rapidamente um animal.")
        resposta = st.selectbox(
            "Qual animal você escolheu?",
            ["Cachorro", "Gato", "Leao", "Lobo", "Aguia", "Golfinho"]
        )

    elif experimento == "carta_baralho":
        st.write("Escolha rapidamente uma carta de baralho.")

        elif experimento == "carta_baralho":
        st.write("Escolha rapidamente uma carta de baralho.")

        naipe = st.selectbox(
            "Escolha o naipe:",
            [
                "Copas",
                "Espadas",
                "Ouros",
                "Paus"
            ]
        )

        carta = st.selectbox(
            "Escolha a carta:",
            [
                "A",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "J",
                "Q",
                "K"
            ]
        )

        resposta = f"{carta} de {naipe}"



    elif experimento == "mes_ano":
        st.write("Escolha rapidamente um mês do ano.")

        resposta = st.selectbox(
            "Qual mês você escolheu?",
            [
                "Janeiro",
                "Fevereiro",
                "Março",
                "Abril",
                "Maio",
                "Junho",
                "Julho",
                "Agosto",
                "Setembro",
                "Outubro",
                "Novembro",
                "Dezembro"
            ]
        )

    elif experimento == "estacao":
        st.write("Escolha rapidamente uma estação do ano.")

        resposta = st.selectbox(
            "Qual estação você escolheu?",
            [
                "Verão",
                "Outono",
                "Inverno",
                "Primavera"
            ]
        )

    elif experimento == "emoji":
        st.write("Escolha rapidamente um emoji.")

        resposta = st.selectbox(
            "Qual emoji você escolheu?",
            [
                "😀",
                "😂",
                "😎",
                "😍",
                "😢",
                "😡",
                "🔥",
                "❤️"
            ]
        )

    elif experimento == "clima":
        st.write("Escolha rapidamente um tipo de clima.")

        resposta = st.selectbox(
            "Qual clima você escolheu?",
            [
                "Sol",
                "Chuva",
                "Nublado",
                "Neve",
                "Tempestade",
                "Vento"
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

    if experimento_dashboard in ["numero_0_100", "numero_1_10"]:
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
    st.write("Resposta mais frequente")

    resposta_dominante = contagem_respostas.iloc[0]

    percentual_dominante = round(
        resposta_dominante["quantidade"]
        / contagem_respostas["quantidade"].sum()
        * 100,
        2
    )

    st.metric(
        label="Resposta dominante",
        value=str(resposta_dominante["resposta"])
    )

    st.metric(
        label="Índice de previsibilidade (%)",
        value=percentual_dominante
    )

    st.divider()
    st.subheader("Ranking de previsibilidade")

    ranking_previsibilidade = []

    for experimento in sorted(df_respostas["tipo_experimento"].dropna().unique()):

        df_exp = df_respostas[
            df_respostas["tipo_experimento"] == experimento
        ]

        contagem = (
            df_exp["resposta"]
            .value_counts()
            .reset_index()
        )

        contagem.columns = [
            "resposta",
            "quantidade"
        ]

        resposta_dominante_exp = contagem.iloc[0]["resposta"]

        percentual_exp = round(
            contagem.iloc[0]["quantidade"]
            / contagem["quantidade"].sum()
            * 100,
            2
        )

        ranking_previsibilidade.append({
            "tipo_experimento": experimento,
            "resposta_dominante": resposta_dominante_exp,
            "previsibilidade_%": percentual_exp
        })

    ranking_df = pd.DataFrame(ranking_previsibilidade)

    ranking_df = ranking_df.sort_values(
        by="previsibilidade_%",
        ascending=False
    )

    st.dataframe(
        ranking_df,
        use_container_width=True
    )

    st.bar_chart(
        ranking_df.set_index("tipo_experimento")["previsibilidade_%"]
    )

    st.divider()
    st.subheader("Tendência temporal")

    st.write("Respostas por semana")

    respostas_por_semana = (
        df_respostas
        .groupby("semana_ano")
        .size()
        .reset_index(name="quantidade")
        .sort_values("semana_ano")
    )

    st.bar_chart(
        respostas_por_semana.set_index("semana_ano")
    )

    st.dataframe(
        respostas_por_semana,
        use_container_width=True
    )

    st.write("Participantes por semana")

    participantes_por_semana = (
        df_respostas
        .groupby("semana_ano")["user_id"]
        .nunique()
        .reset_index(name="participantes_unicos")
        .sort_values("semana_ano")
    )

    st.bar_chart(
        participantes_por_semana.set_index("semana_ano")
    )

    st.dataframe(
        participantes_por_semana,
        use_container_width=True
    )

    st.write("Resposta dominante por semana")

    dominante_por_semana = []

    for semana in sorted(df_respostas["semana_ano"].dropna().unique()):

        df_semana = df_respostas[
            df_respostas["semana_ano"] == semana
        ]

        contagem_semana = (
            df_semana["resposta"]
            .value_counts()
            .reset_index()
        )

        contagem_semana.columns = [
            "resposta",
            "quantidade"
        ]

        resposta_dominante_semana = contagem_semana.iloc[0]["resposta"]

        percentual_semana = round(
            contagem_semana.iloc[0]["quantidade"]
            / contagem_semana["quantidade"].sum()
            * 100,
            2
        )

        dominante_por_semana.append({
            "semana_ano": semana,
            "resposta_dominante": resposta_dominante_semana,
            "previsibilidade_%": percentual_semana
        })

    dominante_semana_df = pd.DataFrame(dominante_por_semana)

    st.dataframe(
        dominante_semana_df,
        use_container_width=True
    )

    st.divider()
    st.write("Tempo médio de resposta por experimento")

    tempo_coluna = (
        df_respostas["tempo_resposta_segundos"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )

    tempo_coluna = pd.to_numeric(
        tempo_coluna,
        errors="coerce"
    ).astype(float)

    tempo_coluna = tempo_coluna.apply(
        lambda x: x / 100 if pd.notnull(x) and x > 30 else x
    )

    df_respostas = df_respostas.copy()
    df_respostas["tempo_resposta_segundos"] = tempo_coluna

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