import streamlit as st
import extra_streamlit_components as stx
import datetime
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import tempfile
from fpdf import FPDF
from dataclasses import dataclass

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Luvas x Cabos",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ajuste CSS para reduzir a largura da barra lateral
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] { min-width: 280px !important; }
    [data-testid="block-container"] {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- TELA DE LOGIN ---
# Gerenciador de Cookies (Persistência segura no navegador)
cookie_manager = stx.CookieManager()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Verifica se o cookie existe e é válido
if not st.session_state["logged_in"] and "logout_sync" not in st.session_state:
    cookie = cookie_manager.get("weg_auth")
    if cookie == "valid":
        st.session_state["logged_in"] = True

if not st.session_state["logged_in"]:
    st.image("logo.png", width=150)
    st.title("Login")
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

    if submit:
        if usuario.lower() == "weguser" and senha == "ParteAtivaGCV":
            st.session_state["logged_in"] = True
            # Cria o cookie com validade de 1 dia
            expires = datetime.datetime.now() + datetime.timedelta(days=1)
            cookie_manager.set("weg_auth", "valid", expires_at=expires)
            if "logout_sync" in st.session_state:
                del st.session_state["logout_sync"]
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")
    st.stop()

# --- Gerenciamento de Estado da Simulação ---
if "simulation_results" not in st.session_state:
    st.session_state.simulation_results = None

# ==============================================================================
# 1. DADOS DE ENTRADA (SIDEBAR)
# ==============================================================================
if st.sidebar.button("Sair (Logout)"):
    try:
        cookie_manager.delete("weg_auth")
    except Exception:
        pass
    st.session_state["logged_in"] = False
    st.session_state["logout_sync"] = True
    time.sleep(0.5)
    st.rerun()

st.sidebar.header("Parâmetros da Luva")

OPCOES_LUVA = {
    "25 mm²": 8.0,
    "35 mm²": 9.0,
    "50 mm²": 11.0,
    "70 mm²": 13.0,
    "95 mm²": 15.0,
    "120 mm²": 17.0,
    "150 mm²": 19.0,
    "185 mm²": 21.0,
    "240 mm²": 24.0,
    "300 mm²": 24.5,
    "400 mm²": 30.0,
    "500 mm²": 33.0,
    "630 mm²": 39.0,
    "Personalizado": 0.0,
}

lista_opcoes = (
    ["Automático"]
    + [k for k in OPCOES_LUVA.keys() if k != "Personalizado"]
    + ["Personalizado"]
)
escolha_luva = st.sidebar.selectbox("Seção Nominal da Luva", lista_opcoes, index=0)

if escolha_luva == "Personalizado":
    DIAM_LUVA = st.sidebar.number_input("Diâmetro da Luva (mm)", value=17.0, step=0.5)
elif escolha_luva == "Automático":
    DIAM_LUVA = 0.0  # Será definido durante a simulação
else:
    DIAM_LUVA = OPCOES_LUVA[escolha_luva]
    st.sidebar.markdown(f"**Diâmetro:** {DIAM_LUVA} mm")

st.sidebar.header("Fio Retangular")
ALT_RECT = st.sidebar.number_input("Axial (mm)", value=1.5, step=0.1)
LARG_RECT = st.sidebar.number_input("Radial (mm)", value=7.0, step=0.1)
QTD_RECT = st.sidebar.number_input("Quantidade", value=10, step=1)

st.sidebar.header("Cabo Circular")
excluir_circular = st.sidebar.checkbox(
    "Excluir Cabo Circular da Simulação", value=False
)

DIAM_REDONDO_TOTAL = 0.0
DIAM_MICRO_FIO = 0.8  # Valor padrão seguro

if not excluir_circular:
    OPCOES_CABO_CIRCULAR = {
        "50 mm²": 9.15,
        "70 mm²": 10.83,
        "120 mm²": 14.77,
        "185 mm²": 18.09,
        "240 mm²": 23.3,
        "300 mm²": 23.5,
        "400 mm²": 29.1,
        "500 mm²": 33.5,
        "Personalizado": 0.0,
    }
    escolha_cabo = st.sidebar.selectbox(
        "Seção Nominal do Cabo", list(OPCOES_CABO_CIRCULAR.keys())
    )

    if escolha_cabo == "Personalizado":
        DIAM_REDONDO_TOTAL = st.sidebar.number_input(
            "Diâmetro Equivalente Total (mm)", value=10.0, step=0.5
        )
    else:
        DIAM_REDONDO_TOTAL = OPCOES_CABO_CIRCULAR[escolha_cabo]
        st.sidebar.markdown(f"**Diâmetro:** {DIAM_REDONDO_TOTAL} mm")

    # Sincronização de Slider e Number Input para Micro-Fio
    if "micro_slider" not in st.session_state:
        st.session_state.micro_slider = 0.8
        st.session_state.micro_number = 0.8

    def sync_micro_from_slider():
        st.session_state.micro_number = st.session_state.micro_slider

    def sync_micro_from_number():
        st.session_state.micro_slider = st.session_state.micro_number

    st.sidebar.markdown(
        "Diâmetro do Micro-Fio (Granularidade)",
        help="O cabo circular é multifilamentoso (composto por vários fios finos). O diâmetro selecionado será o diâmetro da 'partição' criada na simulação. Quanto menor, mais preciso o preenchimento, porém mais lenta a simulação.",
    )
    col_mf1, col_mf2 = st.sidebar.columns([0.7, 1])
    with col_mf1:
        st.slider(
            "",
            0.4,
            2.0,
            key="micro_slider",
            on_change=sync_micro_from_slider,
            step=0.1,
            label_visibility="collapsed",
        )
    with col_mf2:
        st.number_input(
            "",
            0.4,
            2.0,
            key="micro_number",
            on_change=sync_micro_from_number,
            step=0.1,
            format="%.2f",
            label_visibility="collapsed",
        )

    DIAM_MICRO_FIO = st.session_state.micro_slider

st.sidebar.header("Configurações")

if "ocupacao_slider" not in st.session_state:
    st.session_state.ocupacao_slider = 85.0
    st.session_state.ocupacao_number = 85.0


def sync_ocupacao_from_slider():
    st.session_state.ocupacao_number = st.session_state.ocupacao_slider


def sync_ocupacao_from_number():
    st.session_state.ocupacao_slider = st.session_state.ocupacao_number


st.sidebar.markdown(
    "Limite de Ocupação (%)",
    help="Taxa de ocupação é a porcentagem da área interna da luva que é preenchida pelos condutores. O padrão é 85%, conforme WPR-33156 ES (WEG México).",
)
col_oc1, col_oc2 = st.sidebar.columns([0.7, 1])
with col_oc1:
    st.slider(
        "",
        0.0,
        100.0,
        key="ocupacao_slider",
        on_change=sync_ocupacao_from_slider,
        step=1.0,
        label_visibility="collapsed",
    )
with col_oc2:
    st.number_input(
        "",
        0.0,
        100.0,
        key="ocupacao_number",
        on_change=sync_ocupacao_from_number,
        step=1.0,
        format="%.2f",
        label_visibility="collapsed",
    )

LIMITE_OCUPACAO = st.session_state.ocupacao_slider / 100.0

# --- TÍTULO DA PÁGINA (DINÂMICO) ---
st.image("logo.png", width=150)
if excluir_circular:
    st.title("Simulação: Fio Retangular")
else:
    st.title("Simulação: Fio Retangular + Cabo Circular")
st.markdown(
    "Este aplicativo simula a montagem prática de luvas, verificando fisicamente se o condutor cabe na luva. Além disso, realiza a simulação utilizando cabos retangulares e circulares para validar o encaixe em luvas curtas."
)


# ==============================================================================
# 2. CLASSES E FUNÇÕES
# ==============================================================================
@dataclass
class Retangulo:
    x: float
    y: float
    w: float
    h: float


@dataclass
class Circulo:
    cx: float
    cy: float
    r: float


def gerar_grade_ordenada(raio, passo):
    eixo = np.arange(-raio, raio, passo)
    xx, yy = np.meshgrid(eixo, eixo)
    dist = xx**2 + yy**2
    mask = dist <= raio**2
    pontos = np.column_stack((xx[mask], yy[mask]))
    indices = np.argsort(pontos[:, 0] ** 2 + pontos[:, 1] ** 2)
    return pontos[indices]


def validar_rect(x, y, w, h, r_luva, rects):
    r2 = r_luva**2
    if (
        (x**2 + y**2 > r2)
        or ((x + w) ** 2 + y**2 > r2)
        or (x**2 + (y + h) ** 2 > r2)
        or ((x + w) ** 2 + (y + h) ** 2 > r2)
    ):
        return False
    for r in rects:
        if x < r.x + r.w and x + w > r.x and y < r.y + r.h and y + h > r.y:
            return False
    return True


def ponto_livre(cx, cy, r_micro, r_luva, rects, micro_circs_existentes):
    if np.sqrt(cx**2 + cy**2) + r_micro > r_luva:
        return False
    for r in rects:
        closest_x = max(r.x, min(cx, r.x + r.w))
        closest_y = max(r.y, min(cy, r.y + r.h))
        dist_sq = (cx - closest_x) ** 2 + (cy - closest_y) ** 2
        if dist_sq < r_micro**2:
            return False
    for c in micro_circs_existentes:
        if (cx - c.cx) ** 2 + (cy - c.cy) ** 2 < (2 * r_micro) ** 2:
            return False
    return True


# ==============================================================================
# 3. LÓGICA PRINCIPAL (EXECUTADA AO CLICAR NO BOTÃO)
# ==============================================================================

if st.sidebar.button("Executar Simulação", type="primary"):
    start_time = time.time()

    # --- BARRA DE PROGRESSO E STATUS ---
    progress_bar = st.progress(0)
    status_text = st.empty()
    logs = ["Limpando simulação antiga e iniciando..."]
    status_text.text("\n".join(logs))

    # --- CÁLCULOS INICIAIS ---
    area_rect_total = QTD_RECT * LARG_RECT * ALT_RECT
    r_redondo_total = DIAM_REDONDO_TOTAL / 2
    area_redondo_total = np.pi * r_redondo_total**2
    area_total_ocupada = area_rect_total + area_redondo_total

    nome_exibicao = escolha_luva

    # --- RESOLUÇÃO AUTOMÁTICA DE LUVA ---
    if escolha_luva == "Automático":
        logs.append("Fase 1: Selecionando Luva...")
        status_text.text("\n".join(logs))
        t_phase = time.time()
        opcoes_ordenadas = sorted(
            [(k, v) for k, v in OPCOES_LUVA.items() if k != "Personalizado"],
            key=lambda x: x[1],
        )
        encontrou_auto = False

        for nome, diam in opcoes_ordenadas:
            r_cand = diam / 2
            area_cand = np.pi * r_cand**2

            # 1. Validação de Área
            if area_total_ocupada / area_cand > LIMITE_OCUPACAO:
                continue

            # 2. Validação Física Rápida (Passo 0.1)
            if QTD_RECT == 0:
                DIAM_LUVA = diam
                nome_exibicao = nome
                encontrou_auto = True
                break

            grade_cand = gerar_grade_ordenada(r_cand, 0.1)
            encaixou_cand = False

            # Definição das estratégias baseada na paridade
            configs_auto = []
            if QTD_RECT % 2 == 0:
                # Para PARES: Tenta primeiro simetria estrita (gap central), depois simetria relaxada (preenche centro se necessário)
                configs_auto = [
                    (0, "DuploX"),
                    (0, "DuploY"),
                    (1, "DuploX"),
                    (1, "DuploY"),
                    (0, "DuploX_Full"),
                    (0, "DuploY_Full"),
                    (1, "DuploX_Full"),
                    (1, "DuploY_Full"),
                ]
            else:
                # Para ÍMPARES: Prioriza o Centro, mas permite estratégias duplas (assimétricas)
                configs_auto = [
                    (0, "Centro"),
                    (1, "Centro"),
                    (0, "DuploX"),
                    (0, "DuploY"),
                    (1, "DuploX"),
                    (1, "DuploY"),
                    (0, "DuploX_Full"),
                    (0, "DuploY_Full"),
                    (1, "DuploX_Full"),
                    (1, "DuploY_Full"),
                ]

            for sentido, estrategia in configs_auto:
                w = LARG_RECT if sentido == 0 else ALT_RECT
                h = ALT_RECT if sentido == 0 else LARG_RECT

                if estrategia == "Centro":
                    grade_sorted = grade_cand
                    rects_temp = []
                    for _ in range(QTD_RECT):
                        for p in grade_sorted:
                            tx, ty = p[0] - w / 2, p[1] - h / 2
                            if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                rects_temp.append(Retangulo(tx, ty, w, h))
                                break
                elif estrategia == "DuploX":  # Divide em X (Esquerda/Direita)
                    # Filtra pontos estritamente em cada lado para garantir o gap central
                    mask_L = grade_cand[:, 0] <= -w / 2 + 1e-5
                    mask_R = grade_cand[:, 0] >= w / 2 - 1e-5

                    d_L = (grade_cand[mask_L][:, 0] + w / 2) ** 2 + grade_cand[mask_L][
                        :, 1
                    ] ** 2
                    d_R = (grade_cand[mask_R][:, 0] - w / 2) ** 2 + grade_cand[mask_R][
                        :, 1
                    ] ** 2

                    g_L = grade_cand[mask_L][np.argsort(d_L)]
                    g_R = grade_cand[mask_R][np.argsort(d_R)]

                    rects_temp = []
                    idx_L, idx_R = 0, 0
                    # Alterna estritamente: Esq, Dir, Esq, Dir...
                    for i in range(QTD_RECT):
                        placed = False
                        if i % 2 == 0:  # Tenta Esquerda
                            while idx_L < len(g_L):
                                p = g_L[idx_L]
                                idx_L += 1
                                tx, ty = p[0] - w / 2, p[1] - h / 2
                                if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                    rects_temp.append(Retangulo(tx, ty, w, h))
                                    placed = True
                                    break
                        else:  # Tenta Direita
                            while idx_R < len(g_R):
                                p = g_R[idx_R]
                                idx_R += 1
                                tx, ty = p[0] - w / 2, p[1] - h / 2
                                if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                    rects_temp.append(Retangulo(tx, ty, w, h))
                                    placed = True
                                    break
                        if not placed:
                            break

                elif (
                    estrategia == "DuploX_Full"
                ):  # Divide em X mas permite preencher o centro (sem mask)
                    d2 = np.minimum(
                        (grade_cand[:, 0] + w / 2) ** 2 + grade_cand[:, 1] ** 2,
                        (grade_cand[:, 0] - w / 2) ** 2 + grade_cand[:, 1] ** 2,
                    )
                    grade_sorted = grade_cand[np.argsort(d2)]
                    rects_temp = []
                    for _ in range(QTD_RECT):
                        for p in grade_sorted:
                            tx, ty = p[0] - w / 2, p[1] - h / 2
                            if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                rects_temp.append(Retangulo(tx, ty, w, h))
                                break
                elif (
                    estrategia == "DuploY_Full"
                ):  # Divide em Y mas permite preencher o centro (sem mask)
                    d2 = np.minimum(
                        grade_cand[:, 0] ** 2 + (grade_cand[:, 1] - h / 2) ** 2,
                        grade_cand[:, 0] ** 2 + (grade_cand[:, 1] + h / 2) ** 2,
                    )
                    grade_sorted = grade_cand[np.argsort(d2)]
                    rects_temp = []
                    for _ in range(QTD_RECT):
                        for p in grade_sorted:
                            tx, ty = p[0] - w / 2, p[1] - h / 2
                            if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                rects_temp.append(Retangulo(tx, ty, w, h))
                                break

                elif estrategia == "DuploY":  # Divide em Y (Cima/Baixo)
                    mask_T = grade_cand[:, 1] >= h / 2 - 1e-5
                    mask_B = grade_cand[:, 1] <= -h / 2 + 1e-5

                    d_T = (
                        grade_cand[mask_T][:, 0] ** 2
                        + (grade_cand[mask_T][:, 1] - h / 2) ** 2
                    )
                    d_B = (
                        grade_cand[mask_B][:, 0] ** 2
                        + (grade_cand[mask_B][:, 1] + h / 2) ** 2
                    )

                    g_T = grade_cand[mask_T][np.argsort(d_T)]
                    g_B = grade_cand[mask_B][np.argsort(d_B)]

                    rects_temp = []
                    idx_T, idx_B = 0, 0
                    for i in range(QTD_RECT):
                        placed = False
                        if i % 2 == 0:  # Tenta Cima
                            while idx_T < len(g_T):
                                p = g_T[idx_T]
                                idx_T += 1
                                tx, ty = p[0] - w / 2, p[1] - h / 2
                                if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                    rects_temp.append(Retangulo(tx, ty, w, h))
                                    placed = True
                                    break
                        else:  # Tenta Baixo
                            while idx_B < len(g_B):
                                p = g_B[idx_B]
                                idx_B += 1
                                tx, ty = p[0] - w / 2, p[1] - h / 2
                                if validar_rect(tx, ty, w, h, r_cand, rects_temp):
                                    rects_temp.append(Retangulo(tx, ty, w, h))
                                    placed = True
                                    break
                        if not placed:
                            break

                if len(rects_temp) == QTD_RECT:
                    encaixou_cand = True
                    break

            if encaixou_cand:
                DIAM_LUVA = diam
                nome_exibicao = nome
                encontrou_auto = True
                break

        if not encontrou_auto:
            nome_exibicao = opcoes_ordenadas[-1][0]
            DIAM_LUVA = opcoes_ordenadas[-1][1]
            st.warning(
                f"Automático: Nenhuma luva padrão atende aos critérios. Usando a maior disponível ({nome_exibicao})."
            )
        else:
            st.success(
                f"Automático: Luva selecionada **{nome_exibicao}** ({DIAM_LUVA} mm)"
            )
        logs[-1] += f" ({time.time() - t_phase:.2f}s)"
        status_text.text("\n".join(logs))

    progress_bar.progress(33)
    r_luva = DIAM_LUVA / 2
    area_luva = np.pi * r_luva**2
    r_micro = DIAM_MICRO_FIO / 2
    area_micro = np.pi * r_micro**2

    qtd_micro_fios = 0
    if area_redondo_total > 0 and area_micro > 0:
        # Utiliza a área total do envelope, ajustada pelo limite geométrico de empacotamento (aprox 90%)
        # para evitar solicitar uma quantidade fisicamente impossível (100% sólido).
        qtd_micro_fios = int((area_redondo_total * 0.90) / area_micro)

    taxa = area_total_ocupada / area_luva

    if area_total_ocupada > area_luva:
        st.error(
            "ERRO FATAL: A área dos cabos é maior que a área da luva! Impossível calcular."
        )
        st.stop()

    if taxa > LIMITE_OCUPACAO:
        st.warning(
            f"ALERTA: Taxa de ocupação acima do limite configurado ({LIMITE_OCUPACAO * 100:.0f}%)"
        )

    # --- FASE 1: RETÂNGULOS ---
    logs.append("Fase 2: Posicionando Fio Retangular...")
    status_text.text("\n".join(logs))
    t_phase = time.time()
    grade_rect = gerar_grade_ordenada(r_luva, 0.05)

    melhor_rects = []
    melhor_score = -1
    orientacao_final = ""

    # Definição das estratégias para Fase 2
    configs = []
    if QTD_RECT % 2 == 0:
        # Pares: Prioriza simetria estrita, mas tenta relaxada se couber mais
        configs = [
            (0, "DuploX"),
            (0, "DuploY"),
            (1, "DuploX"),
            (1, "DuploY"),
            (0, "DuploX_Full"),
            (0, "DuploY_Full"),
            (1, "DuploX_Full"),
            (1, "DuploY_Full"),
        ]
    else:
        # Ímpares: Centro + Simétricas + Full (permite assimetria para melhor encaixe)
        configs = [
            (0, "Centro"),
            (1, "Centro"),
            (0, "DuploX"),
            (0, "DuploY"),
            (1, "DuploX"),
            (1, "DuploY"),
            (0, "DuploX_Full"),
            (0, "DuploY_Full"),
            (1, "DuploX_Full"),
            (1, "DuploY_Full"),
        ]

    for sentido, estrategia in configs:
        w = LARG_RECT if sentido == 0 else ALT_RECT
        h = ALT_RECT if sentido == 0 else LARG_RECT

        # Ordena a grade de pontos baseada na estratégia
        if estrategia == "Centro":
            grade_sorted = grade_rect
            rects_temp = []
            for _ in range(QTD_RECT):
                for p in grade_sorted:
                    tx, ty = p[0] - w / 2, p[1] - h / 2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h))
                        break
        elif estrategia == "DuploX":
            mask_L = grade_rect[:, 0] <= -w / 2 + 1e-5
            mask_R = grade_rect[:, 0] >= w / 2 - 1e-5

            d_L = (grade_rect[mask_L][:, 0] + w / 2) ** 2 + grade_rect[mask_L][
                :, 1
            ] ** 2
            d_R = (grade_rect[mask_R][:, 0] - w / 2) ** 2 + grade_rect[mask_R][
                :, 1
            ] ** 2

            g_L = grade_rect[mask_L][np.argsort(d_L)]
            g_R = grade_rect[mask_R][np.argsort(d_R)]

            rects_temp = []
            idx_L, idx_R = 0, 0
            for i in range(QTD_RECT):
                placed = False
                if i % 2 == 0:  # Tenta Esquerda
                    while idx_L < len(g_L):
                        p = g_L[idx_L]
                        idx_L += 1
                        tx, ty = p[0] - w / 2, p[1] - h / 2
                        if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                            rects_temp.append(Retangulo(tx, ty, w, h))
                            placed = True
                            break
                else:  # Tenta Direita
                    while idx_R < len(g_R):
                        p = g_R[idx_R]
                        idx_R += 1
                        tx, ty = p[0] - w / 2, p[1] - h / 2
                        if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                            rects_temp.append(Retangulo(tx, ty, w, h))
                            placed = True
                            break
                if not placed:
                    break

        elif estrategia == "DuploX_Full":
            d2 = np.minimum(
                (grade_rect[:, 0] + w / 2) ** 2 + grade_rect[:, 1] ** 2,
                (grade_rect[:, 0] - w / 2) ** 2 + grade_rect[:, 1] ** 2,
            )
            grade_sorted = grade_rect[np.argsort(d2)]
            rects_temp = []
            for _ in range(QTD_RECT):
                for p in grade_sorted:
                    tx, ty = p[0] - w / 2, p[1] - h / 2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h))
                        break
        elif estrategia == "DuploY_Full":
            d2 = np.minimum(
                grade_rect[:, 0] ** 2 + (grade_rect[:, 1] - h / 2) ** 2,
                grade_rect[:, 0] ** 2 + (grade_rect[:, 1] + h / 2) ** 2,
            )
            grade_sorted = grade_rect[np.argsort(d2)]
            rects_temp = []
            for _ in range(QTD_RECT):
                for p in grade_sorted:
                    tx, ty = p[0] - w / 2, p[1] - h / 2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h))
                        break

        elif estrategia == "DuploY":
            mask_T = grade_rect[:, 1] >= h / 2 - 1e-5
            mask_B = grade_rect[:, 1] <= -h / 2 + 1e-5

            d_T = (
                grade_rect[mask_T][:, 0] ** 2 + (grade_rect[mask_T][:, 1] - h / 2) ** 2
            )
            d_B = (
                grade_rect[mask_B][:, 0] ** 2 + (grade_rect[mask_B][:, 1] + h / 2) ** 2
            )

            g_T = grade_rect[mask_T][np.argsort(d_T)]
            g_B = grade_rect[mask_B][np.argsort(d_B)]

            rects_temp = []
            idx_T, idx_B = 0, 0
            for i in range(QTD_RECT):
                placed = False
                if i % 2 == 0:  # Tenta Cima
                    while idx_T < len(g_T):
                        p = g_T[idx_T]
                        idx_T += 1
                        tx, ty = p[0] - w / 2, p[1] - h / 2
                        if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                            rects_temp.append(Retangulo(tx, ty, w, h))
                            placed = True
                            break
                else:  # Tenta Baixo
                    while idx_B < len(g_B):
                        p = g_B[idx_B]
                        idx_B += 1
                        tx, ty = p[0] - w / 2, p[1] - h / 2
                        if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                            rects_temp.append(Retangulo(tx, ty, w, h))
                            placed = True
                            break
                if not placed:
                    break

        if len(rects_temp) > melhor_score:
            melhor_score = len(rects_temp)
            melhor_rects = rects_temp
            orientacao_final = "Horizontal" if sentido == 0 else "Vertical"
            if "Duplo" in estrategia:
                orientacao_final += " (Simétrico)"

    logs[-1] += f" ({time.time() - t_phase:.2f}s)"
    status_text.text("\n".join(logs))

    progress_bar.progress(66)

    # --- FASE 2: CABO FLEXÍVEL ---
    micro_fios = []
    if not excluir_circular:
        logs.append("Fase 3: Posicionando Cabo Circular...")
        status_text.text("\n".join(logs))
        t_phase = time.time()
        fios_restantes = qtd_micro_fios
        grade_fios = gerar_grade_ordenada(r_luva, DIAM_MICRO_FIO * 0.2)

        for p in grade_fios:
            if fios_restantes <= 0:
                break
            cx, cy = p[0], p[1]
            if ponto_livre(cx, cy, r_micro, r_luva, melhor_rects, micro_fios):
                micro_fios.append(Circulo(cx, cy, r_micro))
                fios_restantes -= 1

        logs[-1] += f" ({time.time() - t_phase:.2f}s)"
        status_text.text("\n".join(logs))

    progress_bar.progress(100)
    area_real_fios = len(micro_fios) * area_micro

    end_time = time.time()
    elapsed_time = end_time - start_time
    logs.append(f"Simulação Concluída! ({elapsed_time:.1f}s)")
    status_text.text("\n".join(logs))

    # --- CÁLCULO REAL PÓS-SIMULAÇÃO ---
    # A área total ocupada é a soma da área dos retângulos que couberam
    # mais a área dos micro-fios que couberam, para refletir a realidade visual.
    area_rect_real = len(melhor_rects) * LARG_RECT * ALT_RECT
    area_total_ocupada_real = area_rect_real + area_real_fios
    taxa_real = area_total_ocupada_real / area_luva if area_luva > 0 else 0

    # --- Armazena todos os resultados em session_state ---
    st.session_state.simulation_results = {
        "area_rect_total": area_rect_total,
        "area_redondo_total": area_redondo_total,  # Áreas teóricas para referência
        "area_luva": area_luva,
        "DIAM_LUVA": DIAM_LUVA,
        "LARG_RECT": LARG_RECT,
        "ALT_RECT": ALT_RECT,
        "QTD_RECT": QTD_RECT,
        "excluir_circular": excluir_circular,
        "melhor_rects": melhor_rects,
        "micro_fios": micro_fios,
        "taxa": taxa_real,
        "LIMITE_OCUPACAO": LIMITE_OCUPACAO,
        "area_total_ocupada": area_total_ocupada_real,
        "orientacao_final": orientacao_final,
        "qtd_micro_fios": qtd_micro_fios,
        "nome_exibicao": nome_exibicao,
        "elapsed_time": elapsed_time,
        "logs": logs,
        "cabo_selecionado": escolha_cabo if not excluir_circular else "N/A",
        "DIAM_MICRO_FIO": DIAM_MICRO_FIO,
    }
    st.rerun()

