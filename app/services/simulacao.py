import time
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from dataclasses import dataclass
from typing import List, Optional, Callable

# ==============================================================================
# CONSTANTES
# ==============================================================================
OPCOES_LUVA = {
    "25 mm²": 8.0, "35 mm²": 9.0, "50 mm²": 11.0, "70 mm²": 13.0,
    "95 mm²": 15.0, "120 mm²": 17.0, "150 mm²": 19.0, "185 mm²": 21.0,
    "240 mm²": 24.0, "300 mm²": 24.5, "400 mm²": 30.0, "500 mm²": 33.0,
    "630 mm²": 39.0
}

OPCOES_CABO_CIRCULAR = {
    "50 mm²": 9.15, "70 mm²": 10.83, "120 mm²": 14.77,
    "185 mm²": 18.09, "240 mm²": 23.3, "300 mm²": 23.5,
    "400 mm²": 29.1, "500 mm²": 33.5
}

_ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'assets'
)

# ==============================================================================
# CLASSES DE DADOS
# ==============================================================================
@dataclass
class Retangulo:
    x: float; y: float; w: float; h: float

@dataclass
class Circulo:
    cx: float; cy: float; r: float

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================
def gerar_grade_ordenada(raio: float, passo: float) -> np.ndarray:
    eixo = np.arange(-raio, raio, passo)
    xx, yy = np.meshgrid(eixo, eixo)
    dist = xx**2 + yy**2
    mask = dist <= raio**2
    pontos = np.column_stack((xx[mask], yy[mask]))
    indices = np.argsort(pontos[:, 0]**2 + pontos[:, 1]**2)
    return pontos[indices]


def validar_rect(x: float, y: float, w: float, h: float,
                 r_luva: float, rects: List[Retangulo]) -> bool:
    r2 = r_luva**2
    if (x**2 + y**2 > r2) or ((x + w)**2 + y**2 > r2) or \
       (x**2 + (y + h)**2 > r2) or ((x + w)**2 + (y + h)**2 > r2):
        return False
    for r in rects:
        if x < r.x + r.w and x + w > r.x and y < r.y + r.h and y + h > r.y:
            return False
    return True


def ponto_livre(cx: float, cy: float, r_micro: float, r_luva: float,
                rects: List[Retangulo], micro_circs: List[Circulo]) -> bool:
    if np.sqrt(cx**2 + cy**2) + r_micro > r_luva:
        return False
    for r in rects:
        closest_x = max(r.x, min(cx, r.x + r.w))
        closest_y = max(r.y, min(cy, r.y + r.h))
        if (cx - closest_x)**2 + (cy - closest_y)**2 < r_micro**2:
            return False
    for c in micro_circs:
        if (cx - c.cx)**2 + (cy - c.cy)**2 < (2 * r_micro)**2:
            return False
    return True


def _posicionar_retangulos(grade: np.ndarray, QTD_RECT: int, r_luva: float,
                           LARG_RECT: float, ALT_RECT: float) -> tuple:
    """Executa todas as estratégias e retorna (melhor_lista, orientacao_str)."""
    melhor_rects = []
    melhor_score = -1
    orientacao_final = ""

    configs = []
    if QTD_RECT % 2 == 0:
        configs = [
            (0, "DuploX"), (0, "DuploY"), (1, "DuploX"), (1, "DuploY"),
            (0, "DuploX_Full"), (0, "DuploY_Full"), (1, "DuploX_Full"), (1, "DuploY_Full")
        ]
    else:
        configs = [
            (0, "Centro"), (1, "Centro"),
            (0, "DuploX"), (0, "DuploY"), (1, "DuploX"), (1, "DuploY"),
            (0, "DuploX_Full"), (0, "DuploY_Full"), (1, "DuploX_Full"), (1, "DuploY_Full")
        ]

    for sentido, estrategia in configs:
        w = LARG_RECT if sentido == 0 else ALT_RECT
        h = ALT_RECT if sentido == 0 else LARG_RECT

        rects_temp = _aplicar_estrategia(grade, estrategia, w, h, r_luva, QTD_RECT)

        if len(rects_temp) > melhor_score:
            melhor_score = len(rects_temp)
            melhor_rects = rects_temp
            orientacao_final = "Horizontal" if sentido == 0 else "Vertical"
            if "Duplo" in estrategia:
                orientacao_final += " (Simétrico)"

    return melhor_rects, orientacao_final


