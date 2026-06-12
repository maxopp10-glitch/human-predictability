import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_cookies_manager import EncryptedCookieManager
import gspread
from google.oauth2.service_account import Credentials

MAX_RESPOSTAS_SEMANA = 3
APP_TIMEZONE = ZoneInfo("America/Sao_Paulo")
MAINTENANCE_MODE = True
def agora_brasil():
    return datetime.now(APP_TIMEZONE)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

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

TEXTOS = {
    "Português": {
        "title": "Human Predictability",
        "subtitle": "Experimentos de escolhas simples",
        "objective": "🧠 Você consegue ser imprevisível?\n\nParticipe de desafios rápidos e descubra se suas escolhas são realmente únicas ou se seguem padrões parecidos com os da maioria das pessoas.\n\n⏱ Menos de 2 minutos\n🔒 Totalmente anônimo",
        "anonymous_id": "Seu ID anônimo é:",
        "initial_data": "Dados iniciais",
        "age": "Qual sua idade?",
        "sex": "Sexo (opcional)",
        "save_initial": "Salvar dados iniciais",
        "saved": "Dados iniciais salvos com sucesso!",
        "choose_experiment": "Escolha o experimento",
        "experiment": "Experimento",
        "weekly_answers": "Respostas nesta semana para este experimento:",
        "ready": "Quando estiver pronto, clique para iniciar o experimento.",
        "start": "Iniciar experimento",
        "limit": "Você atingiu o limite semanal para este experimento. Escolha outro experimento ou volte na próxima semana.",
        "submit": "Enviar resposta",
        "registered": "✅ Resposta registrada!\n\n🎯 Você pode testar outro experimento ou voltar mais tarde para contribuir novamente.",
        "results": "Resultados em tempo real",
        "latest": "Última resposta registrada:",
        "answers_by_experiment": "Respostas por experimento",
        "distribution": "Distribuição por experimento",
        "select_exp": "Selecione um experimento para visualizar",
        "frequency": "Tabela de frequência",
        "dominant": "Resposta mais frequente",
        "dominant_answer": "Resposta dominante",
        "predictability": "Índice de previsibilidade (%)",
        "ranking": "Ranking de previsibilidade",
        "trend": "Tendência temporal",
        "answers_week": "Respostas por semana",
        "participants_week": "Participantes por semana",
        "dominant_week": "Resposta dominante por semana",
        "avg_time": "Tempo médio de resposta por experimento",
        "instructions_title": "Como participar",
        "instructions": """
        1. Escolha um experimento.
        2. Clique em "Iniciar experimento".
        3. Responda o mais rápido possível.
        4. Clique em "Enviar resposta".
        5. Você pode participar de vários experimentos diferentes.

        ⏱ Tempo total estimado: cerca de 2 minutos.
        🔒 Todas as respostas são anônimas.
        """,   

        "instructions": """
        1. Escolha um experimento.
        2. Clique em "Iniciar experimento".
        3. Responda o mais rápido possível.
        4. Clique em "Enviar resposta".
        5. Você pode participar de vários experimentos diferentes.

        ⏱ Tempo total estimado: cerca de 2 minutos.
        🔒 Todas as respostas são anônimas.
        """,

        "instructions_card": """
        <h3>📋 Como participar</h3>
        <p>
        Descubra se suas escolhas seguem padrões parecidos com os da maioria das pessoas.
        </p>

        <p>
        Este estudo investiga se escolhas humanas aparentemente aleatórias
        seguem padrões previsíveis quando analisadas em grupo.
        </p>

        <p>
        ⏱ Tempo total: cerca de 2 minutos<br>
        🔒 Todas as respostas são anônimas<br>
        🌎 Participantes de vários países podem participar
        </p>

        <hr>

        <h4>Como funciona</h4>

        <p>
        1️⃣ Escolha um experimento<br>
        2️⃣ Responda o mais rápido possível, sem pensar demais<br>
        3️⃣ Cada experimento pode ser respondido até <b>3 vezes por semana</b><br>
        4️⃣ Compare suas escolhas com as de centenas de outras pessoas
        </p>

        <hr>

        <h4>O que estamos tentando descobrir?</h4>

        <p>
        Muitas pessoas acreditam que suas escolhas são únicas.
        Mas quando várias respostas são analisadas juntas,
        padrões surpreendentes podem surgir.
        </p>
        """,

        "weekly_limit_text": "Você pode responder este experimento até 3 vezes por semana.", 
        "weekly_limit_text": "Você pode responder este experimento até 3 vezes por semana.",
        "weekly_done_text": "Respostas já realizadas:",
    },
    "English": {
        "title": "Human Predictability",
        "subtitle": "Simple choice experiments",
        "objective": "🧠 Can you be unpredictable?\n\nTake part in quick challenges and discover whether your choices are truly unique or follow patterns similar to most people.\n\n⏱ Less than 2 minutes\n🔒 Completely anonymous",
        "anonymous_id": "Your anonymous ID is:",
        "initial_data": "Initial data",
        "age": "How old are you?",
        "sex": "Sex (optional)",
        "save_initial": "Save initial data",
        "saved": "Initial data saved successfully!",
        "choose_experiment": "Choose the experiment",
        "experiment": "Experiment",
        "weekly_answers": "Answers this week for this experiment:",
        "ready": "When you are ready, click to start the experiment.",
        "start": "Start experiment",
        "limit": "You reached the weekly limit for this experiment. Choose another experiment or come back next week.",
        "submit": "Submit answer",
        "registered": "✅ Answer registered!\n\n🎯 You can try another experiment or come back later to contribute again.",
        "results": "Real-time results",
        "latest": "Latest registered answer:",
        "answers_by_experiment": "Answers by experiment",
        "distribution": "Distribution by experiment",
        "select_exp": "Select an experiment to view",
        "frequency": "Frequency table",
        "dominant": "Most frequent answer",
        "dominant_answer": "Dominant answer",
        "predictability": "Predictability index (%)",
        "ranking": "Predictability ranking",
        "trend": "Temporal trend",
        "answers_week": "Answers per week",
        "participants_week": "Participants per week",
        "dominant_week": "Dominant answer per week",
        "avg_time": "Average response time by experiment",
        "instructions_title": "How to participate",
        "instructions": """
        1. Choose an experiment.
        2. Click "Start experiment".
        3. Answer as quickly as possible.
        4. Click "Submit answer".
        5. You can participate in multiple different experiments.

        ⏱ Estimated total time: about 2 minutes.
        🔒 All answers are anonymous.
        """,
        "instructions_card": """
        <h3>📋 How to participate</h3>

        <p>
        Discover whether your choices follow patterns similar to those of most people.
        </p>

        <p>
        ⏱ Total time: about 2 minutes<br>
        🔒 All responses are anonymous<br>
        🌎 Participants from different countries are welcome
        </p>

        <hr>

        <h4>How does it work?</h4>

        <p>
        1️⃣ Choose an experiment<br>
        2️⃣ Answer as quickly as possible without overthinking<br>
        3️⃣ Each experiment can be answered up to <b>3 times per week</b><br>
        4️⃣ Compare your choices with those of hundreds of other participants
        </p>

        <hr>

        <h4>What are we trying to discover?</h4>

        <p>
        Many people believe their choices are unique.
        However, when large groups of responses are analyzed together,
        surprising patterns often emerge.
        </p>
        """,
        "weekly_limit_text": "You can answer this experiment up to 3 times per week.",
        "weekly_done_text": "Answers already submitted:",
    },
    "Español": {
        "title": "Human Predictability",
        "subtitle": "Experimentos de elecciones simples",
        "objective": "🧠 ¿Puedes ser impredecible?\n\nParticipa en desafíos rápidos y descubre si tus decisiones son realmente únicas o si siguen patrones similares a los de la mayoría de las personas.\n\n⏱ Menos de 2 minutos\n🔒 Totalmente anónimo",
        "anonymous_id": "Tu ID anónimo es:",
        "initial_data": "Datos iniciales",
        "age": "¿Cuál es tu edad?",
        "sex": "Sexo (opcional)",
        "save_initial": "Guardar datos iniciales",
        "saved": "¡Datos iniciales guardados con éxito!",
        "choose_experiment": "Elige el experimento",
        "experiment": "Experimento",
        "weekly_answers": "Respuestas esta semana para este experimento:",
        "ready": "Cuando estés listo, haz clic para iniciar el experimento.",
        "start": "Iniciar experimento",
        "limit": "Has alcanzado el límite semanal para este experimento. Elige otro experimento o vuelve la próxima semana.",
        "submit": "Enviar respuesta",
        "registered": "✅ ¡Respuesta registrada!\n\n🎯 Puedes probar otro experimento o volver más tarde para contribuir nuevamente.",
        "results": "Resultados en tiempo real",
        "latest": "Última respuesta registrada:",
        "answers_by_experiment": "Respuestas por experimento",
        "distribution": "Distribución por experimento",
        "select_exp": "Selecciona un experimento para visualizar",
        "frequency": "Tabla de frecuencia",
        "dominant": "Respuesta más frecuente",
        "dominant_answer": "Respuesta dominante",
        "predictability": "Índice de previsibilidad (%)",
        "ranking": "Ranking de previsibilidad",
        "trend": "Tendencia temporal",
        "answers_week": "Respuestas por semana",
        "participants_week": "Participantes por semana",
        "dominant_week": "Respuesta dominante por semana",
        "avg_time": "Tiempo medio de respuesta por experimento",
        "instructions_title": "Cómo participar",
        "instructions": """
        1. Elige un experimento.
        2. Haz clic en "Iniciar experimento".
        3. Responde lo más rápido posible.
        4. Haz clic en "Enviar respuesta".
        5. Puedes participar en varios experimentos diferentes.

        ⏱ Tiempo estimado: aproximadamente 2 minutos.
        🔒 Todas las respuestas son anónimas.
        """,

        "instructions_card": """
        <h3>📋 Cómo participar</h3>

        <p>
        Descubre si tus decisiones siguen patrones similares a los de la mayoría de las personas.
        </p>

        <p>
        ⏱ Tiempo total: aproximadamente 2 minutos<br>
        🔒 Todas las respuestas son anónimas<br>
        🌎 Participantes de diferentes países pueden participar
        </p>

        <hr>

        <h4>¿Cómo funciona?</h4>

        <p>
        1️⃣ Elige un experimento<br>
        2️⃣ Responde lo más rápido posible, sin pensarlo demasiado<br>
        3️⃣ Cada experimento puede responderse hasta <b>3 veces por semana</b><br>
        4️⃣ Compara tus decisiones con las de cientos de otros participantes
        </p>

        <hr>

        <h4>¿Qué intentamos descubrir?</h4>

        <p>
        Muchas personas creen que sus decisiones son únicas.
        Sin embargo, cuando se analizan grandes cantidades de respuestas en conjunto,
        pueden aparecer patrones sorprendentes.
        </p>
        """,

        "weekly_limit_text": "Puedes responder este experimento hasta 3 veces por semana.",
        "weekly_done_text": "Respuestas ya realizadas:",
    },
    "Français": {
        "title": "Human Predictability",
        "subtitle": "Expériences de choix simples",
        "objective": "🧠 Pouvez-vous être imprévisible ?\n\nParticipez à de rapides défis et découvrez si vos choix sont vraiment uniques ou s'ils suivent des modèles similaires à ceux de la majorité.\n\n⏱ Moins de 2 minutes\n🔒 Totalement anonyme",
        "anonymous_id": "Votre ID anonyme est :",
        "initial_data": "Données initiales",
        "age": "Quel âge avez-vous ?",
        "sex": "Sexe (optionnel)",
        "save_initial": "Enregistrer les données initiales",
        "saved": "Données initiales enregistrées avec succès !",
        "choose_experiment": "Choisissez l'expérience",
        "experiment": "Expérience",
        "weekly_answers": "Réponses cette semaine pour cette expérience :",
        "ready": "Lorsque vous êtes prêt, cliquez pour commencer l'expérience.",
        "start": "Commencer l'expérience",
        "limit": "Vous avez atteint la limite hebdomadaire pour cette expérience. Choisissez une autre expérience ou revenez la semaine prochaine.",
        "submit": "Envoyer la réponse",
        "registered": "✅ Réponse enregistrée !\n\n🎯 Vous pouvez essayer une autre expérience ou revenir plus tard pour contribuer à nouveau.",
        "results": "Résultats en temps réel",
        "latest": "Dernière réponse enregistrée :",
        "answers_by_experiment": "Réponses par expérience",
        "distribution": "Distribution par expérience",
        "select_exp": "Sélectionnez une expérience à visualiser",
        "frequency": "Tableau de fréquence",
        "dominant": "Réponse la plus fréquente",
        "dominant_answer": "Réponse dominante",
        "predictability": "Indice de prévisibilité (%)",
        "ranking": "Classement de prévisibilité",
        "trend": "Tendance temporelle",
        "answers_week": "Réponses par semaine",
        "participants_week": "Participants par semaine",
        "dominant_week": "Réponse dominante par semaine",
        "avg_time": "Temps moyen de réponse par expérience",
        "instructions_title": "Comment participer",
        "instructions": """
        1. Choisissez une expérience.
        2. Cliquez sur "Commencer l'expérience".
        3. Répondez aussi vite que possible.
        4. Cliquez sur "Envoyer la réponse".
        5. Vous pouvez participer à plusieurs expériences différentes.

        ⏱ Temps estimé : environ 2 minutes.
        🔒 Toutes les réponses sont anonymes.
        """,
        "instructions_card": """
        <h3>📋 Comment participer</h3>

        <p>
        Découvrez si vos choix suivent des tendances similaires à celles de la majorité des participants.
        </p>

        <p>
        ⏱ Temps total : environ 2 minutes<br>
        🔒 Toutes les réponses sont anonymes<br>
        🌎 Des participants de différents pays peuvent participer
        </p>

        <hr>

        <h4>Comment ça fonctionne ?</h4>

        <p>
        1️⃣ Choisissez une expérience<br>
        2️⃣ Répondez le plus rapidement possible sans trop réfléchir<br>
        3️⃣ Chaque expérience peut être réalisée jusqu'à <b>3 fois par semaine</b><br>
        4️⃣ Comparez vos choix à ceux de centaines d'autres participants
        </p>

        <hr>

        <h4>Que cherchons-nous à découvrir ?</h4>

        <p>
        Beaucoup de personnes pensent que leurs choix sont uniques.
        Cependant, lorsque de nombreuses réponses sont analysées ensemble,
        des tendances surprenantes peuvent apparaître.
        </p>
        """,
        "weekly_limit_text": "Vous pouvez répondre à cette expérience jusqu'à 3 fois par semaine.",
        "weekly_done_text": "Réponses déjà envoyées :",
    }
}

