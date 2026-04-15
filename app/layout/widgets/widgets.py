import flet as ft

""" ----------------------------------------------------- Sidebar ----------------------------------------------------- """

BOTAO_CLOSE_SIDBAR = ft.IconButton(icon=ft.CupertinoIcons.LEFT_CHEVRON)
LOGO_WEG = ft.Image(src="assets/icon.png", width=100) ## Verificar verdadeira posição

PARAMETROS_DA_LUVA_TITLE = ft.Text("Parâmetros da Luva", size=20, weight=ft.FontWeight.W_500)
DROPDOWN_SECAO_NOMINAL_DA_LUVA = ft.Dropdown(label="Seção Nominal da Luva", width=200, border_radius=10, options=[])

FIO_RETANGULAR_TITLE = ft.Text("Fio Retangular", size=20, weight=ft.FontWeight.W_500)
ENTRADA_TEXT_AXIAL = ft.TextField(label="Axial (mm)", width=200, border_radius=10)
ENTRADA_TEXT_RADIAL = ft.TextField(label="Radial (mm)", width=200, border_radius=10)
ENTRADA_TEXT_QUANTIDADE = ft.TextField(label="Quantidade", width=200, border_radius=10)

CABO_CIRCULAR_TITLE = ft.Text("Cabo Circular", size=20, weight=ft.FontWeight.W_500)
CHECK_BOX_EXCLUIR_CABO_CIRCULAR = ft.Checkbox(label="Excluir Cabo Circular")
DROPDOWN_SECAO_NOMINAL_CABO = ft.Dropdown(label="Seção Nominal do Cabo", width=200, border_radius=10, options=[])

TEXT_DIAMETRO = ft.Text("Diâmetro 9.15 (mm)", size=20, weight=ft.FontWeight.W_500)

TITULO_GRANULARIDADE = ft.Text("Diâmetro do Micro-fio (Granularidade)", size=20, weight=ft.FontWeight.W_500)
ENTRADA_TEXT_GRANULARIDADE = ft.TextField(width=200, border_radius=10)
ICONE_PERGUNTA_GRANULARIDADE = ft.Icon(ft.Icons.HELP, color="#888888", size=18, tooltip="O cabo circular é multifilamentoso (composto por vários fios finos). O diâmetro selecionado será o diâmetro da 'partição' criada na simulação. Quanto menor, mais preciso o preenchimento, porém mais lenta a simulação.")


TITULO_CONFIGURACOES = ft.Text("Configurações", size=20, weight=ft.FontWeight.W_500)
TITULO_LIMITE_CONFIGURACAO = ft.Text("Limite de Ocupação (%)", size=18, weight=ft.FontWeight.W_400)
ICONE_PERGUNTA_CONFIGURACOES = ft.Icon(ft.Icons.HELP, color="#888888", size=18, tooltip="Taxa de ocupação é a porcentagem da área interna da luva que é preenchida pelos condutores. O padrão é 85%, conforme WPR-33156 ES (WEG México).")

ELEVATE_BUTTON_EXECUTAR_SIMULACAO = ft.ElevatedButton("Executar Simulação", width=200, height=50, bgcolor="#4CAF50", color="white")

BOTAO_ALTERAR_TEMA = ft.IconButton(icon=ft.Icons.BRIGHTNESS_4, tooltip="Alterar Tema")


""" ----------------------------------------------------- Janela Principal ----------------------------------------------------- """
TITULO_JANELA_PRINCIPAL = ft.Text("Simulação: Fio Retangular + Cabo Circular", size=24, weight=ft.FontWeight.W_600) ## Precisa ser alterado em algumas situaçãoes específicas
DESCRICAO_APP = ft.Text("Este aplicativo simula a montagem prática de luvas, verificando fisicamente se o condutor cabe na luva. Além disso, realiza a simulação utilizando cabos retangulares e circulares para validar o encaixe em luvas curtas.", size=16)

PROGRESS_BAR_SIMULACAO = ft.ProgressBar(width=True, height=10, color=ft.Colors.BLUE_500, visible=True)

TEXT_DADOS_DAS_SECOES = ft.Text("Dados das Seções", size=20, weight=ft.FontWeight.W_500)