def _aplicar_estrategia(grade: np.ndarray, estrategia: str,
                        w: float, h: float, r_luva: float,
                        QTD_RECT: int) -> List[Retangulo]:
    rects_temp = []

    if estrategia == "Centro":
        for _ in range(QTD_RECT):
            for p in grade:
                tx, ty = p[0] - w / 2, p[1] - h / 2
                if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                    rects_temp.append(Retangulo(tx, ty, w, h))
                    break

    elif estrategia == "DuploX":
        mask_L = grade[:, 0] <= -w / 2 + 1e-5
        mask_R = grade[:, 0] >= w / 2 - 1e-5
        d_L = (grade[mask_L][:, 0] + w / 2)**2 + grade[mask_L][:, 1]**2
        d_R = (grade[mask_R][:, 0] - w / 2)**2 + grade[mask_R][:, 1]**2
        g_L = grade[mask_L][np.argsort(d_L)]
        g_R = grade[mask_R][np.argsort(d_R)]
        idx_L, idx_R = 0, 0
        for i in range(QTD_RECT):
            placed = False
            if i % 2 == 0:
                while idx_L < len(g_L):
                    p = g_L[idx_L]; idx_L += 1
                    tx, ty = p[0] - w / 2, p[1] - h / 2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h))
                        placed = True; break
            else:
                while idx_R < len(g_R):
                    p = g_R[idx_R]; idx_R += 1
                    tx, ty = p[0] - w / 2, p[1] - h / 2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h))
                        placed = True; break
            if not placed:
                break

    elif estrategia == "DuploX_Full":
        d2 = np.minimum(
            (grade[:, 0] + w / 2)**2 + grade[:, 1]**2,
            (grade[:, 0] - w / 2)**2 + grade[:, 1]**2
        )
        grade_sorted = grade[np.argsort(d2)]
        for _ in range(QTD_RECT):
            for p in grade_sorted:
                tx, ty = p[0] - w / 2, p[1] - h / 2
                if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                    rects_temp.append(Retangulo(tx, ty, w, h))
                    break

    elif estrategia == "DuploY":
        mask_T = grade[:, 1] >= h / 2 - 1e-5
        mask_B = grade[:, 1] <= -h / 2 + 1e-5
        d_T = grade[mask_T][:, 0]**2 + (grade[mask_T][:, 1] - h / 2)**2
        d_B = grade[mask_B][:, 0]**2 + (grade[mask_B][:, 1] + h / 2)**2
        g_T = grade[mask_T][np.argsort(d_T)]
        g_B = grade[mask_B][np.argsort(d_B)]
        idx_T, idx_B = 0, 0
        for i in range(QTD_RECT):
            placed = False
            if i % 2 == 0:
                while idx_T < len(g_T):
                    p = g_T[idx_T]; idx_T += 1
                    tx, ty = p[0] - w / 2, p[1] - h / 2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h))
                        placed = True; break
            else:
                while idx_B < len(g_B):
                    p = g_B[idx_B]; idx_B += 1
                    tx, ty = p[0] - w / 2, p[1] - h / 2
                    if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                        rects_temp.append(Retangulo(tx, ty, w, h))
                        placed = True; break
            if not placed:
                break

    elif estrategia == "DuploY_Full":
        d2 = np.minimum(
            grade[:, 0]**2 + (grade[:, 1] - h / 2)**2,
            grade[:, 0]**2 + (grade[:, 1] + h / 2)**2
        )
        grade_sorted = grade[np.argsort(d2)]
        for _ in range(QTD_RECT):
            for p in grade_sorted:
                tx, ty = p[0] - w / 2, p[1] - h / 2
                if validar_rect(tx, ty, w, h, r_luva, rects_temp):
                    rects_temp.append(Retangulo(tx, ty, w, h))
                    break

    return rects_temp

