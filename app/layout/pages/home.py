import flet as ft
import os
import threading
import base64
from app.layout.widgets.widgets import *
from app.services.simulacao import (
    executar_simulacao as _run_sim,
    salvar_imagem,
    OPCOES_LUVA,
    OPCOES_CABO_CIRCULAR,
)
from app.services.gera_relatorio import create_pdf


class Home(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()

        ## ADD FUNCS AOS BUTTONS
        BOTAO_CLOSE_SIDBAR.on_click = self.close_sidebar
        BOTAO_OPEN_SIDBAR.on_click = self.open_sidbar
        DROPDOWN_SECAO_NOMINAL_DA_LUVA.on_change = self.selection_dropdown_luva
        DROPDOWN_SECAO_NOMINAL_CABO.on_change = self.selection_dropdown_cabo
        SLIDER_GRANULARIDADE.on_change = self.slider_granularidade_change
        SLIDER_LIMITE_OCUPACAO.on_change = self.slider_limite_ocupacao_change
        ENTRADA_LIMITE_CONFIGURACAO.on_change = self.escrevendo_entrada_limite_ocupacao
        ENTRADA_TEXT_GRANULARIDADE.on_change = self.escrevendo_entrada_granularidade
        CHECK_BOX_EXCLUIR_CABO_CIRCULAR.on_change = (
            self.checkbox_excluir_cabo_circular_change
        )
        BOTAO_ALTERAR_TEMA.on_click = self.alterar_tema
        ELEVATE_BUTTON_EXECUTAR_SIMULACAO.on_click = self.executar_simulacao
        BOTAO_BAIXAR_RELATORIO.on_click = self.baixar_relatorio
        ## SIDBAR
        self.sidbar = ft.Container(
            width=310,
            animate=ft.Animation(500, ft.AnimationCurve.DECELERATE),
            height=True,
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY_900),
            border_radius=ft.border_radius.only(top_right=20, bottom_right=20),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ## TOP
                    ft.Container(
                        width=True,
                        height=120,
                        padding=ft.padding.only(top=10, right=5, left=5),
                        # bgcolor="red",
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    width=True,
                                    padding=ft.padding.only(left=20, top=10),
                                    height=100,
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.CrossAxisAlignment.START,
                                        controls=[LOGO_WEG, BOTAO_CLOSE_SIDBAR],
                                    ),
                                ),
                            ],
                        ),
                    ),
                    ## MID
                    ft.Container(
                        expand=True,
                        padding=10,
                        content=ft.Column(
                            scroll="auto",
                            spacing=5,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                PARAMETROS_DA_LUVA_TITLE,
                                DROPDOWN_SECAO_NOMINAL_DA_LUVA,
                                ENTRADA_DIAMETRO_PERSONALIZADO,
                                ft.Container(height=10),
                                DIVIDER_SIDEBAR,
                                ft.Container(height=10),
                                FIO_RETANGULAR_TITLE,
                                ENTRADA_TEXT_AXIAL,
                                ENTRADA_TEXT_RADIAL,
                                ENTRADA_TEXT_QUANTIDADE,
                                ft.Container(height=10),
                                DIVIDER_SIDEBAR,
                                ft.Container(height=10),
                                CABO_CIRCULAR_TITLE,
                                ft.Container(
                                    padding=ft.padding.only(left=60),
                                    alignment=ft.alignment.center,
                                    content=CHECK_BOX_EXCLUIR_CABO_CIRCULAR,
                                ),
                                ft.Container(height=10),
                                DIVIDER_SIDEBAR,
                                ft.Container(height=10),
                                DROPDOWN_SECAO_NOMINAL_CABO,
                                ENTRADA_SECAO_PERSONALIZADA_CABO,
                                ft.Container(height=10),
                                DIVIDER_SIDEBAR,
                                ft.Container(height=10),
                                ft.Row(
                                    spacing=1,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ENTRADA_TEXT_GRANULARIDADE,
                                        ICONE_PERGUNTA_GRANULARIDADE,
                                    ],
                                ),
                                SLIDER_GRANULARIDADE,
                                ft.Container(height=10),
                                DIVIDER_SIDEBAR,
                                ft.Container(height=10),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        TITULO_CONFIGURACOES,
                                        ICONE_PERGUNTA_CONFIGURACOES,
                                    ],
                                ),
                                ENTRADA_LIMITE_CONFIGURACAO,
                                SLIDER_LIMITE_OCUPACAO,
                                ft.Container(height=10),
                                DIVIDER_SIDEBAR,
                                ft.Container(height=10),
                            ],
                        ),
                    ),
                    ## BOTTOM
                    ft.Container(
                        width=True,
                        padding=5,
                        height=100,
                        # bgcolor="blue",
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                    controls=[ELEVATE_BUTTON_EXECUTAR_SIMULACAO],
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.END,
                                    vertical_alignment=ft.CrossAxisAlignment.END,
                                    controls=[BOTAO_ALTERAR_TEMA],
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

        """  --------------------------------------------------------- CONFIG FRAME ---------------------------------------------------------  """
        self.page = page
        self.expand = True

        self._resultado = None
        self._caminho_img = None
        self._simulacao_aprovada = False

        self._file_picker = ft.FilePicker(on_result=self.on_file_picker_result)
        self.page.overlay.append(self._file_picker)

        self.content = self.build()
        """  --------------------------------------------------------------------------------------------------------------------------------  """

    def alterar_tema(self, e):
        if self.page.theme_mode == "light":
            self.page.theme_mode = "dark"
            self.sidbar.bgcolor = ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY_900)
            DIVIDER_SIDEBAR.color = ft.Colors.GREY_900
        else:
            self.page.theme_mode = "light"
            self.sidbar.bgcolor = ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY_100)
            DIVIDER_SIDEBAR.color = ft.Colors.GREY_200

        DIVIDER_SIDEBAR.update()
        self.page.update()

    def open_sidbar(self, e):
        self.sidbar.width = 310
        BOTAO_OPEN_SIDBAR.visible = False
        BOTAO_OPEN_SIDBAR.update()
        self.sidbar.update()

    def close_sidebar(self, e):
        self.sidbar.width = 0.0
        BOTAO_OPEN_SIDBAR.visible = True
        BOTAO_OPEN_SIDBAR.update()
        self.sidbar.update()

    def slider_granularidade_change(self, e):
        ENTRADA_TEXT_GRANULARIDADE.value = f"{SLIDER_GRANULARIDADE.value:.2f}"
        SLIDER_GRANULARIDADE.label = f"{SLIDER_GRANULARIDADE.value:.2f}"
        ENTRADA_TEXT_GRANULARIDADE.update()
        SLIDER_GRANULARIDADE.update()

    def slider_limite_ocupacao_change(self, e):
        ENTRADA_LIMITE_CONFIGURACAO.value = f"{SLIDER_LIMITE_OCUPACAO.value:.0f}"
        SLIDER_LIMITE_OCUPACAO.label = f"{SLIDER_LIMITE_OCUPACAO.value:.0f}"
        ENTRADA_LIMITE_CONFIGURACAO.update()
        SLIDER_LIMITE_OCUPACAO.update()

    def escrevendo_entrada_limite_ocupacao(self, e):
        if ENTRADA_LIMITE_CONFIGURACAO.error_text != None:
            ENTRADA_LIMITE_CONFIGURACAO.error_text = None
            ENTRADA_LIMITE_CONFIGURACAO.update()
        try:
            valor = float(ENTRADA_LIMITE_CONFIGURACAO.value)
            if 0 <= valor <= 100:
                SLIDER_LIMITE_OCUPACAO.value = valor
                SLIDER_LIMITE_OCUPACAO.label = f"{valor:.0f}"
                SLIDER_LIMITE_OCUPACAO.update()
            else:
                ENTRADA_LIMITE_CONFIGURACAO.error_text = "Valor deve ser entre 0 e 100."
                ENTRADA_LIMITE_CONFIGURACAO.update()
        except ValueError:
            pass

    def escrevendo_entrada_granularidade(self, e):

        if ENTRADA_TEXT_GRANULARIDADE.error_text != None:
            ENTRADA_TEXT_GRANULARIDADE.error_text = None
            ENTRADA_TEXT_GRANULARIDADE.update()

        try:
            valor = float(ENTRADA_TEXT_GRANULARIDADE.value)
            if 0.4 <= valor <= 2.0:
                SLIDER_GRANULARIDADE.value = valor
                SLIDER_GRANULARIDADE.label = f"{valor:.2f}"
                SLIDER_GRANULARIDADE.update()
            else:
                ENTRADA_TEXT_GRANULARIDADE.error_text = (
                    "Valor deve ser entre 0.40 e 2.00."
                )
                ENTRADA_TEXT_GRANULARIDADE.update()

        except ValueError:
            pass

    def selection_dropdown_luva(self, e):
        match DROPDOWN_SECAO_NOMINAL_DA_LUVA.value:
            case "25 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 8.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "35 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 9.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "50 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 11.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "70 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 13.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "95 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 15.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "120 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 17.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "150 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 19.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "185 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 21.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "240 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 24.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "300 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 24.5
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "400 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 30.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "500 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 33.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "630 mm²":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 39.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = True
            case "Personalizado":
                ENTRADA_DIAMETRO_PERSONALIZADO.value = 0.0
                ENTRADA_DIAMETRO_PERSONALIZADO.disabled = False
                pass
        ENTRADA_DIAMETRO_PERSONALIZADO.visible = True
        ENTRADA_DIAMETRO_PERSONALIZADO.update()

    def selection_dropdown_cabo(self, e):
        match DROPDOWN_SECAO_NOMINAL_CABO.value:
            case "50 mm²":
                ENTRADA_SECAO_PERSONALIZADA_CABO.value = 9.15
                ENTRADA_SECAO_PERSONALIZADA_CABO.disabled = True
            case "70 mm²":
                ENTRADA_SECAO_PERSONALIZADA_CABO.value = 10.83
                ENTRADA_SECAO_PERSONALIZADA_CABO.disabled = True
            case "120 mm²":
                ENTRADA_SECAO_PERSONALIZADA_CABO.value = 14.77
                ENTRADA_SECAO_PERSONALIZADA_CABO.disabled = True
            case "185 mm²":
                ENTRADA_SECAO_PERSONALIZADA_CABO.value = 18.09
                ENTRADA_SECAO_PERSONALIZADA_CABO.disabled = True
            case "240 mm²":
                ENTRADA_SECAO_PERSONALIZADA_CABO.value = 23.3
                ENTRADA_SECAO_PERSONALIZADA_CABO.disabled = True
            case "300 mm²":
                ENTRADA_SECAO_PERSONALIZADA_CABO.value = 23.5
                ENTRADA_SECAO_PERSONALIZADA_CABO.disabled = True
            case "400 mm²":
                ENTRADA_SECAO_PERSONALIZADA_CABO.value = 29.1
                ENTRADA_SECAO_PERSONALIZADA_CABO.disabled = True
            case "500 mm²":
                ENTRADA_SECAO_PERSONALIZADA_CABO.value = 33.5
                ENTRADA_SECAO_PERSONALIZADA_CABO.disabled = True
            case "Personalizado":
                ENTRADA_SECAO_PERSONALIZADA_CABO.value = 0.0
                ENTRADA_SECAO_PERSONALIZADA_CABO.disabled = False
                pass
        ENTRADA_SECAO_PERSONALIZADA_CABO.visible = True
        ENTRADA_SECAO_PERSONALIZADA_CABO.update()

    def checkbox_excluir_cabo_circular_change(self, e):
        if CHECK_BOX_EXCLUIR_CABO_CIRCULAR.value == True:
            TITULO_JANELA_PRINCIPAL.value = "Simulação: Fio Retangular"
            DROPDOWN_SECAO_NOMINAL_CABO.visible = False
            ENTRADA_SECAO_PERSONALIZADA_CABO.visible = False
            ENTRADA_TEXT_GRANULARIDADE.visible = False
            ICONE_PERGUNTA_GRANULARIDADE.visible = False
            SLIDER_GRANULARIDADE.visible = False
        else:
            TITULO_JANELA_PRINCIPAL.value = "Simulação: Fio Retangular + Cabo Circular"
            DROPDOWN_SECAO_NOMINAL_CABO.visible = True
            ENTRADA_SECAO_PERSONALIZADA_CABO.visible = True
            ENTRADA_TEXT_GRANULARIDADE.visible = True
            ICONE_PERGUNTA_GRANULARIDADE.visible = True
            SLIDER_GRANULARIDADE.visible = True

        TITULO_JANELA_PRINCIPAL.update()
        DROPDOWN_SECAO_NOMINAL_CABO.update()
        ENTRADA_SECAO_PERSONALIZADA_CABO.update()
        ENTRADA_TEXT_GRANULARIDADE.update()
        ICONE_PERGUNTA_GRANULARIDADE.update()
        SLIDER_GRANULARIDADE.update()

    def executar_simulacao(self, e):
        # --- Leitura e validação dos inputs ---
        try:
            ALT_RECT = float(ENTRADA_TEXT_AXIAL.value or 0)
            LARG_RECT = float(ENTRADA_TEXT_RADIAL.value or 0)
            QTD_RECT = int(float(ENTRADA_TEXT_QUANTIDADE.value or 0))
        except ValueError:
            CONTAINER_VALIDACAO_SIMULACAO.bgcolor = ft.Colors.with_opacity(
                0.2, ft.Colors.RED_500
            )
            TEXTO_VALIDACAO_SIMULACAO.value = (
                "Erro: preencha corretamente Axial, Radial e Quantidade."
            )
            TEXTO_VALIDACAO_SIMULACAO.color = ft.Colors.RED_300
            CONTAINER_VALIDACAO_SIMULACAO.visible = True
            TEXTO_VALIDACAO_SIMULACAO.visible = True
            CONTAINER_VALIDACAO_SIMULACAO.update()
            TEXTO_VALIDACAO_SIMULACAO.update()
            return

        escolha_luva = DROPDOWN_SECAO_NOMINAL_DA_LUVA.value or "Automático"

        if escolha_luva == "Personalizado":
            try:
                DIAM_LUVA = float(ENTRADA_DIAMETRO_PERSONALIZADO.value or 0)
            except ValueError:
                DIAM_LUVA = 0.0
        elif escolha_luva == "Automático":
            DIAM_LUVA = 0.0
        else:
            DIAM_LUVA = OPCOES_LUVA.get(escolha_luva, 0.0)

        excluir_circular = bool(CHECK_BOX_EXCLUIR_CABO_CIRCULAR.value)
        DIAM_MICRO_FIO = float(SLIDER_GRANULARIDADE.value or 0.8)
        LIMITE_OCUPACAO = float(SLIDER_LIMITE_OCUPACAO.value or 85) / 100.0

        escolha_cabo = DROPDOWN_SECAO_NOMINAL_CABO.value or "50 mm²"
        if excluir_circular:
            DIAM_REDONDO_TOTAL = 0.0
        elif escolha_cabo == "Personalizado":
            try:
                DIAM_REDONDO_TOTAL = float(ENTRADA_SECAO_PERSONALIZADA_CABO.value or 0)
            except ValueError:
                DIAM_REDONDO_TOTAL = 0.0
        else:
            DIAM_REDONDO_TOTAL = OPCOES_CABO_CIRCULAR.get(escolha_cabo, 0.0)

        # --- Prepara UI para a simulação ---
        PROGRESS_BAR_SIMULACAO.value = 0
        PROGRESS_BAR_SIMULACAO.visible = True
        PROGRESS_BAR_SIMULACAO.update()

        TITULO_LOGS_SIMULACAO.visible = True
        LOG_LIMPANDO_SIMULACAO_ANTERIOR.visible = False
        LOG_FASE_1.visible = False
        LOG_FASE_2.visible = False
        LOG_FASE_3.visible = False
        LOG_CONCLUSAO_SIMULACAO.visible = False
        BOTAO_BAIXAR_RELATORIO.visible = False
        CONTAINER_VALIDACAO_SIMULACAO.visible = False
        self.page.update()

        # --- Callbacks para atualização em tempo real ---
        _log_widgets = [
            LOG_LIMPANDO_SIMULACAO_ANTERIOR,
            LOG_FASE_1,
            LOG_FASE_2,
            LOG_FASE_3,
            LOG_CONCLUSAO_SIMULACAO,
        ]

        def on_log(fase_idx: int, texto: str):
            widget = _log_widgets[fase_idx]
            widget.value = texto
            widget.visible = True
            widget.update()

        def on_progress(valor: int):
            PROGRESS_BAR_SIMULACAO.value = valor / 100.0
            PROGRESS_BAR_SIMULACAO.update()

        # --- Executa simulação em thread separada ---
        def run():
            resultado = _run_sim(
                escolha_luva=escolha_luva,
                DIAM_LUVA=DIAM_LUVA,
                LARG_RECT=LARG_RECT,
                ALT_RECT=ALT_RECT,
                QTD_RECT=QTD_RECT,
                excluir_circular=excluir_circular,
                DIAM_REDONDO_TOTAL=DIAM_REDONDO_TOTAL,
                DIAM_MICRO_FIO=DIAM_MICRO_FIO,
                LIMITE_OCUPACAO=LIMITE_OCUPACAO,
                escolha_cabo=escolha_cabo,
                on_log=on_log,
                on_progress=on_progress,
            )

            if "erro" in resultado:
                CONTAINER_VALIDACAO_SIMULACAO.bgcolor = ft.Colors.with_opacity(
                    0.2, ft.Colors.RED_500
                )
                TEXTO_VALIDACAO_SIMULACAO.value = resultado["erro"]
                TEXTO_VALIDACAO_SIMULACAO.color = ft.Colors.RED_300
                CONTAINER_VALIDACAO_SIMULACAO.visible = True
                TEXTO_VALIDACAO_SIMULACAO.visible = True
                self.page.update()
                return

            # Salva imagem e carrega como base64 para exibição
            caminho_img = salvar_imagem(resultado)
            with open(caminho_img, "rb") as f:
                IMAGEM_SIMULACAO.src_base64 = base64.b64encode(f.read()).decode("utf-8")
            IMAGEM_SIMULACAO.visible = True

            res = resultado
            self._resultado = resultado
            self._caminho_img = caminho_img

            # Dados das Seções
            TEXT_DADOS_DAS_SECOES.visible = True

            TITULO_FIO_RETANGULAR.visible = True
            ICONE_PERGUNTA_FIO_RETANGULAR.tooltip = f"Unitário: {res['LARG_RECT']}x{res['ALT_RECT']} mm | Qtd: {res['QTD_RECT']}"
            ICONE_PERGUNTA_FIO_RETANGULAR.visible = True
            VALOR_FIO_RETANGULAR.value = f"{res['area_rect_total']:.2f} mm²"
            VALOR_FIO_RETANGULAR.visible = True

            TITULO_CABO_CIRCULAR.visible = not res["excluir_circular"]
            VALOR_CABO_CIRCULAR.value = f"{res['area_redondo_total']:.2f} mm²"
            VALOR_CABO_CIRCULAR.visible = not res["excluir_circular"]

            TITULO_LUVA.visible = True
            ICONE_PERGUNTA_LUVA.tooltip = f"Diâmetro: {res['DIAM_LUVA']} mm"
            ICONE_PERGUNTA_LUVA.visible = True
            VALOR_LUVA.value = f"{res['area_luva']:.2f} mm²"
            VALOR_LUVA.visible = True

            # Indicadores
            TEXTO_INDICADORES.visible = True

            TITULO_FIOS.visible = True
            VALOR_INDICADOR_FIOS.value = (
                f"{len(res['melhor_rects'])} / {res['QTD_RECT']}"
            )
            VALOR_INDICADOR_FIOS.visible = True

            TITULO_OCUPACAO.visible = True
            VALOR_INDICADOR_OCUPACAO.value = f"{res['taxa'] * 100:.1f}%"
            VALOR_INDICADOR_OCUPACAO.visible = True

            delta_taxa = (res["taxa"] - res["LIMITE_OCUPACAO"]) * 100
            VALOR_DESVIO_OCUPACAO.value = f"{delta_taxa:+.1f}%"
            if delta_taxa <= 0:
                ICONE_DESVIO_OCUPACAO.name = ft.CupertinoIcons.ARROW_DOWN
                ICONE_DESVIO_OCUPACAO.color = ft.Colors.GREEN_200
                VALOR_DESVIO_OCUPACAO.color = ft.Colors.GREEN_200
                CONTAINER_DESVIO_OCUPACAO.bgcolor = ft.Colors.with_opacity(
                    0.2, ft.Colors.GREEN_500
                )
            else:
                ICONE_DESVIO_OCUPACAO.name = ft.CupertinoIcons.ARROW_UP
                ICONE_DESVIO_OCUPACAO.color = ft.Colors.RED_200
                VALOR_DESVIO_OCUPACAO.color = ft.Colors.RED_200
                CONTAINER_DESVIO_OCUPACAO.bgcolor = ft.Colors.with_opacity(
                    0.2, ft.Colors.RED_500
                )
            ICONE_DESVIO_OCUPACAO.visible = True
            VALOR_DESVIO_OCUPACAO.visible = True
            CONTAINER_DESVIO_OCUPACAO.visible = True

            TITULO_AREA_TOTAL.visible = True
            VALOR_AREA_TOTAL.value = f"{res['area_total_ocupada']:.2f} mm²"
            VALOR_AREA_TOTAL.visible = True

            # Validação final
            falha_retangulos = len(res["melhor_rects"]) < res["QTD_RECT"]
            falha_ocupacao = res["taxa"] > res["LIMITE_OCUPACAO"]
            falha_circular = (
                not res["excluir_circular"]
                and res["qtd_micro_fios"] > 0
                and len(res["micro_fios"]) < res["qtd_micro_fios"]
            )
            simulacao_aprovada = not (
                falha_retangulos or falha_ocupacao or falha_circular
            )
            self._simulacao_aprovada = simulacao_aprovada

            if simulacao_aprovada:
                msg = f"Aprovada | Orientação: {res['orientacao_final']} | Fios: {len(res['melhor_rects'])}/{res['QTD_RECT']}"
                if not res["excluir_circular"] and res["qtd_micro_fios"] > 0:
                    pct = len(res["micro_fios"]) / res["qtd_micro_fios"] * 100
                    msg += f" | Circular: {pct:.0f}%"
                msg += f" | {res['elapsed_time']:.2f}s"
                CONTAINER_VALIDACAO_SIMULACAO.bgcolor = ft.Colors.with_opacity(
                    0.2, ft.Colors.GREEN_500
                )
                TEXTO_VALIDACAO_SIMULACAO.value = msg
                TEXTO_VALIDACAO_SIMULACAO.color = ft.Colors.GREEN_300
            else:
                motivos = []
                if falha_retangulos:
                    motivos.append(
                        f"Fios: {len(res['melhor_rects'])}/{res['QTD_RECT']}"
                    )
                if falha_circular:
                    pct = len(res["micro_fios"]) / res["qtd_micro_fios"] * 100
                    motivos.append(f"Circular: {pct:.0f}%")
                if falha_ocupacao:
                    motivos.append(
                        f"Ocupação: {res['taxa'] * 100:.1f}% > {res['LIMITE_OCUPACAO'] * 100:.0f}%"
                    )
                CONTAINER_VALIDACAO_SIMULACAO.bgcolor = ft.Colors.with_opacity(
                    0.2, ft.Colors.RED_500
                )
                TEXTO_VALIDACAO_SIMULACAO.value = (
                    f"Reprovada | {', '.join(motivos)} | {res['elapsed_time']:.2f}s"
                )
                TEXTO_VALIDACAO_SIMULACAO.color = ft.Colors.RED_300

            CONTAINER_VALIDACAO_SIMULACAO.visible = True
            TEXTO_VALIDACAO_SIMULACAO.visible = True
            BOTAO_BAIXAR_RELATORIO.visible = True

            self.page.update()

        threading.Thread(target=run, daemon=True).start()

    def baixar_relatorio(self, e):
        if self._resultado is None:
            return
        import datetime

        fuso_br = datetime.timezone(datetime.timedelta(hours=-3))
        data_hoje = datetime.datetime.now(fuso_br).strftime("%d-%m-%Y")
        self._file_picker.save_file(
            dialog_title="Salvar Relatório",
            file_name=f"relatorio_simulacao_{data_hoje}.pdf",
            allowed_extensions=["pdf"],
        )
        self.page.update()

    def on_file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.path is None:
            return
        pdf_bytes = create_pdf(
            self._resultado,
            self._caminho_img,
            self._simulacao_aprovada,
            TEXTO_VALIDACAO_SIMULACAO.value,
        )
        with open(e.path, "wb") as f:
            f.write(pdf_bytes)
        if self._caminho_img and os.path.exists(self._caminho_img):
            os.remove(self._caminho_img)
        self.page.open(
            ft.SnackBar(
                content=ft.Text(f"Relatório salvo em: {e.path}"),
                bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.GREEN_800),
            )
        )

    def build(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.sidbar,
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=True,
                                height=120,
                                padding=ft.padding.only(top=50, right=10, left=10),
                                # bgcolor="red",
                                content=ft.Column(
                                    width=True,
                                    height=50,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.START,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                            controls=[
                                                BOTAO_OPEN_SIDBAR,
                                                ft.Container(width=20),
                                                TITULO_JANELA_PRINCIPAL,
                                            ],
                                        ),
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.START,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                            controls=[DESCRICAO_APP],
                                        ),
                                    ],
                                ),
                            ),
                            ft.Container(height=20),
                            ## Progress Bar
                            ft.Container(
                                width=True,
                                height=50,
                                alignment=ft.alignment.center,
                                padding=ft.padding.only(right=30, left=30),
                                content=PROGRESS_BAR_SIMULACAO,
                            ),
                            ## DADOS GERAIS
                            ft.Container(
                                expand=True,
                                content=ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ## Container dados
                                        ft.Container(
                                            expand=True,
                                            padding=10,
                                            content=ft.Column(
                                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ## Dados da seção
                                                    ft.Container(
                                                        expand=True,
                                                        # bgcolor="red",
                                                        content=ft.Column(
                                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                            controls=[
                                                                ft.Container(
                                                                    width=True,
                                                                    height=50,
                                                                    padding=ft.padding.only(
                                                                        left=5
                                                                    ),
                                                                    alignment=ft.alignment.center_left,
                                                                    content=TEXT_DADOS_DAS_SECOES,
                                                                ),
                                                                ft.Container(
                                                                    expand=True,
                                                                    padding=10,
                                                                    content=ft.Row(
                                                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                                        controls=[
                                                                            ## Fio retangular
                                                                            ft.Container(
                                                                                width=200,
                                                                                height=True,
                                                                                alignment=ft.alignment.center,
                                                                                content=ft.Column(
                                                                                    alignment=ft.MainAxisAlignment.START,
                                                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                                                    controls=[
                                                                                        ft.Row(
                                                                                            alignment=ft.MainAxisAlignment.CENTER,
                                                                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                                                            controls=[
                                                                                                TITULO_FIO_RETANGULAR,
                                                                                                ICONE_PERGUNTA_FIO_RETANGULAR,
                                                                                            ],
                                                                                        ),
                                                                                        VALOR_FIO_RETANGULAR,
                                                                                    ],
                                                                                ),
                                                                            ),
                                                                            ## Cabo Cirbular
                                                                            ft.Container(
                                                                                width=200,
                                                                                height=True,
                                                                                alignment=ft.alignment.center,
                                                                                content=ft.Column(
                                                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                                                    controls=[
                                                                                        TITULO_CABO_CIRCULAR,
                                                                                        VALOR_CABO_CIRCULAR,
                                                                                    ],
                                                                                ),
                                                                            ),
                                                                            ##Luva
                                                                            ft.Container(
                                                                                width=200,
                                                                                height=True,
                                                                                alignment=ft.alignment.center,
                                                                                content=ft.Column(
                                                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                                                    controls=[
                                                                                        ft.Row(
                                                                                            alignment=ft.MainAxisAlignment.CENTER,
                                                                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                                                            controls=[
                                                                                                TITULO_LUVA,
                                                                                                ICONE_PERGUNTA_LUVA,
                                                                                            ],
                                                                                        ),
                                                                                        VALOR_LUVA,
                                                                                    ],
                                                                                ),
                                                                            ),
                                                                        ],
                                                                    ),
                                                                ),
                                                            ],
                                                        ),
                                                    ),
                                                    ft.Divider(
                                                        height=1,
                                                        color=ft.Colors.GREY_900,
                                                    ),
                                                    ## Indicadores
                                                    ft.Container(
                                                        expand=True,
                                                        # bgcolor="blue",
                                                        content=ft.Column(
                                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                            controls=[
                                                                ft.Container(
                                                                    width=True,
                                                                    height=50,
                                                                    padding=ft.padding.only(
                                                                        left=5
                                                                    ),
                                                                    alignment=ft.alignment.center_left,
                                                                    content=TEXTO_INDICADORES,
                                                                ),
                                                                ft.Container(
                                                                    expand=True,
                                                                    padding=10,
                                                                    content=ft.Row(
                                                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                                        controls=[
                                                                            ft.Container(
                                                                                width=200,
                                                                                height=True,
                                                                                alignment=ft.alignment.center,
                                                                                content=ft.Column(
                                                                                    alignment=ft.MainAxisAlignment.START,
                                                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                                                    controls=[
                                                                                        ft.Row(
                                                                                            alignment=ft.MainAxisAlignment.CENTER,
                                                                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                                                            controls=[
                                                                                                TITULO_FIOS
                                                                                            ],
                                                                                        ),
                                                                                        VALOR_INDICADOR_FIOS,
                                                                                    ],
                                                                                ),
                                                                            ),
                                                                            ft.Container(
                                                                                width=400,
                                                                                height=True,
                                                                                alignment=ft.alignment.center,
                                                                                content=ft.Column(
                                                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                                                    controls=[
                                                                                        TITULO_OCUPACAO,
                                                                                        VALOR_INDICADOR_OCUPACAO,
                                                                                        ft.Container(
                                                                                            content=CONTAINER_DESVIO_OCUPACAO
                                                                                        ),
                                                                                    ],
                                                                                ),
                                                                            ),
                                                                            ft.Container(
                                                                                width=200,
                                                                                height=True,
                                                                                alignment=ft.alignment.center,
                                                                                content=ft.Column(
                                                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                                                    controls=[
                                                                                        ft.Row(
                                                                                            alignment=ft.MainAxisAlignment.CENTER,
                                                                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                                                            controls=[
                                                                                                TITULO_AREA_TOTAL
                                                                                            ],
                                                                                        ),
                                                                                        VALOR_AREA_TOTAL,
                                                                                    ],
                                                                                ),
                                                                            ),
                                                                        ],
                                                                    ),
                                                                ),
                                                            ],
                                                        ),
                                                    ),
                                                ],
                                            ),
                                        ),
                                        ## Container Graph
                                        ft.Container(
                                            expand=True,
                                            alignment=ft.alignment.center,
                                            content=IMAGEM_SIMULACAO,
                                        ),
                                    ],
                                ),
                            ),
                            ft.Container(height=20),
                            ## VALIDACAO
                            ft.Container(
                                width=True,
                                height=40,
                                padding=ft.padding.only(right=15, left=15),
                                content=CONTAINER_VALIDACAO_SIMULACAO,
                            ),
                            ## LOGS
                            ft.Container(
                                width=True,
                                height=300,
                                padding=ft.padding.only(right=15, left=15),
                                content=ft.Column(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Container(
                                            width=True,
                                            padding=5,
                                            height=40,
                                            content=ft.Row(
                                                alignment=ft.MainAxisAlignment.START,
                                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[TITULO_LOGS_SIMULACAO],
                                            ),
                                        ),
                                        ft.Container(
                                            expand=True,
                                            padding=10,
                                            content=ft.Row(
                                                alignment=ft.MainAxisAlignment.START,
                                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ft.Column(
                                                        spacing=2,
                                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                        horizontal_alignment=ft.CrossAxisAlignment.START,
                                                        controls=[
                                                            LOG_LIMPANDO_SIMULACAO_ANTERIOR,
                                                            LOG_FASE_1,
                                                            LOG_FASE_2,
                                                            LOG_FASE_3,
                                                            LOG_CONCLUSAO_SIMULACAO,
                                                            ft.Container(
                                                                width=True,
                                                                height=30,
                                                                content=BOTAO_BAIXAR_RELATORIO,
                                                            ),
                                                        ],
                                                    )
                                                ],
                                            ),
                                        ),
                                    ],
                                ),
                            ),
                            ft.Divider(height=1, color=ft.Colors.GREY_900),
                            ## DEV
                            ft.Container(
                                width=True,
                                height=70,
                                padding=ft.padding.only(left=15, bottom=10),
                                content=ft.Row(
                                    alignment=ft.MainAxisAlignment.START,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        TITULO_DESENVOLVEDOR,
                                        VALOR_DESENVOLVEDOR,
                                    ],
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        )