EXPERIMENT_LABELS = {
    "Português": {
        "numero_0_100": "Número de 0 a 100",
        "numero_1_10": "Número de 1 a 10",
        "cor": "Cor",
        "cara_coroa": "Cara ou coroa",
        "direcao": "Direção",
        "forma_geometrica": "Forma geométrica",
        "animal": "Animal",
        "carta_baralho": "Carta de baralho",
        "mes_ano": "Mês do ano",
        "estacao": "Estação do ano",
        "emoji": "Emoji",
        "clima": "Clima"
    },
    "English": {
        "numero_0_100": "Number from 0 to 100",
        "numero_1_10": "Number from 1 to 10",
        "cor": "Color",
        "cara_coroa": "Coin toss",
        "direcao": "Direction",
        "forma_geometrica": "Geometric shape",
        "animal": "Animal",
        "carta_baralho": "Playing card",
        "mes_ano": "Month of the year",
        "estacao": "Season",
        "emoji": "Emoji",
        "clima": "Weather"
    },
    "Español": {
        "numero_0_100": "Número de 0 a 100",
        "numero_1_10": "Número de 1 a 10",
        "cor": "Color",
        "cara_coroa": "Cara o cruz",
        "direcao": "Dirección",
        "forma_geometrica": "Forma geométrica",
        "animal": "Animal",
        "carta_baralho": "Carta de baraja",
        "mes_ano": "Mes del año",
        "estacao": "Estación del año",
        "emoji": "Emoji",
        "clima": "Clima"
    },
    "Français": {
        "numero_0_100": "Nombre de 0 à 100",
        "numero_1_10": "Nombre de 1 à 10",
        "cor": "Couleur",
        "cara_coroa": "Pile ou face",
        "direcao": "Direction",
        "forma_geometrica": "Forme géométrique",
        "animal": "Animal",
        "carta_baralho": "Carte à jouer",
        "mes_ano": "Mois de l'année",
        "estacao": "Saison",
        "emoji": "Emoji",
        "clima": "Météo"
    }
}


