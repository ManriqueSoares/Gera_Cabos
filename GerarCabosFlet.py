import matplotlib
matplotlib.use('Agg')

import flet as ft
import datetime
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import tempfile
import json
import base64
import io
import threading
from fpdf import FPDF
from dataclasses import dataclass
from typing import List, Optional

# ==============================================================================
# CONSTANTES
# ==============================================================================
OPCOES_LUVA = {
    "25 mm²": 8.0, "35 mm²": 9.0, "50 mm²": 11.0, "70 mm²": 13.0,
    "95 mm²": 15.0, "120 mm²": 17.0, "150 mm²": 19.0, "185 mm²": 21.0,
    "240 mm²": 24.0, "300 mm²": 24.5, "400 mm²": 30.0, "500 mm²": 33.0,
    "630 mm²": 39.0, "Personalizado": 0.0
}

OPCOES_CABO_CIRCULAR = {
    "50 mm²": 9.15, "70 mm²": 10.83, "120 mm²": 14.77,
    "185 mm²": 18.09, "240 mm²": 23.3, "300 mm²": 23.5,
    "400 mm²": 29.1, "500 mm²": 33.5, "Personalizado": 0.0
}

AUTH_FILE = os.path.join(os.path.expanduser("~"), ".gcv_auth.json")
ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))


# ==============================================================================
# DATA CLASSES
# ==============================================================================
@dataclass
class Retangulo:
    x: float; y: float; w: float; h: float

@dataclass
class Circulo:
    cx: float; cy: float; r: float


# ==============================================================================
# FUNÇÕES DE SIMULAÇÃO
# ==============================================================================
def gerar_grade_ordenada(raio, passo):
    eixo = np.arange(-raio, raio, passo)
    xx, yy = np.meshgrid(eixo, eixo)
    dist = xx**2 + yy**2
    mask = dist <= raio**2
    pontos = np.column_stack((xx[mask], yy[mask]))
    indices = np.argsort(pontos[:,0]**2 + pontos[:,1]**2)
    return pontos[indices]


def validar_rect(x, y, w, h, r_luva, rects):
    r2 = r_luva**2
    if (x**2+y**2 > r2) or ((x+w)**2+y**2 > r2) or \
       (x**2+(y+h)**2 > r2) or ((x+w)**2+(y+h)**2 > r2):
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
        dist_sq = (cx - closest_x)**2 + (cy - closest_y)**2
        if dist_sq < r_micro**2:
            return False
    for c in micro_circs_existentes:
        if (cx - c.cx)**2 + (cy - c.cy)**2 < (2 * r_micro)**2:
            return False
    return True


def posicionar_rects(grade, QTD_RECT, LARG_RECT, ALT_RECT, r_luva, configs):
    melhor_rects = []
    melhor_score = -1
    orientacao_final = ""

    for sentido, estrategia in configs:
        w = LARG_RECT if sentido == 0 else ALT_RECT
        h = ALT_RECT if sentido == 0 else LARG_RECT
        rects_temp = []

        if estrategia == "Centro":
            for _ in range(QTD_RECT):
                for p in grade:
                    tx, ty = p[0] - w/2, p[1] - h/2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h))
                        break

        elif estrategia == "DuploX":
            mask_L = grade[:,0] <= -w/2 + 1e-5
            mask_R = grade[:,0] >= w/2 - 1e-5
            d_L = (grade[mask_L][:,0] + w/2)**2 + grade[mask_L][:,1]**2
            d_R = (grade[mask_R][:,0] - w/2)**2 + grade[mask_R][:,1]**2
            g_L = grade[mask_L][np.argsort(d_L)]
            g_R = grade[mask_R][np.argsort(d_R)]
            idx_L, idx_R = 0, 0
            for i in range(QTD_RECT):
                placed = False
                if i % 2 == 0:
                    while idx_L < len(g_L):
                        p = g_L[idx_L]; idx_L += 1
                        tx, ty = p[0] - w/2, p[1] - h/2
                        if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                            rects_temp.append(Retangulo(tx, ty, w, h)); placed = True; break
                else:
                    while idx_R < len(g_R):
                        p = g_R[idx_R]; idx_R += 1
                        tx, ty = p[0] - w/2, p[1] - h/2
                        if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                            rects_temp.append(Retangulo(tx, ty, w, h)); placed = True; break
                if not placed:
                    break

        elif estrategia == "DuploX_Full":
            d2 = np.minimum((grade[:,0] + w/2)**2 + grade[:,1]**2, (grade[:,0] - w/2)**2 + grade[:,1]**2)
            grade_sorted = grade[np.argsort(d2)]
            for _ in range(QTD_RECT):
                for p in grade_sorted:
                    tx, ty = p[0] - w/2, p[1] - h/2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h)); break

        elif estrategia == "DuploY_Full":
            d2 = np.minimum(grade[:,0]**2 + (grade[:,1] - h/2)**2, grade[:,0]**2 + (grade[:,1] + h/2)**2)
            grade_sorted = grade[np.argsort(d2)]
            for _ in range(QTD_RECT):
                for p in grade_sorted:
                    tx, ty = p[0] - w/2, p[1] - h/2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h)); break

        elif estrategia == "DuploY":
            mask_T = grade[:,1] >= h/2 - 1e-5
            mask_B = grade[:,1] <= -h/2 + 1e-5
            d_T = grade[mask_T][:,0]**2 + (grade[mask_T][:,1] - h/2)**2
            d_B = grade[mask_B][:,0]**2 + (grade[mask_B][:,1] + h/2)**2
            g_T = grade[mask_T][np.argsort(d_T)]
            g_B = grade[mask_B][np.argsort(d_B)]
            idx_T, idx_B = 0, 0
            for i in range(QTD_RECT):
                placed = False
                if i % 2 == 0:
                    while idx_T < len(g_T):
                        p = g_T[idx_T]; idx_T += 1
                        tx, ty = p[0] - w/2, p[1] - h/2
                        if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                            rects_temp.append(Retangulo(tx, ty, w, h)); placed = True; break
                else:
                    while idx_B < len(g_B):
                        p = g_B[idx_B]; idx_B += 1
                        tx, ty = p[0] - w/2, p[1] - h/2
                        if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                            rects_temp.append(Retangulo(tx, ty, w, h)); placed = True; break
                if not placed:
                    break

        if len(rects_temp) > melhor_score:
            melhor_score = len(rects_temp)
            melhor_rects = rects_temp[:]
            orientacao_final = "Horizontal" if sentido == 0 else "Vertical"
            if "Duplo" in estrategia:
                orientacao_final += " (Simétrico)"

    return melhor_rects, orientacao_final


