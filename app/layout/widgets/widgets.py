import flet as ft

""" ----------------------------------------------------- Sidebar ----------------------------------------------------- """

BOTAO_CLOSE_SIDBAR = ft.IconButton(icon=ft.CupertinoIcons.LEFT_CHEVRON)
LOGO_WEG = ft.Image(src="assets/icon.png", width=80) ## Verificar verdadeira posição

DIVIDER_SIDEBAR = ft.Divider(height=1, color="transparent")
PARAMETROS_DA_LUVA_TITLE = ft.Text("Parâmetros da Luva", size=15, weight=ft.FontWeight.W_500)
DROPDOWN_SECAO_NOMINAL_DA_LUVA = ft.Dropdown(label="Seção Nominal da Luva", width=300, border_radius=10, label_style=ft.TextStyle(12), text_style=ft.TextStyle(12), scale=0.88, editable=True, input_filter=True, enable_filter=True, options=[
    ft.dropdown.Option("Automático"),
    ft.dropdown.Option("25 mm²"),
    ft.dropdown.Option("35 mm²"),
    ft.dropdown.Option("50 mm²"),
    ft.dropdown.Option("70 mm²"),
    ft.dropdown.Option("95 mm²"),
    ft.dropdown.Option("120 mm²"),
    ft.dropdown.Option("150 mm²"),
    ft.dropdown.Option("185 mm²"),
    ft.dropdown.Option("240 mm²"),
    ft.dropdown.Option("300 mm²"),
    ft.dropdown.Option("400 mm²"),
    ft.dropdown.Option("500 mm²"),
    ft.dropdown.Option("630 mm²"),
    ft.dropdown.Option("Personalizado"),
])

ENTRADA_DIAMETRO_PERSONALIZADO = ft.TextField(label="Diâmetro da Luva (mm)", width=300, border_radius=10, scale=0.88, label_style=ft.TextStyle(size=12), text_style=ft.TextStyle(size=12), visible=False)

FIO_RETANGULAR_TITLE = ft.Text("Fio Retangular", size=13, weight=ft.FontWeight.W_500)
ENTRADA_TEXT_AXIAL = ft.TextField(label="Axial (mm)", width=300, border_radius=10, scale=0.88, label_style=ft.TextStyle(size=12), text_style=ft.TextStyle(size=12))
ENTRADA_TEXT_RADIAL = ft.TextField(label="Radial (mm)", width=300, border_radius=10, scale=0.88, label_style=ft.TextStyle(size=12), text_style=ft.TextStyle(size=12))
ENTRADA_TEXT_QUANTIDADE = ft.TextField(label="Quantidade", width=300, border_radius=10, scale=0.88, label_style=ft.TextStyle(size=12), text_style=ft.TextStyle(size=12))

CABO_CIRCULAR_TITLE = ft.Text("Cabo Circular", size=13, weight=ft.FontWeight.W_500)
CHECK_BOX_EXCLUIR_CABO_CIRCULAR = ft.Checkbox(label="Excluir Cabo Circular")
DROPDOWN_SECAO_NOMINAL_CABO = ft.Dropdown(label="Seção Nominal do Cabo", width=300, border_radius=10, label_style=ft.TextStyle(size=12), text_style=ft.TextStyle(size=12), scale=0.88, editable=True, input_filter=True, enable_filter=True, options=[
    ft.dropdown.Option("Automático"),
    ft.dropdown.Option("50 mm²"),
    ft.dropdown.Option("70 mm²"),
    ft.dropdown.Option("120 mm²"),
    ft.dropdown.Option("185 mm²"),
    ft.dropdown.Option("240 mm²"),
    ft.dropdown.Option("300 mm²"),
    ft.dropdown.Option("400 mm²"),
    ft.dropdown.Option("500 mm²"),
    ft.dropdown.Option("Personalizado"),
])

ENTRADA_SECAO_PERSONALIZADA_CABO = ft.TextField(label="Diâmetro equivalente total (mm)", width=300, border_radius=10, scale=0.88, label_style=ft.TextStyle(size=12), text_style=ft.TextStyle(size=12), visible=False)