INSTRUCOES_EXPERIMENTOS = {
    "Português": {
        "numero_0_100": "Escolha um único número inteiro entre 0 e 100. Não existe resposta certa ou errada. Responda intuitivamente, sem pensar demais.",
        "numero_1_10": "Escolha um único número inteiro entre 1 e 10. Responda de forma espontânea.",
        "cor": "Escolha a cor que vier primeiro à sua mente. Não tente ser estratégico.",
        "cara_coroa": "Imagine que precisa escolher entre cara ou coroa. Selecione a opção que parecer mais natural.",
        "direcao": "Escolha uma direção cardinal. Responda sem procurar justificativas.",
        "forma_geometrica": "Escolha a forma geométrica que mais naturalmente chama sua atenção.",
        "animal": "Escolha o animal que vier primeiro à sua mente.",
        "carta_baralho": "Escolha livremente uma carta de baralho. Primeiro selecione o naipe e depois a carta.",
        "mes_ano": "Escolha o mês que surgir primeiro na sua mente.",
        "estacao": "Escolha a estação do ano que mais naturalmente lhe ocorre.",
        "emoji": "Escolha o emoji que mais combina com sua reação espontânea.",
        "clima": "Escolha a condição climática que vier primeiro à sua mente."
    },
    "English": {
        "numero_0_100": "Choose one whole number between 0 and 100. There is no right or wrong answer. Answer intuitively, without overthinking.",
        "numero_1_10": "Choose one whole number between 1 and 10. Answer spontaneously.",
        "cor": "Choose the color that comes to your mind first. Do not try to be strategic.",
        "cara_coroa": "Imagine you need to choose heads or tails. Select the option that feels most natural.",
        "direcao": "Choose a cardinal direction. Answer without trying to justify it.",
        "forma_geometrica": "Choose the geometric shape that naturally catches your attention.",
        "animal": "Choose the animal that comes to your mind first.",
        "carta_baralho": "Freely choose a playing card. First select the suit, then the card.",
        "mes_ano": "Choose the month that comes to your mind first.",
        "estacao": "Choose the season that naturally comes to mind.",
        "emoji": "Choose the emoji that best matches your spontaneous reaction.",
        "clima": "Choose the weather condition that comes to your mind first."
    },
    "Español": {
        "numero_0_100": "Elige un único número entero entre 0 y 100. No hay respuesta correcta o incorrecta. Responde intuitivamente, sin pensarlo demasiado.",
        "numero_1_10": "Elige un único número entero entre 1 y 10. Responde de forma espontánea.",
        "cor": "Elige el color que venga primero a tu mente. No intentes ser estratégico.",
        "cara_coroa": "Imagina que tienes que elegir entre cara o cruz. Selecciona la opción que parezca más natural.",
        "direcao": "Elige una dirección cardinal. Responde sin buscar una justificación.",
        "forma_geometrica": "Elige la forma geométrica que más naturalmente llame tu atención.",
        "animal": "Elige el animal que venga primero a tu mente.",
        "carta_baralho": "Elige libremente una carta de baraja. Primero selecciona el palo y luego la carta.",
        "mes_ano": "Elige el mes que venga primero a tu mente.",
        "estacao": "Elige la estación del año que venga más naturalmente a tu mente.",
        "emoji": "Elige el emoji que mejor represente tu reacción espontánea.",
        "clima": "Elige la condición climática que venga primero a tu mente."
    },
    "Français": {
        "numero_0_100": "Choisissez un seul nombre entier entre 0 et 100. Il n'y a pas de bonne ou de mauvaise réponse. Répondez intuitivement, sans trop réfléchir.",
        "numero_1_10": "Choisissez un seul nombre entier entre 1 et 10. Répondez spontanément.",
        "cor": "Choisissez la couleur qui vous vient d'abord à l'esprit. N'essayez pas d'être stratégique.",
        "cara_coroa": "Imaginez que vous devez choisir entre pile ou face. Sélectionnez l'option qui vous semble la plus naturelle.",
        "direcao": "Choisissez une direction cardinale. Répondez sans chercher à vous justifier.",
        "forma_geometrica": "Choisissez la forme géométrique qui attire naturellement votre attention.",
        "animal": "Choisissez l'animal qui vous vient d'abord à l'esprit.",
        "carta_baralho": "Choisissez librement une carte à jouer. Sélectionnez d'abord la couleur, puis la carte.",
        "mes_ano": "Choisissez le mois qui vous vient d'abord à l'esprit.",
        "estacao": "Choisissez la saison qui vous vient naturellement à l'esprit.",
        "emoji": "Choisissez l'emoji qui correspond le mieux à votre réaction spontanée.",
        "clima": "Choisissez la condition météo qui vous vient d'abord à l'esprit."
    }
}