# ==============================================================================
# FUNÇÃO PRINCIPAL DE SIMULAÇÃO
# ==============================================================================
def executar_simulacao(
    escolha_luva: str,
    DIAM_LUVA: float,
    LARG_RECT: float,
    ALT_RECT: float,
    QTD_RECT: int,
    excluir_circular: bool,
    DIAM_REDONDO_TOTAL: float,
    DIAM_MICRO_FIO: float,
    LIMITE_OCUPACAO: float,
    escolha_cabo: str = "N/A",
    on_log: Optional[Callable[[int, str], None]] = None,
    on_progress: Optional[Callable[[int], None]] = None,
) -> dict:
    """
    Executa a simulação de posicionamento de cabos dentro de uma luva.

    Callbacks:
        on_log(fase_idx, texto): fase 0=limpando, 1=luva, 2=retangular, 3=circular, 4=conclusão
        on_progress(valor_0_a_100): atualiza barra de progresso

    Retorna dict com resultados ou {"erro": "mensagem"} em caso de falha fatal.
    """

    def _log(fase_idx: int, texto: str):
        if on_log:
            on_log(fase_idx, texto)

    def _progress(valor: int):
        if on_progress:
            on_progress(valor)

    start_time = time.time()

    _log(0, "Limpando simulação anterior e iniciando...")

    # --- Cálculos iniciais ---
    area_rect_total = QTD_RECT * LARG_RECT * ALT_RECT
    r_redondo_total = DIAM_REDONDO_TOTAL / 2
    area_redondo_total = np.pi * r_redondo_total**2
    area_total_ocupada = area_rect_total + area_redondo_total

    nome_exibicao = escolha_luva

    # --- Fase 1: Resolução automática de luva ---
    if escolha_luva == "Automático":
        _log(1, "Fase 1: Selecionando Luva...")
        t_phase = time.time()

        opcoes_ordenadas = sorted(OPCOES_LUVA.items(), key=lambda x: x[1])
        encontrou_auto = False

        for nome, diam in opcoes_ordenadas:
            r_cand = diam / 2
            area_cand = np.pi * r_cand**2

            if area_total_ocupada / area_cand > LIMITE_OCUPACAO:
                continue

            if QTD_RECT == 0:
                DIAM_LUVA = diam
                nome_exibicao = nome
                encontrou_auto = True
                break

            grade_cand = gerar_grade_ordenada(r_cand, 0.1)

            configs_auto = []
            if QTD_RECT % 2 == 0:
                configs_auto = [
                    (0, "DuploX"), (0, "DuploY"), (1, "DuploX"), (1, "DuploY"),
                    (0, "DuploX_Full"), (0, "DuploY_Full"), (1, "DuploX_Full"), (1, "DuploY_Full")
                ]
            else:
                configs_auto = [
                    (0, "Centro"), (1, "Centro"),
                    (0, "DuploX"), (0, "DuploY"), (1, "DuploX"), (1, "DuploY"),
                    (0, "DuploX_Full"), (0, "DuploY_Full"), (1, "DuploX_Full"), (1, "DuploY_Full")
                ]

            encaixou_cand = False
            for sentido, estrategia in configs_auto:
                w = LARG_RECT if sentido == 0 else ALT_RECT
                h = ALT_RECT if sentido == 0 else LARG_RECT
                rects_temp = _aplicar_estrategia(grade_cand, estrategia, w, h, r_cand, QTD_RECT)
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

        _log(1, f"Fase 1: Selecionando Luva... ({time.time() - t_phase:.2f}s)")
    else:
        _log(1, "Fase 1: Selecionando Luva... (0.00s)")

    _progress(33)

    r_luva = DIAM_LUVA / 2
    area_luva = np.pi * r_luva**2
    r_micro = DIAM_MICRO_FIO / 2
    area_micro = np.pi * r_micro**2

    qtd_micro_fios = 0
    if area_redondo_total > 0 and area_micro > 0:
        qtd_micro_fios = int((area_redondo_total * 0.90) / area_micro)

    if area_total_ocupada > area_luva:
        return {"erro": f"ERRO FATAL: A área dos cabos ({area_total_ocupada:.2f} mm²) é maior que a área da luva ({area_luva:.2f} mm²)!"}

    # --- Fase 2: Posicionamento dos retângulos ---
    _log(2, "Fase 2: Posicionando Fio Retangular...")
    t_phase = time.time()

    grade_rect = gerar_grade_ordenada(r_luva, 0.05)
    melhor_rects, orientacao_final = _posicionar_retangulos(
        grade_rect, QTD_RECT, r_luva, LARG_RECT, ALT_RECT
    )

    _log(2, f"Fase 2: Posicionando Fio Retangular... ({time.time() - t_phase:.2f}s)")
    _progress(66)

    # --- Fase 3: Cabo circular ---
    micro_fios = []
    if not excluir_circular:
        _log(3, "Fase 3: Posicionando Cabo Circular...")
        t_phase = time.time()

        grade_fios = gerar_grade_ordenada(r_luva, DIAM_MICRO_FIO * 0.2)
        fios_restantes = qtd_micro_fios

        for p in grade_fios:
            if fios_restantes <= 0:
                break
            cx, cy = p[0], p[1]
            if ponto_livre(cx, cy, r_micro, r_luva, melhor_rects, micro_fios):
                micro_fios.append(Circulo(cx, cy, r_micro))
                fios_restantes -= 1

        _log(3, f"Fase 3: Posicionando Cabo Circular... ({time.time() - t_phase:.2f}s)")
    else:
        _log(3, "Fase 3: Cabo Circular excluído.")

    _progress(100)

    elapsed_time = time.time() - start_time
    _log(4, f"Simulação Concluída! (Total: {elapsed_time:.2f}s)")

    # --- Cálculo real pós-simulação ---
    area_rect_real = len(melhor_rects) * LARG_RECT * ALT_RECT
    area_real_fios = len(micro_fios) * area_micro
    area_total_ocupada_real = area_rect_real + area_real_fios
    taxa_real = area_total_ocupada_real / area_luva if area_luva > 0 else 0

    return {
        "area_rect_total": area_rect_total,
        "area_redondo_total": area_redondo_total,
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
        "cabo_selecionado": escolha_cabo if not excluir_circular else "N/A",
        "DIAM_MICRO_FIO": DIAM_MICRO_FIO,
    }