TEXT_DIAMETRO = ft.Text("Diâmetro 9.15 (mm)", size=13, weight=ft.FontWeight.W_500)

ENTRADA_TEXT_GRANULARIDADE = ft.TextField(label="Diâmetro do Micro-fio (Granularidade)", value="0.80", width=250, border_radius=10, scale=0.88, label_style=ft.TextStyle(size=12), text_style=ft.TextStyle(size=12))
ICONE_PERGUNTA_GRANULARIDADE = ft.Icon(ft.Icons.HELP_OUTLINE, size=17, color="#888888", tooltip="O cabo circular é multifilamentoso (composto por vários fios finos). O diâmetro selecionado será o diâmetro da 'partição' criada na simulação. Quanto menor, mais preciso o preenchimento, porém mais lenta a simulação.")
SLIDER_GRANULARIDADE = ft.Slider(min=0.4, max=2.0, value=0.80, divisions=160, width=250, scale=0.7)

TITULO_CONFIGURACOES = ft.Text("Configurações", size=13, weight=ft.FontWeight.W_500)
ENTRADA_LIMITE_CONFIGURACAO = ft.TextField(label="Limite de Ocupação (%)", value="85", width=300, border_radius=10, scale=0.88, label_style=ft.TextStyle(size=12), text_style=ft.TextStyle(size=12))
ICONE_PERGUNTA_CONFIGURACOES = ft.Icon(ft.Icons.HELP_OUTLINE, size=17, color="#888888", tooltip="Taxa de ocupação é a porcentagem da área interna da luva que é preenchida pelos condutores. O padrão é 85%, conforme WPR-33156 ES (WEG México).")
SLIDER_LIMITE_OCUPACAO = ft.Slider(min=0.0, max=100.0, value=85.0, divisions=100, width=250, scale=0.7)

ELEVATE_BUTTON_EXECUTAR_SIMULACAO = ft.ElevatedButton("Executar Simulação", width=150, height=30, bgcolor=ft.Colors.with_opacity(0.8,ft.Colors.BLUE_800), color="white")

BOTAO_ALTERAR_TEMA = ft.IconButton(icon=ft.Icons.BRIGHTNESS_4, tooltip="Alterar Tema")


""" ----------------------------------------------------- Janela Principal ----------------------------------------------------- """
BOTAO_OPEN_SIDBAR = ft.IconButton(icon=ft.CupertinoIcons.RIGHT_CHEVRON, visible=False, animate_opacity=1000)
TITULO_JANELA_PRINCIPAL = ft.Text("Simulação: Fio Retangular + Cabo Circular", size=27, weight=ft.FontWeight.W_600) ## Precisa ser alterado em algumas situaçãoes específicas
DESCRICAO_APP = ft.Text("Este aplicativo simula a montagem prática de luvas, verificando fisicamente se o condutor cabe na luva. Além disso, realiza a simulação \nutilizando cabos retangulares e circulares para validar o encaixe em luvas curtas.", size=16)

PROGRESS_BAR_SIMULACAO = ft.ProgressBar(width=True, height=8, color=ft.Colors.BLUE_500, visible=False, border_radius=20)

TEXT_DADOS_DAS_SECOES = ft.Text("Dados das Seções", size=20, weight=ft.FontWeight.W_500, visible=False)

TITULO_FIO_RETANGULAR = ft.Text("Fio Retangular", size=13, weight=ft.FontWeight.W_400, visible=False)
ICONE_PERGUNTA_FIO_RETANGULAR = ft.Icon(ft.Icons.HELP_OUTLINE, color="#888888", size=18, tooltip="Unitário: 7.0x1.5 mm | Qtd: 10", visible=False)
VALOR_FIO_RETANGULAR = ft.Text("105.00 mm²", size=20, weight=ft.FontWeight.W_500, visible=False)

TITULO_CABO_CIRCULAR = ft.Text("Cabo Circular", size=13, weight=ft.FontWeight.W_400, visible=False)
VALOR_CABO_CIRCULAR = ft.Text("95.00 mm²", size=20, weight=ft.FontWeight.W_500, visible=False)