IDIOMA_CODIGO = {
    "Português": "PT",
    "English": "EN",
    "Español": "ES",
    "Français": "FR"
}

SEXO_OPCOES = {
    "Português": {
        "Prefiro não informar": "Prefiro não informar",
        "Masculino": "Masculino",
        "Feminino": "Feminino"
    },
    "English": {
        "Prefer not to say": "Prefiro não informar",
        "Male": "Masculino",
        "Female": "Feminino"
    },
    "Español": {
        "Prefiero no informar": "Prefiro não informar",
        "Masculino": "Masculino",
        "Femenino": "Feminino"
    },
    "Français": {
        "Je préfère ne pas répondre": "Prefiro não informar",
        "Masculin": "Masculino",
        "Féminin": "Feminino"
    }
}


def selectbox_traduzido(label, opcoes):
    labels = list(opcoes.keys())
    escolha_label = st.selectbox(label, labels)
    return opcoes[escolha_label]


@st.cache_resource
def conectar_planilha():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client.open_by_key(st.secrets["sheets"]["sheet_id"]).sheet1


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

idioma = st.selectbox(
    "🌎 Language / Idioma / Langue",
    ["Português", "English", "Español", "Français"]
)

t = TEXTOS[idioma]

st.title(t["title"])

if MAINTENANCE_MODE:
    st.warning(
        "🚧 O aplicativo está temporariamente em manutenção para melhorias.\n\n"
        "Voltaremos em breve."
    )
    st.stop()

