import datetime
import os

from fpdf import FPDF


class _RelatorioPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Desenvolvido por: DELLAZARIG - Parte Ativa Gravataí", 0, 0, "C")


def create_pdf(res: dict, img_path: str | None, aprovado: bool, msg_status: str) -> bytes:
    """Gera o relatório PDF da simulação e retorna os bytes prontos para gravação."""
    pdf = _RelatorioPDF()
    pdf.add_page()

    # Cabeçalho
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório de Simulação: Luvas x Cabos", ln=True, align="C")
    pdf.set_font("Arial", "I", 10)
    fuso_br = datetime.timezone(datetime.timedelta(hours=-3))
    pdf.cell(
        0,
        10,
        f"Gerado em: {datetime.datetime.now(fuso_br).strftime('%d/%m/%Y %H:%M')}",
        ln=True,
        align="C",
    )
    pdf.ln(5)

    # Dados de Entrada (2 colunas)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Dados de Entrada", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font("Arial", "", 10)

    pdf.cell(95, 6, f"Luva: {res['nome_exibicao']} (Diam: {res['DIAM_LUVA']} mm)", border=0)
    pdf.cell(95, 6, f"Cabo: {res['cabo_selecionado']}", border=0, ln=True)

    pdf.cell(95, 6, f"Fio Retangular: {res['LARG_RECT']} x {res['ALT_RECT']} mm", border=0)
    gran_txt = f"{res['DIAM_MICRO_FIO']} mm" if not res["excluir_circular"] else "N/A"
    pdf.cell(95, 6, f"Granularidade: {gran_txt}", border=0, ln=True)

    pdf.cell(95, 6, f"Fios Retangulares: {res['QTD_RECT']}", border=0)
    pdf.cell(95, 6, f"Limite Ocupação: {res['LIMITE_OCUPACAO'] * 100:.1f}%", border=0, ln=True)

    pdf.ln(5)

    # Resultados
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Resultados Calculados", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font("Arial", "", 10)

    pdf.cell(63, 7, f"Ocupação Real: {res['taxa'] * 100:.1f}%", border=0)
    pdf.cell(63, 7, f"Área Ocupada: {res['area_total_ocupada']:.2f} mm2", border=0)
    pdf.cell(64, 7, f"Área Luva: {res['area_luva']:.2f} mm2", border=0, ln=True)

    pdf.cell(95, 7, f"Fios Retangulares: {len(res['melhor_rects'])} / {res['QTD_RECT']}", border=0)
    qtd_circ = (
        f"{len(res['micro_fios'])} / {res['qtd_micro_fios']}"
        if not res["excluir_circular"]
        else "-"
    )
    pdf.cell(95, 7, f"Micro-fios Circulares: {qtd_circ}", border=0, ln=True)

    pdf.ln(10)

    # Status
    pdf.set_font("Arial", "B", 16)
    if aprovado:
        pdf.set_text_color(0, 128, 0)
        pdf.cell(0, 10, "RESULTADO: APROVADO", ln=True, align="C")
    else:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, "RESULTADO: REPROVADO", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)

    # Imagem
    if img_path and os.path.exists(img_path):
        pdf.image(img_path, x=55, w=100)

    result = pdf.output(dest="S")
    if isinstance(result, str):
        return result.encode("latin-1")
    return bytes(result)