# ==============================================================================
# GERAÇÃO E SALVAMENTO DA IMAGEM
# ==============================================================================
def salvar_imagem(res: dict, nome_arquivo: str = "simulacao.png") -> str:
    """
    Gera o gráfico matplotlib e salva em assets/<nome_arquivo>.
    Retorna o caminho absoluto do arquivo salvo.
    """
    os.makedirs(_ASSETS_DIR, exist_ok=True)
    caminho = os.path.join(_ASSETS_DIR, nome_arquivo)

    r_luva = res["DIAM_LUVA"] / 2

    fig, ax = plt.subplots(figsize=(5, 5))

    ax.add_patch(patches.Circle((0, 0), r_luva, color='#F0F0F0', zorder=0))
    ax.add_patch(patches.Circle((0, 0), r_luva, fill=False, color='black', lw=0.75, zorder=10))

    for r in res["melhor_rects"]:
        ax.add_patch(patches.Rectangle((r.x, r.y), r.w, r.h,
                                       ec='black', fc='#4169E1', zorder=5, lw=0.5))

    for c in res["micro_fios"]:
        ax.add_patch(patches.Circle((c.cx, c.cy), c.r, color='#FF8C00', zorder=4))

    ax.axhline(0, color='red', linewidth=0.6, linestyle='--', zorder=11)
    ax.axvline(0, color='red', linewidth=0.6, linestyle='--', zorder=11)

    ax.set_xlim(-r_luva * 1.1, r_luva * 1.1)
    ax.set_ylim(-r_luva * 1.1, r_luva * 1.1)
    ax.set_aspect('equal')

    max_tick = int(np.ceil(res["DIAM_LUVA"]))
    max_tick = ((max_tick + 4) // 5) * 5
    tick_labels = np.arange(0, max_tick + 1, 5)
    tick_positions = tick_labels - r_luva

    ax.set_xticks(tick_positions)
    ax.set_yticks(tick_positions)
    ax.set_xticklabels(tick_labels)
    ax.set_yticklabels(tick_labels)
    ax.tick_params(axis='both', which='major', labelsize=6)
    ax.set_xlabel("Radial", fontsize=7)
    ax.set_ylabel("Axial", fontsize=7)
    ax.grid(True, linestyle=':', linewidth=0.4, color='grey')
    ax.set_title(f"Luva {res['nome_exibicao']} - Diâmetro {res['DIAM_LUVA']} mm", fontsize=9)

    fig.savefig(caminho, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)

    return caminho