st.markdown(
    f"""
    <div class="instruction-card">
        {t["instructions_card"]}
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(99, 102, 241, 0.20), transparent 32%),
            radial-gradient(circle at top right, rgba(14, 165, 233, 0.18), transparent 30%),
            radial-gradient(circle at bottom left, rgba(168, 85, 247, 0.14), transparent 34%),
            linear-gradient(135deg, #f8fbff 0%, #eef4ff 45%, #fdfcff 100%);
    }

    section.main > div {
        max-width: 920px;
        padding-top: 2rem;
    }

    h1 {
        font-size: 3.2rem !important;
        font-weight: 850 !important;
        letter-spacing: -1.2px;
        color: #0f172a;
    }

    h2, h3 {
        font-weight: 750 !important;
        color: #1e293b;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid rgba(99, 102, 241, 0.16);
        padding: 18px;
        border-radius: 20px;
        box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
        backdrop-filter: blur(8px);
    }

    div[data-testid="stAlert"] {
        border-radius: 16px;
    }

    .instruction-card {
        background: rgba(255, 255, 255, 0.90);
        border: 1px solid rgba(99, 102, 241, 0.18);
        border-radius: 24px;
        padding: 24px 26px;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.09);
        margin: 20px 0 26px 0;
        backdrop-filter: blur(10px);
    }

    .instruction-card h3 {
        margin-top: 0;
        margin-bottom: 12px;
        color: #0f172a;
    }

    .instruction-card p {
        margin-bottom: 8px;
        line-height: 1.6;
        color: #334155;
    }

    .small-note {
        color: #475569;
        font-size: 0.95rem;
    }

    .stButton > button {
        border-radius: 999px;
        padding: 0.6rem 1.2rem;
        font-weight: 700;
        border: 1px solid rgba(99, 102, 241, 0.35);
        box-shadow: 0 8px 22px rgba(99, 102, 241, 0.16);
    }
    </style>
    """,
    unsafe_allow_html=True
)

user_id = cookies.get("user_id")

if user_id is None:
    user_id = "USER_" + str(uuid.uuid4())[:8].upper()
    cookies["user_id"] = user_id
    cookies.save()

idade_cookie = cookies.get("idade")
sexo_cookie = cookies.get("sexo")

if idade_cookie is None or sexo_cookie is None:
    st.subheader(t["initial_data"])

    idade = st.number_input(
        t["age"],
        min_value=10,
        max_value=100,
        step=1
    )

    sexo = selectbox_traduzido(
        t["sex"],
        SEXO_OPCOES[idioma]
    )

    if st.button(t["save_initial"]):
        cookies["idade"] = str(idade)
        cookies["sexo"] = sexo
        cookies.save()
        st.success(t["saved"])
        st.rerun()

    st.stop()

else:
    idade = int(idade_cookie)
    sexo = sexo_cookie

agora = agora_brasil()
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

st.info(f"{t['anonymous_id']} {user_id}")

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
    st.subheader(t["choose_experiment"])

    label_para_codigo = {
        EXPERIMENT_LABELS[idioma][codigo]: codigo
        for codigo in EXPERIMENTOS
    }

    experimento_label = st.selectbox(
        t["experiment"],
        list(label_para_codigo.keys())
    )

    experimento = label_para_codigo[experimento_label]
    st.info(
    f"📝 **O que fazer neste experimento**\n\n"
    f"{INSTRUCOES_EXPERIMENTOS[idioma][experimento]}"
)

    total_respostas_semana = contar_respostas_semanais(
        df_respostas,
        user_id,
        semana_ano,
        experimento
    )

    restantes = MAX_RESPOSTAS_SEMANA - total_respostas_semana

    st.info(
        f"✅ Você ainda possui **{restantes} participações disponíveis** "
        f"para este experimento nesta semana."
)

    pode_responder_experimento = total_respostas_semana < MAX_RESPOSTAS_SEMANA

    if pode_responder_experimento:
        st.write(t["ready"])

        if st.button(t["start"]):
            st.session_state.experimento_iniciado = True
            st.session_state.start_time = agora_brasil()
            st.session_state.experimento_atual = experimento
            st.rerun()
    else:
        st.warning(t["limit"])