TITULO_LUVA = ft.Text("Luva", size=13, weight=ft.FontWeight.W_400, visible=False)
ICONE_PERGUNTA_LUVA = ft.Icon(ft.Icons.HELP_OUTLINE, color="#888888", size=18, tooltip="Diâmetro: 17.00 mm", visible=False)
VALOR_LUVA = ft.Text("226.98 mm²", size=20, weight=ft.FontWeight.W_500, visible=False)

TEXTO_INDICADORES = ft.Text("Indicadores", size=20, weight=ft.FontWeight.W_500, visible=False)

TITULO_FIOS = ft.Text("Fios", size=13, weight=ft.FontWeight.W_400, visible=False)
VALOR_INDICADOR_FIOS = ft.Text("10/10", size=20, weight=ft.FontWeight.W_500, visible=False)

TITULO_OCUPACAO = ft.Text("Ocupação", size=13, weight=ft.FontWeight.W_400, visible=False)
VALOR_INDICADOR_OCUPACAO = ft.Text("46.40%", size=20, weight=ft.FontWeight.W_500, visible=False)
ICONE_DESVIO_OCUPACAO = ft.Icon(ft.CupertinoIcons.ARROW_RIGHT, size=10, color=ft.Colors.GREEN_200, visible=False)
VALOR_DESVIO_OCUPACAO = ft.Text("0.00%", size=10, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_200, visible=False)
CONTAINER_DESVIO_OCUPACAO = ft.Container(
    width=70,
    height=20,
    visible=False,
    border_radius=20,
    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.GREEN_500),
    content=ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ICONE_DESVIO_OCUPACAO,
            VALOR_DESVIO_OCUPACAO
        ]
    )
)

TITULO_AREA_TOTAL = ft.Text("Área Total", size=13, weight=ft.FontWeight.W_400, visible=False)
VALOR_AREA_TOTAL = ft.Text("163.81 mm²", size=20, weight=ft.FontWeight.W_500, visible=False)


TEXTO_VALIDACAO_SIMULACAO = ft.Text("Validação da Simulação", size=13, weight=ft.FontWeight.W_400, color=ft.Colors.GREEN_300, visible=False)
CONTAINER_VALIDACAO_SIMULACAO = ft.Container(
    height=20,
    bgcolor=ft.Colors.with_opacity(0.2,ft.Colors.GREEN_500),
    border_radius=10,
    visible=False,
    padding=10,
    content=ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            TEXTO_VALIDACAO_SIMULACAO, ft.Container()
        ]
    )
)

TITULO_LOGS_SIMULACAO = ft.Text("Logs da Simulação", size=16, weight=ft.FontWeight.W_500, visible=False)
LOG_LIMPANDO_SIMULACAO_ANTERIOR = ft.Text("Limpando simulação anterior...", size=11, weight=ft.FontWeight.W_300, visible=False)
LOG_FASE_1 = ft.Text("Fase 1: Selecionando Luva... (0.04s)", size=11, weight=ft.FontWeight.W_300, visible=False)
LOG_FASE_2 = ft.Text("Fase 2: Posicionando Fio Retangular... (1.04s)", size=11, weight=ft.FontWeight.W_300, visible=False)
LOG_FASE_3 = ft.Text("Fase 3: Posicionando Cabo Circular... (0.06s)", size=11, weight=ft.FontWeight.W_300, visible=False)
LOG_CONCLUSAO_SIMULACAO = ft.Text("Simulação concluída! (Total: 1.14s)", size=11, weight=ft.FontWeight.W_300, visible=False)

BOTAO_BAIXAR_RELATORIO = ft.ElevatedButton(text="Baixar Relatório", width=150, bgcolor=ft.Colors.RED, height=26, icon=ft.Icons.FILE_OPEN, visible=False)

IMAGEM_SIMULACAO = ft.Image(visible=False, fit=ft.ImageFit.CONTAIN, expand=True)

TITULO_DESENVOLVEDOR = ft.Text("Desenvolvedor", size=14, weight=ft.FontWeight.W_400)
VALOR_DESENVOLVEDOR = ft.Text("DELLAZARIG - Parte Ativa Gravataí", size=14, weight=ft.FontWeight.W_500)