TITULO_FIO_RETANGULAR = ft.Text("Fio Retangular", size=13, weight=ft.FontWeight.W_400)
ICONE_PERGUNTA_FIO_RETANGULAR = ft.Icon(ft.Icons.HELP, color="#888888", size=18, tooltip="Unitário: 7.0x1.5 mm | Qtd: 10")
VALOR_FIO_RETANGULAR = ft.Text("105.00 mm²", size=20, weight=ft.FontWeight.W_500)

TITULO_CABO_CIRCULAR = ft.Text("Cabo Circular", size=13, weight=ft.FontWeight.W_400)
VALOR_CABO_CIRCULAR = ft.Text("95.00 mm²", size=20, weight=ft.FontWeight.W_500)

TITULO_LUVA = ft.Text("Luva", size=13, weight=ft.FontWeight.W_400)
ICONE_PERGUNTA_LUVA = ft.Icon(ft.Icons.HELP, color="#888888", size=18, tooltip="Diâmetro: 17.00 mm")
VALOR_LUVA = ft.Text("226.98 mm²", size=20, weight=ft.FontWeight.W_500)

TEXTO_INDICADORES = ft.Text("Indicadores", size=20, weight=ft.FontWeight.W_500)

TITULO_FIOS = ft.Text("Fios", size=13, weight=ft.FontWeight.W_400)
VALOR_INDICADOR_FIOS = ft.Text("10/10", size=20, weight=ft.FontWeight.W_500)

TITULO_OCUPACAO = ft.Text("Ocupação", size=13, weight=ft.FontWeight.W_400)
VALOR_INDICADOR_OCUPACAO = ft.Text("46.40%", size=20, weight=ft.FontWeight.W_500)
ICONE_DESVIO_OCUPACAO = ft.Icon(ft.CupertinoIcons.ARROW_RIGHT)
VALOR_DESVIO_OCUPACAO = ft.Text("0.00%", size=7, weight=ft.FontWeight.W_500)
CONTAINER_DESVIO_OCUPACAO = ft.Container(
    expand=True,
    border_radius=20,
    bgcolor=ft.Colors.GREY_300,
    content=ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ICONE_DESVIO_OCUPACAO,
            VALOR_DESVIO_OCUPACAO
        ]
    )
)

TITULO_AREA_TOTAL = ft.Text("Área Total", size=13, weight=ft.FontWeight.W_400)
VALOR_AREA_TOTAL = ft.Text("163.81 mm²", size=20, weight=ft.FontWeight.W_500)


TEXTO_VALIDACAO_SIMULACAO = ft.Text("Validação da Simulação", size=16, weight=ft.FontWeight.W_400)
CONTAINER_VALIDACAO_SIMULACAO = ft.Container(
    width=True,
    height=50,
    bgcolor=ft.Colors.GREY_300,
    border_radius=10,
    padding=10,
    content=ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            TEXTO_VALIDACAO_SIMULACAO, ft.Container()
        ]
    )
)

TITULO_LOGS_SIMULACAO = ft.Text("Logs da Simulação", size=16, weight=ft.FontWeight.W_500)
LOG_LIMPANDO_SIMULACAO_ANTERIOR = ft.Text("Limpando simulação anterior...", size=14, weight=ft.FontWeight.W_300)
LOG_FASE_1 = ft.Text("Fase 1: Selecionando Luva... (0.04s)", size=14, weight=ft.FontWeight.W_300)
LOG_FASE_2 = ft.Text("Fase 2: Posicionando Fio Retangular... (1.04s)", size=14, weight=ft.FontWeight.W_300)
LOG_FASE_3 = ft.Text("Fase 3: Posicionando Cabo Circular... (0.06s)", size=14, weight=ft.FontWeight.W_300)
LOG_CONCLUSAO_SIMULACAO = ft.Text("Simulação concluída! (Total: 1.14s)", size=14, weight=ft.FontWeight.W_300)

BOTAO_BAIXAR_RELATORIO = ft.ElevatedButton("Baixar Relatório", width=150, bgcolor=ft.Colors.RED)

TITULO_DESENVOLVEDOR = ft.Text("Desenvolvedor", size=14, weight=ft.FontWeight.W_400)
VALOR_DESENVOLVEDOR = ft.Text("DELLAZARING - Parte Ativa Gravataí", size=14, weight=ft.FontWeight.W_500)