else:
    experimento = st.session_state.experimento_atual
    resposta_valida = True
    resposta = None

    if experimento == "numero_0_100":
        st.write(EXPERIMENT_LABELS[idioma]["numero_0_100"])
        numero_digitado = st.text_input("", placeholder="0 - 100")

        if numero_digitado.strip() == "":
            resposta_valida = False
        else:
            try:
                numero_convertido = int(numero_digitado)
                if 0 <= numero_convertido <= 100:
                    resposta = numero_convertido
                else:
                    resposta_valida = False
                    st.warning("0 - 100")
            except ValueError:
                resposta_valida = False
                st.warning("Use only whole numbers.")

    elif experimento == "numero_1_10":
        st.write(EXPERIMENT_LABELS[idioma]["numero_1_10"])
        numero_digitado = st.text_input("", placeholder="1 - 10")

        if numero_digitado.strip() == "":
            resposta_valida = False
        else:
            try:
                numero_convertido = int(numero_digitado)
                if 1 <= numero_convertido <= 10:
                    resposta = numero_convertido
                else:
                    resposta_valida = False
                    st.warning("1 - 10")
            except ValueError:
                resposta_valida = False
                st.warning("Use only whole numbers.")

    elif experimento == "cor":
        resposta = selectbox_traduzido(
            EXPERIMENT_LABELS[idioma]["cor"],
            {
                "Azul" if idioma in ["Português", "Español"] else "Blue" if idioma == "English" else "Bleu": "Azul",
                "Vermelho" if idioma == "Português" else "Red" if idioma == "English" else "Rojo" if idioma == "Español" else "Rouge": "Vermelho",
                "Verde" if idioma in ["Português", "Español"] else "Green" if idioma == "English" else "Vert": "Verde",
                "Amarelo" if idioma == "Português" else "Yellow" if idioma == "English" else "Amarillo" if idioma == "Español" else "Jaune": "Amarelo",
                "Preto" if idioma == "Português" else "Black" if idioma == "English" else "Negro" if idioma == "Español" else "Noir": "Preto",
                "Branco" if idioma == "Português" else "White" if idioma == "English" else "Blanco" if idioma == "Español" else "Blanc": "Branco"
            }
        )

    elif experimento == "cara_coroa":
        resposta = selectbox_traduzido(
            EXPERIMENT_LABELS[idioma]["cara_coroa"],
            {
                "Cara" if idioma in ["Português", "Español"] else "Heads" if idioma == "English" else "Pile": "Cara",
                "Coroa" if idioma == "Português" else "Tails" if idioma == "English" else "Cruz" if idioma == "Español" else "Face": "Coroa"
            }
        )

    elif experimento == "direcao":
        resposta = selectbox_traduzido(
            EXPERIMENT_LABELS[idioma]["direcao"],
            {
                "Norte" if idioma in ["Português", "Español"] else "North" if idioma == "English" else "Nord": "Norte",
                "Sul" if idioma == "Português" else "South" if idioma == "English" else "Sur" if idioma == "Español" else "Sud": "Sul",
                "Leste" if idioma == "Português" else "East" if idioma == "English" else "Este" if idioma == "Español" else "Est": "Leste",
                "Oeste" if idioma in ["Português", "Español"] else "West" if idioma == "English" else "Ouest": "Oeste"
            }
        )

    elif experimento == "forma_geometrica":
        resposta = selectbox_traduzido(
            EXPERIMENT_LABELS[idioma]["forma_geometrica"],
            {
                "Circulo" if idioma == "Português" else "Circle" if idioma == "English" else "Círculo" if idioma == "Español" else "Cercle": "Circulo",
                "Quadrado" if idioma == "Português" else "Square" if idioma == "English" else "Cuadrado" if idioma == "Español" else "Carré": "Quadrado",
                "Triangulo" if idioma == "Português" else "Triangle" if idioma == "English" else "Triángulo" if idioma == "Español" else "Triangle": "Triangulo",
                "Retangulo" if idioma == "Português" else "Rectangle" if idioma == "English" else "Rectángulo" if idioma == "Español" else "Rectangle": "Retangulo",
                "Estrela" if idioma == "Português" else "Star" if idioma == "English" else "Estrella" if idioma == "Español" else "Étoile": "Estrela",
                "Losango" if idioma == "Português" else "Diamond" if idioma == "English" else "Rombo" if idioma == "Español" else "Losange": "Losango"
            }
        )

    elif experimento == "animal":
        resposta = selectbox_traduzido(
            EXPERIMENT_LABELS[idioma]["animal"],
            {
                "Cachorro" if idioma == "Português" else "Dog" if idioma == "English" else "Perro" if idioma == "Español" else "Chien": "Cachorro",
                "Gato" if idioma in ["Português", "Español"] else "Cat" if idioma == "English" else "Chat": "Gato",
                "Leao" if idioma == "Português" else "Lion" if idioma == "English" else "León" if idioma == "Español" else "Lion": "Leao",
                "Lobo" if idioma in ["Português", "Español"] else "Wolf" if idioma == "English" else "Loup": "Lobo",
                "Aguia" if idioma == "Português" else "Eagle" if idioma == "English" else "Águila" if idioma == "Español" else "Aigle": "Aguia",
                "Golfinho" if idioma == "Português" else "Dolphin" if idioma == "English" else "Delfín" if idioma == "Español" else "Dauphin": "Golfinho"
            }
        )

    elif experimento == "carta_baralho":
        naipe = selectbox_traduzido(
            "Suit / Naipe",
            {
                "Copas" if idioma in ["Português", "Español"] else "Hearts" if idioma == "English" else "Cœurs": "Copas",
                "Espadas" if idioma in ["Português", "Español"] else "Spades" if idioma == "English" else "Piques": "Espadas",
                "Ouros" if idioma == "Português" else "Diamonds" if idioma == "English" else "Oros" if idioma == "Español" else "Carreaux": "Ouros",
                "Paus" if idioma == "Português" else "Clubs" if idioma == "English" else "Bastos" if idioma == "Español" else "Trèfles": "Paus"
            }
        )

        carta = st.selectbox(
            "Card / Carta",
            ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        )

        resposta = f"{carta} de {naipe}"

    elif experimento == "mes_ano":
        resposta = selectbox_traduzido(
            EXPERIMENT_LABELS[idioma]["mes_ano"],
            {
                "Janeiro" if idioma == "Português" else "January" if idioma == "English" else "Enero" if idioma == "Español" else "Janvier": "Janeiro",
                "Fevereiro" if idioma == "Português" else "February" if idioma == "English" else "Febrero" if idioma == "Español" else "Février": "Fevereiro",
                "Março" if idioma == "Português" else "March" if idioma == "English" else "Marzo" if idioma == "Español" else "Mars": "Março",
                "Abril" if idioma == "Português" else "April" if idioma == "English" else "Abril" if idioma == "Español" else "Avril": "Abril",
                "Maio" if idioma == "Português" else "May" if idioma == "English" else "Mayo" if idioma == "Español" else "Mai": "Maio",
                "Junho" if idioma == "Português" else "June" if idioma == "English" else "Junio" if idioma == "Español" else "Juin": "Junho",
                "Julho" if idioma == "Português" else "July" if idioma == "English" else "Julio" if idioma == "Español" else "Juillet": "Julho",
                "Agosto" if idioma == "Português" else "August" if idioma == "English" else "Agosto" if idioma == "Español" else "Août": "Agosto",
                "Setembro" if idioma == "Português" else "September" if idioma == "English" else "Septiembre" if idioma == "Español" else "Septembre": "Setembro",
                "Outubro" if idioma == "Português" else "October" if idioma == "English" else "Octubre" if idioma == "Español" else "Octobre": "Outubro",
                "Novembro" if idioma == "Português" else "November" if idioma == "English" else "Noviembre" if idioma == "Español" else "Novembre": "Novembro",
                "Dezembro" if idioma == "Português" else "December" if idioma == "English" else "Diciembre" if idioma == "Español" else "Décembre": "Dezembro"
            }
        )

    elif experimento == "estacao":
        resposta = selectbox_traduzido(
            EXPERIMENT_LABELS[idioma]["estacao"],
            {
                "Verão" if idioma == "Português" else "Summer" if idioma == "English" else "Verano" if idioma == "Español" else "Été": "Verão",
                "Outono" if idioma == "Português" else "Autumn" if idioma == "English" else "Otoño" if idioma == "Español" else "Automne": "Outono",
                "Inverno" if idioma == "Português" else "Winter" if idioma == "English" else "Invierno" if idioma == "Español" else "Hiver": "Inverno",
                "Primavera" if idioma in ["Português", "Español"] else "Spring" if idioma == "English" else "Printemps": "Primavera"
            }
        )

    elif experimento == "emoji":
        resposta = st.selectbox(
            EXPERIMENT_LABELS[idioma]["emoji"],
            ["😀", "😂", "😎", "😍", "😢", "😡", "🔥", "❤️"]
        )

    elif experimento == "clima":
        resposta = selectbox_traduzido(
            EXPERIMENT_LABELS[idioma]["clima"],
            {
                "Sol" if idioma == "Português" else "Sun" if idioma == "English" else "Sol" if idioma == "Español" else "Soleil": "Sol",
                "Chuva" if idioma == "Português" else "Rain" if idioma == "English" else "Lluvia" if idioma == "Español" else "Pluie": "Chuva",
                "Nublado" if idioma == "Português" else "Cloudy" if idioma == "English" else "Nublado" if idioma == "Español" else "Nuageux": "Nublado",
                "Neve" if idioma == "Português" else "Snow" if idioma == "English" else "Nieve" if idioma == "Español" else "Neige": "Neve",
                "Tempestade" if idioma == "Português" else "Storm" if idioma == "English" else "Tormenta" if idioma == "Español" else "Tempête": "Tempestade",
                "Vento" if idioma == "Português" else "Wind" if idioma == "English" else "Viento" if idioma == "Español" else "Vent": "Vento"
            }
        )

    if st.button(t["submit"], disabled=not resposta_valida):
        agora = agora_brasil()

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
            round(tempo_resposta, 2),
            IDIOMA_CODIGO[idioma]
        ]

        salvar_resposta(nova_resposta)

        st.session_state.experimento_iniciado = False
        st.session_state.start_time = None
        st.session_state.experimento_atual = None

        st.success(t["registered"])
        st.rerun()