# --- Bloco de Renderização (executado sempre que há resultados) ---
if st.session_state.simulation_results:
    st.progress(100)
    res = st.session_state.simulation_results

    # --- RENDERIZAÇÃO DOS RESULTADOS ---
    col_dados, col_desenho = st.columns([1.2, 1])

    with col_dados:
        st.markdown("#### Dados das Seções")
        if not res["excluir_circular"]:
            c1, c2, c3 = st.columns(3)
            c1.metric(
                "Fio Retangular",
                f"{res['area_rect_total']:.2f} mm²",
                help=f"Unitário: {res['LARG_RECT']}x{res['ALT_RECT']} mm | Qtd: {res['QTD_RECT']}",
            )
            c2.metric("Cabo Circular", f"{res['area_redondo_total']:.2f} mm²")
            c3.metric(
                "Luva",
                f"{res['area_luva']:.2f} mm²",
                help=f"Diâmetro: {res['DIAM_LUVA']} mm",
            )
        else:
            c1, c2 = st.columns(2)
            c1.metric(
                "Fio Retangular",
                f"{res['area_rect_total']:.2f} mm²",
                help=f"Unitário: {res['LARG_RECT']}x{res['ALT_RECT']} mm | Qtd: {res['QTD_RECT']}",
            )
            c2.metric(
                "Luva",
                f"{res['area_luva']:.2f} mm²",
                help=f"Diâmetro: {res['DIAM_LUVA']} mm",
            )

        st.markdown("---")
        st.markdown("#### Indicadores")

        i1, i2, i3 = st.columns(3)
        delta_rect = len(res["melhor_rects"]) - res["QTD_RECT"]
        i1.metric(
            "Fios",
            f"{len(res['melhor_rects'])} / {res['QTD_RECT']}",
            delta=int(delta_rect) if delta_rect < 0 else None,
        )

        delta_taxa = (res["taxa"] - res["LIMITE_OCUPACAO"]) * 100
        i2.metric(
            "Ocupação",
            f"{res['taxa'] * 100:.1f}%",
            delta=f"{delta_taxa:.1f}%",
            delta_color="inverse",
        )

        i3.metric("Área Total", f"{res['area_total_ocupada']:.2f} mm²")

    with col_desenho:
        # --- VISUALIZAÇÃO ---
        fig, ax = plt.subplots(figsize=(2.5, 2.5))
        r_luva = res["DIAM_LUVA"] / 2

        # Desenhos
        ax.add_patch(patches.Circle((0, 0), r_luva, color="#F0F0F0", zorder=0))
        ax.add_patch(
            patches.Circle(
                (0, 0), r_luva, fill=False, color="black", lw=0.75, zorder=10
            )
        )

        for r in res["melhor_rects"]:
            ax.add_patch(
                patches.Rectangle(
                    (r.x, r.y), r.w, r.h, ec="black", fc="#4169E1", zorder=5, lw=0.5
                )
            )

        for c in res["micro_fios"]:
            ax.add_patch(patches.Circle((c.cx, c.cy), c.r, color="#FF8C00", zorder=4))

        # Adiciona a cruz vermelha no centro
        ax.axhline(0, color="red", linewidth=0.6, linestyle="--", zorder=11)
        ax.axvline(0, color="red", linewidth=0.6, linestyle="--", zorder=11)

        ax.set_xlim(-r_luva * 1.1, r_luva * 1.1)
        ax.set_ylim(-r_luva * 1.1, r_luva * 1.1)
        ax.set_aspect("equal")

        # Configuração dos eixos e grade
        max_tick = int(np.ceil(res["DIAM_LUVA"]))
        max_tick = ((max_tick + 4) // 5) * 5

        # Labels de 0 até o diâmetro
        tick_labels = np.arange(0, max_tick + 1, 5)
        # Posições no gráfico (deslocadas pelo raio, pois o centro é 0,0)
        tick_positions = tick_labels - r_luva

        ax.set_xticks(tick_positions)
        ax.set_yticks(tick_positions)
        ax.set_xticklabels(tick_labels)
        ax.set_yticklabels(tick_labels)

        ax.tick_params(axis="both", which="major", labelsize=4)  # Fonte bem pequena
        ax.set_xlabel("Radial", fontsize=4)
        ax.set_ylabel("Axial", fontsize=4)
        ax.grid(True, linestyle=":", linewidth=0.4, color="grey")

        ax.set_title(
            f"Luva {res['nome_exibicao']} - Diâmetro {res['DIAM_LUVA']} mm", fontsize=8
        )

        # Salva imagem temporária para o relatório PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, format="png", dpi=300, bbox_inches="tight")
            tmp_img_path = tmpfile.name

        st.pyplot(fig, use_container_width=False)
        plt.close(fig)  # Libera memória da figura

    # Resultados Finais em Texto
    # Define as condições de falha/sucesso
    falha_retangulos = len(res["melhor_rects"]) < res["QTD_RECT"]
    falha_ocupacao = res["taxa"] > res["LIMITE_OCUPACAO"]

    falha_circular = False
    if not res["excluir_circular"] and res["qtd_micro_fios"] > 0:
        if len(res["micro_fios"]) < res["qtd_micro_fios"]:
            falha_circular = True

    simulacao_aprovada = not (falha_retangulos or falha_ocupacao or falha_circular)

    if simulacao_aprovada:
        mensagem = f"Simulação Aprovada! Orientação: {res['orientacao_final']} | Retangular: {len(res['melhor_rects'])}/{res['QTD_RECT']}"
        if not res["excluir_circular"]:
            percentual_circular = 0
            if res["qtd_micro_fios"] > 0:
                percentual_circular = (
                    len(res["micro_fios"]) / res["qtd_micro_fios"]
                ) * 100
            mensagem += f" | Circular: {percentual_circular:.0f}%"
        st.success(f"{mensagem} | Tempo: {res['elapsed_time']:.2f}s")
    else:
        motivos = []
        if falha_retangulos:
            motivos.append(f"Fios: {len(res['melhor_rects'])}/{res['QTD_RECT']}")
        if falha_circular:
            percentual = (len(res["micro_fios"]) / res["qtd_micro_fios"]) * 100
            motivos.append(
                f"Circular: {len(res['micro_fios'])}/{res['qtd_micro_fios']} ({percentual:.0f}%)"
            )
        if falha_ocupacao:
            motivos.append(
                f"Ocupação: {res['taxa'] * 100:.1f}% (Limite: {res['LIMITE_OCUPACAO'] * 100:.0f}%)"
            )

        st.error(
            f"Simulação Reprovada! Motivo(s): {', '.join(motivos)} | Tempo: {res['elapsed_time']:.2f}s"
        )

    st.markdown("#### Logs da Simulação")
    st.text("\n".join(res["logs"]))

    # --- GERAÇÃO DO RELATÓRIO PDF ---
    def create_pdf(res, img_path, aprovado, msg_status):
        class PDF(FPDF):
            def footer(self):
                self.set_y(-15)
                self.set_font("Arial", "I", 8)
                self.cell(
                    0,
                    10,
                    "Desenvolvido por: DELLAZARIG - Parte Ativa Gravataí",
                    0,
                    0,
                    "C",
                )

        pdf = PDF()
        pdf.add_page()

        # Cabeçalho
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Relatório de Simulação: Luvas x Cabos", ln=True, align="C")
        pdf.set_font("Arial", "I", 10)
        # Ajuste para horário de Brasília (UTC-3)
        fuso_br = datetime.timezone(datetime.timedelta(hours=-3))
        pdf.cell(
            0,
            10,
            f"Gerado em: {datetime.datetime.now(fuso_br).strftime('%d/%m/%Y %H:%M')}",
            ln=True,
            align="C",
        )
        pdf.ln(5)

        # Dados de Entrada (Layout 2 Colunas)
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Dados de Entrada", ln=True, fill=True)
        pdf.ln(2)
        pdf.set_font("Arial", "", 10)

        # Coluna 1: Luva, Fio Retangular, Qtd
        # Coluna 2: Cabo, Granularidade, Limite

        # Linha 1
        pdf.cell(
            95,
            6,
            f"Luva: {res['nome_exibicao']} (Diam: {res['DIAM_LUVA']} mm)",
            border=0,
        )
        pdf.cell(95, 6, f"Cabo: {res['cabo_selecionado']}", border=0, ln=True)

        # Linha 2
        pdf.cell(
            95,
            6,
            f"Fio Retangular: {res['LARG_RECT']} x {res['ALT_RECT']} mm",
            border=0,
        )
        gran_txt = (
            f"{res['DIAM_MICRO_FIO']} mm" if not res["excluir_circular"] else "N/A"
        )
        pdf.cell(95, 6, f"Granularidade: {gran_txt}", border=0, ln=True)

        # Linha 3
        pdf.cell(95, 6, f"Fios Retangulares: {res['QTD_RECT']}", border=0)
        pdf.cell(
            95,
            6,
            f"Limite Ocupação: {res['LIMITE_OCUPACAO'] * 100:.1f}%",
            border=0,
            ln=True,
        )

        pdf.ln(5)

        # Tabela de Resultados
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Resultados Calculados", ln=True, fill=True)
        pdf.ln(2)
        pdf.set_font("Arial", "", 10)

        pdf.cell(63, 7, f"Ocupação Real: {res['taxa'] * 100:.1f}%", border=0)
        pdf.cell(63, 7, f"Área Ocupada: {res['area_total_ocupada']:.2f} mm2", border=0)
        pdf.cell(64, 7, f"Área Luva: {res['area_luva']:.2f} mm2", border=0, ln=True)

        pdf.cell(
            95,
            7,
            f"Fios Retangulares: {len(res['melhor_rects'])} / {res['QTD_RECT']}",
            border=0,
        )
        qtd_circ = (
            f"{len(res['micro_fios'])} / {res['qtd_micro_fios']}"
            if not res["excluir_circular"]
            else "-"
        )
        pdf.cell(95, 7, f"Micro-fios Circulares: {qtd_circ}", border=0, ln=True)

        pdf.ln(10)

        # Status da Simulação
        pdf.set_font("Arial", "B", 16)
        if aprovado:
            pdf.set_text_color(0, 128, 0)  # Verde
            pdf.cell(0, 10, "RESULTADO: APROVADO", ln=True, align="C")
        else:
            pdf.set_text_color(255, 0, 0)  # Vermelho
            pdf.cell(0, 10, "RESULTADO: REPROVADO", ln=True, align="C")

        pdf.set_text_color(0, 0, 0)

        # Imagem Centralizada (Largura A4 ~210mm)
        pdf.image(img_path, x=55, w=100)

        return pdf.output(dest="S").encode("latin-1")

    # Prepara mensagem e gera PDF
    msg_pdf = (
        mensagem if simulacao_aprovada else f"Reprovado. Motivos: {', '.join(motivos)}"
    )
    try:
        pdf_bytes = create_pdf(res, tmp_img_path, simulacao_aprovada, msg_pdf)
        # Ajuste para horário de Brasília (UTC-3)
        fuso_br = datetime.timezone(datetime.timedelta(hours=-3))
        st.download_button(
            label="📄 Baixar Relatório (PDF)",
            data=pdf_bytes,
            file_name=f"Relatorio_Simulacao_{datetime.datetime.now(fuso_br).strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            type="primary",
        )
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
    finally:
        if os.path.exists(tmp_img_path):
            os.remove(tmp_img_path)

st.markdown("---")
st.markdown("Desenvolvido por: DELLAZARIG - Parte Ativa Gravataí")