def run_simulation(params):
    start_time = time.time()

    escolha_luva     = params["escolha_luva"]
    DIAM_LUVA        = params["DIAM_LUVA"]
    ALT_RECT         = params["ALT_RECT"]
    LARG_RECT        = params["LARG_RECT"]
    QTD_RECT         = params["QTD_RECT"]
    excluir_circular = params["excluir_circular"]
    DIAM_REDONDO_TOTAL = params["DIAM_REDONDO_TOTAL"]
    DIAM_MICRO_FIO   = params["DIAM_MICRO_FIO"]
    LIMITE_OCUPACAO  = params["LIMITE_OCUPACAO"]
    escolha_cabo     = params.get("escolha_cabo", "N/A")

    logs = ["Iniciando simulação..."]

    area_rect_total    = QTD_RECT * LARG_RECT * ALT_RECT
    r_redondo_total    = DIAM_REDONDO_TOTAL / 2
    area_redondo_total = np.pi * r_redondo_total**2
    area_total_ocupada = area_rect_total + area_redondo_total
    nome_exibicao      = escolha_luva

    # --- RESOLUÇÃO AUTOMÁTICA DE LUVA ---
    if escolha_luva == "Automático":
        logs.append("Fase 1: Selecionando Luva...")
        opcoes_ordenadas = sorted(
            [(k, v) for k, v in OPCOES_LUVA.items() if k != "Personalizado"],
            key=lambda x: x[1]
        )
        encontrou_auto = False

        for nome, diam in opcoes_ordenadas:
            r_cand    = diam / 2
            area_cand = np.pi * r_cand**2
            if area_total_ocupada / area_cand > LIMITE_OCUPACAO:
                continue
            if QTD_RECT == 0:
                DIAM_LUVA = diam; nome_exibicao = nome; encontrou_auto = True; break

            grade_cand = gerar_grade_ordenada(r_cand, 0.1)
            if QTD_RECT % 2 == 0:
                configs_auto = [
                    (0,"DuploX"),(0,"DuploY"),(1,"DuploX"),(1,"DuploY"),
                    (0,"DuploX_Full"),(0,"DuploY_Full"),(1,"DuploX_Full"),(1,"DuploY_Full")
                ]
            else:
                configs_auto = [
                    (0,"Centro"),(1,"Centro"),
                    (0,"DuploX"),(0,"DuploY"),(1,"DuploX"),(1,"DuploY"),
                    (0,"DuploX_Full"),(0,"DuploY_Full"),(1,"DuploX_Full"),(1,"DuploY_Full")
                ]

            rects_test, _ = posicionar_rects(grade_cand, QTD_RECT, LARG_RECT, ALT_RECT, r_cand, configs_auto)
            if len(rects_test) == QTD_RECT:
                DIAM_LUVA = diam; nome_exibicao = nome; encontrou_auto = True; break

        if not encontrou_auto:
            nome_exibicao = opcoes_ordenadas[-1][0]
            DIAM_LUVA     = opcoes_ordenadas[-1][1]
            logs.append(f"Automático: Nenhuma luva padrão atende. Usando a maior ({nome_exibicao}).")
        else:
            logs.append(f"Automático: Luva selecionada {nome_exibicao} ({DIAM_LUVA} mm)")

    r_luva     = DIAM_LUVA / 2
    area_luva  = np.pi * r_luva**2
    r_micro    = DIAM_MICRO_FIO / 2
    area_micro = np.pi * r_micro**2

    qtd_micro_fios = 0
    if area_redondo_total > 0 and area_micro > 0:
        qtd_micro_fios = int((area_redondo_total * 0.90) / area_micro)

    taxa = area_total_ocupada / area_luva if area_luva > 0 else 0

    if area_total_ocupada > area_luva:
        return {"error": "ERRO FATAL: A área dos cabos é maior que a área da luva!"}

    warning_msg = None
    if taxa > LIMITE_OCUPACAO:
        warning_msg = f"ALERTA: Taxa de ocupação acima do limite configurado ({LIMITE_OCUPACAO*100:.0f}%)"

    # --- FASE 2: RETÂNGULOS ---
    logs.append("Fase 2: Posicionando Fio Retangular...")
    grade_rect = gerar_grade_ordenada(r_luva, 0.05)

    if QTD_RECT % 2 == 0:
        configs = [
            (0,"DuploX"),(0,"DuploY"),(1,"DuploX"),(1,"DuploY"),
            (0,"DuploX_Full"),(0,"DuploY_Full"),(1,"DuploX_Full"),(1,"DuploY_Full")
        ]
    else:
        configs = [
            (0,"Centro"),(1,"Centro"),
            (0,"DuploX"),(0,"DuploY"),(1,"DuploX"),(1,"DuploY"),
            (0,"DuploX_Full"),(0,"DuploY_Full"),(1,"DuploX_Full"),(1,"DuploY_Full")
        ]

    melhor_rects, orientacao_final = posicionar_rects(
        grade_rect, QTD_RECT, LARG_RECT, ALT_RECT, r_luva, configs
    )

    # --- FASE 3: CABO CIRCULAR ---
    micro_fios = []
    if not excluir_circular:
        logs.append("Fase 3: Posicionando Cabo Circular...")
        fios_restantes = qtd_micro_fios
        grade_fios = gerar_grade_ordenada(r_luva, DIAM_MICRO_FIO * 0.2)
        for p in grade_fios:
            if fios_restantes <= 0:
                break
            cx, cy = p[0], p[1]
            if ponto_livre(cx, cy, r_micro, r_luva, melhor_rects, micro_fios):
                micro_fios.append(Circulo(cx, cy, r_micro))
                fios_restantes -= 1

    area_real_fios        = len(micro_fios) * area_micro
    area_rect_real        = len(melhor_rects) * LARG_RECT * ALT_RECT
    area_total_real       = area_rect_real + area_real_fios
    taxa_real             = area_total_real / area_luva if area_luva > 0 else 0
    elapsed_time          = time.time() - start_time

    logs.append(f"Simulação Concluída! ({elapsed_time:.1f}s)")

    return {
        "error": None,
        "warning": warning_msg,
        "area_rect_total":    area_rect_total,
        "area_redondo_total": area_redondo_total,
        "area_luva":          area_luva,
        "DIAM_LUVA":          DIAM_LUVA,
        "LARG_RECT":          LARG_RECT,
        "ALT_RECT":           ALT_RECT,
        "QTD_RECT":           QTD_RECT,
        "excluir_circular":   excluir_circular,
        "melhor_rects":       melhor_rects,
        "micro_fios":         micro_fios,
        "taxa":               taxa_real,
        "LIMITE_OCUPACAO":    LIMITE_OCUPACAO,
        "area_total_ocupada": area_total_real,
        "orientacao_final":   orientacao_final,
        "qtd_micro_fios":     qtd_micro_fios,
        "nome_exibicao":      nome_exibicao,
        "elapsed_time":       elapsed_time,
        "logs":               logs,
        "cabo_selecionado":   escolha_cabo,
        "DIAM_MICRO_FIO":     DIAM_MICRO_FIO,
    }