st.divider()
st.subheader(t["results"])

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
    st.warning("A planilha ainda não possui todas as colunas esperadas para exibir o dashboard.")
    st.write("Colunas esperadas:")
    st.write(colunas_dashboard)
    st.write("Colunas encontradas:")
    st.write(list(df_respostas.columns))

else:
    ultima_atualizacao = df_respostas["timestamp"].max()
    st.caption(f"{t['latest']} {ultima_atualizacao}")

    st.write(t["answers_by_experiment"])

    respostas_por_experimento = (
        df_respostas["tipo_experimento"]
        .value_counts()
        .reset_index()
    )

    respostas_por_experimento.columns = [
        "tipo_experimento",
        "quantidade"
    ]

    st.bar_chart(respostas_por_experimento.set_index("tipo_experimento"))

    st.divider()
    st.write(t["distribution"])

    experimentos_disponiveis = sorted(df_respostas["tipo_experimento"].dropna().unique())

    experimento_dashboard = st.selectbox(
        t["select_exp"],
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
        contagem_respostas = contagem_respostas.sort_values("quantidade", ascending=False)

    st.bar_chart(contagem_respostas.set_index("resposta"))

    st.write(t["frequency"])

    total_experimento = contagem_respostas["quantidade"].sum()

    contagem_respostas["percentual"] = (
        contagem_respostas["quantidade"] / total_experimento * 100
    ).round(2)

    st.dataframe(contagem_respostas)

    st.divider()
    st.write(t["dominant"])

    resposta_dominante = contagem_respostas.iloc[0]

    percentual_dominante = round(
        resposta_dominante["quantidade"] / contagem_respostas["quantidade"].sum() * 100,
        2
    )

    st.metric(label=t["dominant_answer"], value=str(resposta_dominante["resposta"]))
    st.metric(label=t["predictability"], value=percentual_dominante)

    st.divider()
    st.subheader(t["ranking"])

    ranking_previsibilidade = []

    for experimento in sorted(df_respostas["tipo_experimento"].dropna().unique()):
        df_exp = df_respostas[df_respostas["tipo_experimento"] == experimento]

        contagem = (
            df_exp["resposta"]
            .value_counts()
            .reset_index()
        )

        contagem.columns = ["resposta", "quantidade"]

        resposta_dominante_exp = contagem.iloc[0]["resposta"]

        percentual_exp = round(
            contagem.iloc[0]["quantidade"] / contagem["quantidade"].sum() * 100,
            2
        )

        ranking_previsibilidade.append({
            "tipo_experimento": experimento,
            "resposta_dominante": resposta_dominante_exp,
            "previsibilidade_%": percentual_exp
        })

    ranking_df = pd.DataFrame(ranking_previsibilidade)
    ranking_df = ranking_df.sort_values(by="previsibilidade_%", ascending=False)

    st.dataframe(ranking_df, use_container_width=True)
    st.bar_chart(ranking_df.set_index("tipo_experimento")["previsibilidade_%"])

    st.divider()
    st.subheader(t["trend"])

    st.write(t["answers_week"])

    respostas_por_semana = (
        df_respostas
        .groupby("semana_ano")
        .size()
        .reset_index(name="quantidade")
        .sort_values("semana_ano")
    )

    st.bar_chart(respostas_por_semana.set_index("semana_ano"))
    st.dataframe(respostas_por_semana, use_container_width=True)

    st.write(t["participants_week"])

    participantes_por_semana = (
        df_respostas
        .groupby("semana_ano")["user_id"]
        .nunique()
        .reset_index(name="participantes_unicos")
        .sort_values("semana_ano")
    )

    st.bar_chart(participantes_por_semana.set_index("semana_ano"))
    st.dataframe(participantes_por_semana, use_container_width=True)

    st.write(t["dominant_week"])

    dominante_por_semana = []

    for semana in sorted(df_respostas["semana_ano"].dropna().unique()):
        df_semana = df_respostas[df_respostas["semana_ano"] == semana]

        contagem_semana = (
            df_semana["resposta"]
            .value_counts()
            .reset_index()
        )

        contagem_semana.columns = ["resposta", "quantidade"]

        resposta_dominante_semana = contagem_semana.iloc[0]["resposta"]

        percentual_semana = round(
            contagem_semana.iloc[0]["quantidade"] / contagem_semana["quantidade"].sum() * 100,
            2
        )

        dominante_por_semana.append({
            "semana_ano": semana,
            "resposta_dominante": resposta_dominante_semana,
            "previsibilidade_%": percentual_semana
        })

    dominante_semana_df = pd.DataFrame(dominante_por_semana)
    st.dataframe(dominante_semana_df, use_container_width=True)

    st.divider()
    st.write(t["avg_time"])

    tempo_coluna = (
        df_respostas["tempo_resposta_segundos"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )

    tempo_coluna = pd.to_numeric(tempo_coluna, errors="coerce").astype(float)

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

    st.bar_chart(tempo_medio.set_index("tipo_experimento"))
    st.dataframe(tempo_medio)