# ==============================================================================
# MATPLOTLIB → BASE64
# ==============================================================================
def _build_figure(res, dpi=150):
    fig, ax = plt.subplots(figsize=(5, 5))
    r_luva = res["DIAM_LUVA"] / 2

    ax.add_patch(patches.Circle((0, 0), r_luva, color='#F0F0F0', zorder=0))
    ax.add_patch(patches.Circle((0, 0), r_luva, fill=False, color='black', lw=0.75, zorder=10))

    for r in res["melhor_rects"]:
        ax.add_patch(patches.Rectangle((r.x, r.y), r.w, r.h, ec='black', fc='#4169E1', zorder=5, lw=0.5))
    for c in res["micro_fios"]:
        ax.add_patch(patches.Circle((c.cx, c.cy), c.r, color='#FF8C00', zorder=4))

    ax.axhline(0, color='red', linewidth=0.6, linestyle='--', zorder=11)
    ax.axvline(0, color='red', linewidth=0.6, linestyle='--', zorder=11)

    ax.set_xlim(-r_luva * 1.1, r_luva * 1.1)
    ax.set_ylim(-r_luva * 1.1, r_luva * 1.1)
    ax.set_aspect('equal')

    max_tick = ((int(np.ceil(res["DIAM_LUVA"])) + 4) // 5) * 5
    tick_labels    = np.arange(0, max_tick + 1, 5)
    tick_positions = tick_labels - r_luva

    ax.set_xticks(tick_positions); ax.set_xticklabels(tick_labels)
    ax.set_yticks(tick_positions); ax.set_yticklabels(tick_labels)
    ax.tick_params(axis='both', labelsize=6)
    ax.set_xlabel("Radial", fontsize=6)
    ax.set_ylabel("Axial",  fontsize=6)
    ax.grid(True, linestyle=':', linewidth=0.4, color='grey')
    ax.set_title(f"Luva {res['nome_exibicao']} - Diâmetro {res['DIAM_LUVA']} mm", fontsize=10)
    return fig


def render_figure_to_base64(res):
    fig = _build_figure(res, dpi=150)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


# ==============================================================================
# PDF
# ==============================================================================
def create_pdf(res, aprovado):
    class PDF(FPDF):
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, "Desenvolvido por: DELLAZARIG - Parte Ativa Gravataí", 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório de Simulação: Luvas x Cabos", ln=True, align="C")
    pdf.set_font("Arial", "I", 10)
    fuso_br = datetime.timezone(datetime.timedelta(hours=-3))
    pdf.cell(0, 10, f"Gerado em: {datetime.datetime.now(fuso_br).strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
    pdf.ln(5)

    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Dados de Entrada", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font("Arial", "", 10)

    pdf.cell(95, 6, f"Luva: {res['nome_exibicao']} (Diam: {res['DIAM_LUVA']} mm)", border=0)
    pdf.cell(95, 6, f"Cabo: {res['cabo_selecionado']}", border=0, ln=True)
    pdf.cell(95, 6, f"Fio Retangular: {res['LARG_RECT']} x {res['ALT_RECT']} mm", border=0)
    gran_txt = f"{res['DIAM_MICRO_FIO']} mm" if not res['excluir_circular'] else "N/A"
    pdf.cell(95, 6, f"Granularidade: {gran_txt}", border=0, ln=True)
    pdf.cell(95, 6, f"Fios Retangulares: {res['QTD_RECT']}", border=0)
    pdf.cell(95, 6, f"Limite Ocupação: {res['LIMITE_OCUPACAO']*100:.1f}%", border=0, ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Resultados Calculados", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font("Arial", "", 10)

    pdf.cell(63, 7, f"Ocupação Real: {res['taxa']*100:.1f}%", border=0)
    pdf.cell(63, 7, f"Área Ocupada: {res['area_total_ocupada']:.2f} mm2", border=0)
    pdf.cell(64, 7, f"Área Luva: {res['area_luva']:.2f} mm2", border=0, ln=True)

    pdf.cell(95, 7, f"Fios Retangulares: {len(res['melhor_rects'])} / {res['QTD_RECT']}", border=0)
    qtd_circ = f"{len(res['micro_fios'])} / {res['qtd_micro_fios']}" if not res['excluir_circular'] else "-"
    pdf.cell(95, 7, f"Micro-fios Circulares: {qtd_circ}", border=0, ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 16)
    if aprovado:
        pdf.set_text_color(0, 128, 0)
        pdf.cell(0, 10, "RESULTADO: APROVADO", ln=True, align="C")
    else:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, "RESULTADO: REPROVADO", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)

    fig = _build_figure(res, dpi=300)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        fig.savefig(tmp.name, format='png', dpi=300, bbox_inches='tight')
        tmp_path = tmp.name
    plt.close(fig)

    pdf.image(tmp_path, x=55, w=100)
    os.remove(tmp_path)

    return pdf.output(dest='S').encode('latin-1')


# ==============================================================================
# AUTH HELPERS
# ==============================================================================
def check_saved_auth():
    try:
        if os.path.exists(AUTH_FILE):
            with open(AUTH_FILE) as f:
                data = json.load(f)
            expires = datetime.datetime.fromisoformat(data["expires"])
            if datetime.datetime.now() < expires:
                return True
    except Exception:
        pass
    return False


def save_auth():
    expires = datetime.datetime.now() + datetime.timedelta(days=1)
    with open(AUTH_FILE, "w") as f:
        json.dump({"expires": expires.isoformat()}, f)


def clear_auth():
    if os.path.exists(AUTH_FILE):
        os.remove(AUTH_FILE)


# ==============================================================================
# FLET APP
# ==============================================================================
def main(page: ft.Page):
    page.title      = "Luvas x Cabos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width      = 1150
    page.window_height     = 780
    page.window_min_width  = 900
    page.window_min_height = 600
    page.padding    = 0
    page.bgcolor    = ft.Colors.WHITE

    simulation_results: dict = {"data": None}

    # File picker for PDF save — page.update() é obrigatório após append no Flet 0.80+
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.update()

    # ------------------------------------------------------------------ helpers
    def section_title(text):
        return ft.Text(text, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800)

    def metric_card(label, value, subtitle=None, width=None):
        rows = [
            ft.Text(label, size=10, color=ft.Colors.GREY_600),
            ft.Text(value, size=16, weight=ft.FontWeight.BOLD),
        ]
        if subtitle:
            rows.append(ft.Text(subtitle, size=9, color=ft.Colors.GREY_500))
        return ft.Container(
            content=ft.Column(rows, spacing=2, tight=True),
            padding=ft.padding.symmetric(horizontal=10, vertical=8),
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            expand=True if width is None else False,
            width=width,
            bgcolor=ft.Colors.GREY_50,
        )

    # ========================================================================
    # LOGIN VIEW
    # ========================================================================
    def build_login_view():
        tf_user  = ft.TextField(label="Usuário", width=300, autofocus=True)
        tf_senha = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
        txt_erro = ft.Text("", color=ft.Colors.RED_700, size=13)

        def do_login(e):
            if tf_user.value.strip().lower() == "weguser" and tf_senha.value == "ParteAtivaGCV":
                save_auth()
                show_main_view()
            else:
                txt_erro.value = "Usuário ou senha incorretos"
                page.update()

        tf_senha.on_submit = do_login

        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        logo_ctrl = (
            ft.Image(src=logo_path, width=130)
            if os.path.exists(logo_path)
            else ft.Text("Luvas x Cabos", size=26, weight=ft.FontWeight.BOLD)
        )

        return ft.Container(
            content=ft.Column(
                [
                    logo_ctrl,
                    ft.Text("Login", size=22, weight=ft.FontWeight.BOLD),
                    tf_user,
                    tf_senha,
                    ft.OutlinedButton("Entrar", on_click=do_login, width=300),
                    txt_erro,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
            ),
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )

    # ========================================================================
    # MAIN VIEW
    # ========================================================================
    def build_main_view():

        # ---- Luva ----
        lista_luvas = (
            ["Automático"]
            + [k for k in OPCOES_LUVA if k != "Personalizado"]
            + ["Personalizado"]
        )
        dd_luva       = ft.Dropdown(
            label="Seção Nominal da Luva",
            options=[ft.dropdown.Option(o) for o in lista_luvas],
            value="Automático",
            dense=True,
        )
        tf_diam_luva  = ft.TextField(label="Diâmetro da Luva (mm)", value="17.0", dense=True, visible=False)
        txt_diam_luva = ft.Text("", size=11, color=ft.Colors.GREY_600, visible=False)

        # ---- Fio Retangular ----
        tf_alt_rect  = ft.TextField(label="Axial (mm)",   value="1.5", dense=True)
        tf_larg_rect = ft.TextField(label="Radial (mm)",  value="7.0", dense=True)
        tf_qtd_rect  = ft.TextField(label="Quantidade",   value="10",  dense=True)

        # ---- Cabo Circular ----
        cb_excluir = ft.Checkbox(label="Excluir Cabo Circular da Simulação", value=False)
        dd_cabo    = ft.Dropdown(
            label="Seção Nominal do Cabo",
            options=[ft.dropdown.Option(o) for o in OPCOES_CABO_CIRCULAR],
            value="50 mm²",
            dense=True,
        )
        tf_diam_cabo  = ft.TextField(label="Diâmetro Equivalente (mm)", value="10.0", dense=True, visible=False)
        txt_diam_cabo = ft.Text(f"Diâmetro: {OPCOES_CABO_CIRCULAR['50 mm²']} mm", size=11, color=ft.Colors.GREY_600)

        # ---- Micro-fio ----
        lbl_micro = ft.Text("Diâm. Micro-Fio (mm): 0.80", size=11)
        sl_micro  = ft.Slider(min=0.4, max=2.0, value=0.8, divisions=16, expand=True)
        tf_micro  = ft.TextField(value="0.80", width=65, dense=True, text_align=ft.TextAlign.CENTER)

        # ---- Ocupação ----
        lbl_ocupacao = ft.Text("Limite de Ocupação (%): 85.0", size=11)
        sl_ocupacao  = ft.Slider(min=0, max=100, value=85, divisions=100, expand=True)
        tf_ocupacao  = ft.TextField(value="85.0", width=65, dense=True, text_align=ft.TextAlign.CENTER)

        # ---- Results area ----
        progress_bar  = ft.ProgressBar(value=0, visible=False)
        status_text   = ft.Text("", size=12, color=ft.Colors.GREY_600)
        results_col   = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        # Container that hides when "excluir" is checked
        panel_circular = ft.Column([], visible=True, spacing=6)

        title_text = ft.Text(
            "Simulação: Fio Retangular + Cabo Circular",
            size=17, weight=ft.FontWeight.BOLD,
        )

        # ---- Event handlers ----
        def on_luva_change(e):
            v = dd_luva.value
            tf_diam_luva.visible  = (v == "Personalizado")
            txt_diam_luva.visible = (v not in ("Automático", "Personalizado"))
            if txt_diam_luva.visible:
                txt_diam_luva.value = f"Diâmetro: {OPCOES_LUVA[v]} mm"
            page.update()

        def on_cabo_change(e):
            v = dd_cabo.value
            tf_diam_cabo.visible  = (v == "Personalizado")
            txt_diam_cabo.visible = (v != "Personalizado")
            if txt_diam_cabo.visible:
                txt_diam_cabo.value = f"Diâmetro: {OPCOES_CABO_CIRCULAR.get(v, 0)} mm"
            page.update()

        def on_excluir_change(e):
            panel_circular.visible = not cb_excluir.value
            title_text.value = (
                "Simulação: Fio Retangular"
                if cb_excluir.value
                else "Simulação: Fio Retangular + Cabo Circular"
            )
            page.update()

        def on_micro_slider(e):
            v = round(sl_micro.value, 2)
            tf_micro.value  = f"{v:.2f}"
            lbl_micro.value = f"Diâm. Micro-Fio (mm): {v:.2f}"
            page.update()

        def on_micro_field(e):
            try:
                v = max(0.4, min(2.0, float(tf_micro.value)))
                sl_micro.value  = v
                lbl_micro.value = f"Diâm. Micro-Fio (mm): {v:.2f}"
                page.update()
            except ValueError:
                pass

        def on_ocup_slider(e):
            v = round(sl_ocupacao.value, 1)
            tf_ocupacao.value  = f"{v:.1f}"
            lbl_ocupacao.value = f"Limite de Ocupação (%): {v:.1f}"
            page.update()

        def on_ocup_field(e):
            try:
                v = max(0.0, min(100.0, float(tf_ocupacao.value)))
                sl_ocupacao.value  = v
                lbl_ocupacao.value = f"Limite de Ocupação (%): {v:.1f}"
                page.update()
            except ValueError:
                pass

        dd_luva.on_change    = on_luva_change
        dd_cabo.on_change    = on_cabo_change
        cb_excluir.on_change = on_excluir_change
        sl_micro.on_change   = on_micro_slider
        tf_micro.on_submit   = on_micro_field
        tf_micro.on_blur     = on_micro_field
        sl_ocupacao.on_change = on_ocup_slider
        tf_ocupacao.on_submit = on_ocup_field
        tf_ocupacao.on_blur   = on_ocup_field

        # ---- PDF save ----
        def on_save_pdf(e: ft.FilePickerResultEvent):
            if not e.path:
                return
            res = simulation_results["data"]
            if not res:
                return
            falha_r = len(res["melhor_rects"]) < res["QTD_RECT"]
            falha_o = res["taxa"] > res["LIMITE_OCUPACAO"]
            falha_c = (
                not res["excluir_circular"]
                and res["qtd_micro_fios"] > 0
                and len(res["micro_fios"]) < res["qtd_micro_fios"]
            )
            aprovado = not (falha_r or falha_o or falha_c)
            try:
                pdf_bytes = create_pdf(res, aprovado)
                save_path = e.path if e.path.lower().endswith(".pdf") else e.path + ".pdf"
                with open(save_path, "wb") as f:
                    f.write(pdf_bytes)
                page.snack_bar = ft.SnackBar(ft.Text(f"PDF salvo: {save_path}"), open=True)
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao salvar PDF: {ex}"), open=True)
            page.update()

        file_picker.on_result = on_save_pdf

        # ---- Render results ----
        def render_results(res):
            results_col.controls.clear()

            falha_r = len(res["melhor_rects"]) < res["QTD_RECT"]
            falha_o = res["taxa"] > res["LIMITE_OCUPACAO"]
            falha_c = (
                not res["excluir_circular"]
                and res["qtd_micro_fios"] > 0
                and len(res["micro_fios"]) < res["qtd_micro_fios"]
            )
            aprovado = not (falha_r or falha_o or falha_c)

            # --- Dados das Seções ---
            results_col.controls.append(section_title("Dados das Seções"))
            if not res["excluir_circular"]:
                results_col.controls.append(ft.Row([
                    metric_card("Fio Retangular", f"{res['area_rect_total']:.2f} mm²",
                                f"{res['LARG_RECT']}×{res['ALT_RECT']} mm | Qtd: {res['QTD_RECT']}"),
                    metric_card("Cabo Circular",  f"{res['area_redondo_total']:.2f} mm²"),
                    metric_card("Luva",           f"{res['area_luva']:.2f} mm²",
                                f"Ø {res['DIAM_LUVA']} mm"),
                ], spacing=8))
            else:
                results_col.controls.append(ft.Row([
                    metric_card("Fio Retangular", f"{res['area_rect_total']:.2f} mm²",
                                f"{res['LARG_RECT']}×{res['ALT_RECT']} mm | Qtd: {res['QTD_RECT']}"),
                    metric_card("Luva",           f"{res['area_luva']:.2f} mm²",
                                f"Ø {res['DIAM_LUVA']} mm"),
                ], spacing=8))

            results_col.controls.append(ft.Divider(height=6))

            # --- Indicadores ---
            results_col.controls.append(section_title("Indicadores"))
            delta_rect = len(res["melhor_rects"]) - res["QTD_RECT"]
            delta_taxa = (res["taxa"] - res["LIMITE_OCUPACAO"]) * 100
            sub_fios   = f"▼ {abs(int(delta_rect))} fios" if delta_rect < 0 else "OK"
            sub_taxa   = f"{'▲' if delta_taxa > 0 else '▼'} {abs(delta_taxa):.1f}% do limite"

            results_col.controls.append(ft.Row([
                metric_card("Fios Retangulares", f"{len(res['melhor_rects'])} / {res['QTD_RECT']}", sub_fios),
                metric_card("Ocupação Real",     f"{res['taxa']*100:.1f}%", sub_taxa),
                metric_card("Área Total",        f"{res['area_total_ocupada']:.2f} mm²"),
            ], spacing=8))

            results_col.controls.append(ft.Divider(height=6))

            # --- Visualização ---
            try:
                img_b64 = render_figure_to_base64(res)
                results_col.controls.append(
                    ft.Row([
                        ft.Image(src_base64=img_b64, width=390, height=390, fit=ft.ImageFit.CONTAIN)
                    ], alignment=ft.MainAxisAlignment.CENTER)
                )
            except Exception as ex:
                results_col.controls.append(ft.Text(f"Erro ao gerar imagem: {ex}", color=ft.Colors.RED))

            results_col.controls.append(ft.Divider(height=6))

            # --- Status ---
            if aprovado:
                msg = f"Simulação Aprovada!  Orientação: {res['orientacao_final']}  |  Retangular: {len(res['melhor_rects'])}/{res['QTD_RECT']}"
                if not res["excluir_circular"]:
                    pct = (len(res["micro_fios"]) / res["qtd_micro_fios"] * 100) if res["qtd_micro_fios"] > 0 else 0
                    msg += f"  |  Circular: {pct:.0f}%"
                msg += f"  |  Tempo: {res['elapsed_time']:.2f}s"
                cor = ft.Colors.GREEN_700
            else:
                motivos = []
                if falha_r:
                    motivos.append(f"Fios: {len(res['melhor_rects'])}/{res['QTD_RECT']}")
                if falha_c:
                    pct = len(res["micro_fios"]) / res["qtd_micro_fios"] * 100
                    motivos.append(f"Circular: {len(res['micro_fios'])}/{res['qtd_micro_fios']} ({pct:.0f}%)")
                if falha_o:
                    motivos.append(f"Ocupação: {res['taxa']*100:.1f}% (Limite: {res['LIMITE_OCUPACAO']*100:.0f}%)")
                msg = f"Simulação Reprovada!  Motivo(s): {', '.join(motivos)}  |  Tempo: {res['elapsed_time']:.2f}s"
                cor = ft.Colors.RED_700

            results_col.controls.append(
                ft.Container(
                    content=ft.Text(msg, color=ft.Colors.WHITE, size=12),
                    bgcolor=cor, padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    border_radius=6,
                )
            )

            # --- Logs ---
            results_col.controls.append(section_title("Logs da Simulação"))
            results_col.controls.append(
                ft.Text("\n".join(res["logs"]), size=11, font_family="Courier New",
                        color=ft.Colors.GREY_700)
            )

            # --- Botão PDF ---
            fuso_br      = datetime.timezone(datetime.timedelta(hours=-3))
            default_name = f"Relatorio_{datetime.datetime.now(fuso_br).strftime('%Y%m%d_%H%M')}.pdf"
            results_col.controls.append(
                ft.FilledButton(
                    "Baixar Relatório (PDF)",
                    icon=ft.Icons.PICTURE_AS_PDF,
                    on_click=lambda e: file_picker.save_file(
                        dialog_title="Salvar Relatório PDF",
                        file_name=default_name,
                        allowed_extensions=["pdf"],
                    ),
                )
            )

        # ---- Execute button ----
        btn_executar = ft.FilledButton(
            "Executar Simulação",
            icon=ft.Icons.PLAY_ARROW,
            expand=True,
        )

        def on_executar(e):
            try:
                escolha_luva = dd_luva.value
                if escolha_luva == "Personalizado":
                    DIAM_LUVA = float(tf_diam_luva.value)
                elif escolha_luva == "Automático":
                    DIAM_LUVA = 0.0
                else:
                    DIAM_LUVA = OPCOES_LUVA[escolha_luva]

                ALT_RECT         = float(tf_alt_rect.value)
                LARG_RECT        = float(tf_larg_rect.value)
                QTD_RECT         = int(tf_qtd_rect.value)
                excluir_circular = cb_excluir.value

                if excluir_circular:
                    DIAM_REDONDO_TOTAL = 0.0
                    escolha_cabo       = "N/A"
                else:
                    v_cabo = dd_cabo.value
                    DIAM_REDONDO_TOTAL = (
                        float(tf_diam_cabo.value)
                        if v_cabo == "Personalizado"
                        else OPCOES_CABO_CIRCULAR[v_cabo]
                    )
                    escolha_cabo = v_cabo

                DIAM_MICRO_FIO  = sl_micro.value
                LIMITE_OCUPACAO = sl_ocupacao.value / 100.0

            except ValueError as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro nos parâmetros: {ex}"), open=True)
                page.update()
                return

            btn_executar.disabled = True
            progress_bar.visible  = True
            progress_bar.value    = None          # indeterminate
            status_text.value     = "Executando simulação..."
            results_col.controls.clear()
            page.update()

            params = dict(
                escolha_luva=escolha_luva, DIAM_LUVA=DIAM_LUVA,
                ALT_RECT=ALT_RECT, LARG_RECT=LARG_RECT, QTD_RECT=QTD_RECT,
                excluir_circular=excluir_circular, DIAM_REDONDO_TOTAL=DIAM_REDONDO_TOTAL,
                DIAM_MICRO_FIO=DIAM_MICRO_FIO, LIMITE_OCUPACAO=LIMITE_OCUPACAO,
                escolha_cabo=escolha_cabo,
            )

            def run():
                res = run_simulation(params)
                simulation_results["data"] = res

                if res.get("error"):
                    page.snack_bar = ft.SnackBar(ft.Text(res["error"]), open=True)
                else:
                    if res.get("warning"):
                        page.snack_bar = ft.SnackBar(ft.Text(res["warning"]), open=True)
                    render_results(res)

                progress_bar.visible  = False
                progress_bar.value    = 0
                status_text.value     = ""
                btn_executar.disabled = False
                page.update()

            threading.Thread(target=run, daemon=True).start()

        btn_executar.on_click = on_executar

        def on_logout(e):
            clear_auth()
            show_login_view()

        # ---- Assemble panel_circular ----
        panel_circular.controls = [
            section_title("Cabo Circular"),
            dd_cabo,
            tf_diam_cabo,
            txt_diam_cabo,
            ft.Divider(height=4),
            lbl_micro,
            ft.Row([sl_micro, tf_micro], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ]

        # ---- Sidebar ----
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        logo_ctrl = (
            ft.Image(src=logo_path, width=100, fit=ft.ImageFit.CONTAIN)
            if os.path.exists(logo_path)
            else ft.Text("Luvas x Cabos", weight=ft.FontWeight.BOLD, size=14)
        )

        sidebar = ft.Container(
            content=ft.Column(
                [
                    ft.Row([logo_ctrl], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(),
                    section_title("Parâmetros da Luva"),
                    dd_luva,
                    tf_diam_luva,
                    txt_diam_luva,
                    ft.Divider(height=6),
                    section_title("Fio Retangular"),
                    tf_alt_rect,
                    tf_larg_rect,
                    tf_qtd_rect,
                    ft.Divider(height=6),
                    cb_excluir,
                    panel_circular,
                    ft.Divider(height=6),
                    section_title("Configurações"),
                    lbl_ocupacao,
                    ft.Row([sl_ocupacao, tf_ocupacao], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Divider(height=6),
                    btn_executar,
                    ft.Divider(height=6),
                    ft.OutlinedButton(
                        "Sair (Logout)",
                        icon=ft.Icons.LOGOUT,
                        on_click=on_logout,
                        style=ft.ButtonStyle(color=ft.Colors.RED_700),
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=6,
            ),
            width=285,
            padding=ft.padding.all(12),
            bgcolor=ft.Colors.GREY_50,
            border=ft.border.only(right=ft.BorderSide(1, ft.Colors.GREY_200)),
        )

        # ---- Main content ----
        main_content = ft.Container(
            content=ft.Column(
                [
                    title_text,
                    ft.Text(
                        "Simula a montagem prática de luvas, verificando fisicamente se os condutores cabem.",
                        size=12, color=ft.Colors.GREY_600,
                    ),
                    progress_bar,
                    status_text,
                    results_col,
                    ft.Divider(),
                    ft.Text(
                        "Desenvolvido por: DELLAZARIG - Parte Ativa Gravataí",
                        size=11, color=ft.Colors.GREY_400,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
                expand=True,
            ),
            padding=ft.padding.all(18),
            expand=True,
        )

        return ft.Row([sidebar, main_content], expand=True, spacing=0)

    # ========================================================================
    # VIEW MANAGEMENT
    # ========================================================================
    def show_login_view():
        page.controls.clear()
        page.add(build_login_view())
        page.update()

    def show_main_view():
        page.controls.clear()
        page.add(build_main_view())
        page.update()

    if check_saved_auth():
        show_main_view()
    else:
        show_login_view()


ft.app(target=main, assets_dir=ASSETS_DIR)
