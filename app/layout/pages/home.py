import flet as ft
from app.layout.widgets.widgets import *

class Home(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
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
                                padding=ft.padding.only(
                                    top=10, right=5, left=5
                                ),
                                #bgcolor="red",
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
                                                controls=[
                                                    LOGO_WEG,
                                                    BOTAO_CLOSE_SIDBAR
                                                ]
                                            )
                                        ),
                                    ]
                                )
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
                                        ft.Divider(height=1, color=ft.Colors.GREY_900),
                                        ft.Container(height=10),
                                        FIO_RETANGULAR_TITLE,
                                        ENTRADA_TEXT_AXIAL,
                                        ENTRADA_TEXT_RADIAL,
                                        ENTRADA_TEXT_QUANTIDADE,
                                        ft.Container(height=10),    
                                        ft.Divider(height=1, color=ft.Colors.GREY_900),
                                        ft.Container(height=10),
                                        CABO_CIRCULAR_TITLE,
                                        ft.Container(padding=ft.padding.only(left=60), alignment=ft.alignment.center, content=CHECK_BOX_EXCLUIR_CABO_CIRCULAR,),
                                        ft.Container(height=10),    
                                        ft.Divider(height=1, color=ft.Colors.GREY_900),
                                        ft.Container(height=10),
                                        DROPDOWN_SECAO_NOMINAL_CABO,
                                        ENTRADA_SECAO_PERSONALIZADA_CABO,
                                        ft.Container(height=10),    
                                        ft.Divider(height=1, color=ft.Colors.GREY_900),
                                        ft.Container(height=10),
                                        TEXT_DIAMETRO,
                                        ft.Container(height=10),    
                                        ft.Divider(height=1, color=ft.Colors.GREY_900),
                                        ft.Container(height=10),
                                        ft.Row(spacing=1, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                                            ENTRADA_TEXT_GRANULARIDADE,
                                            ICONE_PERGUNTA_GRANULARIDADE,
                                        ]),
                                        SLIDER_GRANULARIDADE,
                                        ft.Container(height=10),    
                                        ft.Divider(height=1, color=ft.Colors.GREY_900),
                                        ft.Container(height=10),
                                        ft.Row(alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                                            TITULO_CONFIGURACOES,
                                            ICONE_PERGUNTA_CONFIGURACOES,
                                        ]),
                                        ENTRADA_LIMITE_CONFIGURACAO,
                                        SLIDER_LIMITE_OCUPACAO,
                                        ft.Container(height=10),    
                                        ft.Divider(height=1, color=ft.Colors.GREY_900),
                                        ft.Container(height=10),
                                    ]
                                )
                            ),
                            ## BOTTOM
                            ft.Container(
                                width=True,
                                padding=5,
                                height=100,
                                #bgcolor="blue",
                                content=ft.Column(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            vertical_alignment=ft.CrossAxisAlignment.START,
                                            controls=[
                                                ELEVATE_BUTTON_EXECUTAR_SIMULACAO
                                            ]
                                        ),
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.END,
                                            vertical_alignment=ft.CrossAxisAlignment.END,
                                            controls=[
                                                BOTAO_ALTERAR_TEMA
                                            ]
                                        )
                                    ]
                                )
                            )
                        ]
                    )
                ),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=True,
                                height=120,
                                padding=ft.padding.only(
                                    top=50, right=10, left=10
                                ),
                                #bgcolor="red",
                                content=ft.Column(
                                    width=True,
                                    height=50,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Row(alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                                            TITULO_JANELA_PRINCIPAL
                                        ]),
                                        ft.Row(alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                                            DESCRICAO_APP
                                        ])
                                    ]
                                )
                            ),
                            ft.Container(height=20),
                            ## Progress Bar
                            ft.Container(
                                width=True,
                                height=50,
                                alignment=ft.alignment.center,
                                padding=ft.padding.only(right=30, left=30),
                                content=PROGRESS_BAR_SIMULACAO
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
                                                        #bgcolor="red",
                                                        content=ft.Column(
                                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                            controls=[
                                                                ft.Container(
                                                                    width=True,
                                                                    height=50,
                                                                    padding=ft.padding.only(left=5),
                                                                    alignment=ft.alignment.center_left,
                                                                    content=TEXT_DADOS_DAS_SECOES
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
                                                                                            controls=[TITULO_FIO_RETANGULAR, ICONE_PERGUNTA_FIO_RETANGULAR]),
                                                                                        VALOR_FIO_RETANGULAR
                                                                                    ]
                                                                                )
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
                                                                                        VALOR_CABO_CIRCULAR
                                                                                    ]
                                                                                )
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
                                                                                            controls=[TITULO_LUVA, ICONE_PERGUNTA_LUVA]),
                                                                                        VALOR_LUVA
                                                                                    ]
                                                                                )
                                                                            )
                                                                        ]
                                                                    )
                                                                )
                                                            ]
                                                        )
                                                    ),
                                                    ft.Divider(height=1, color=ft.Colors.GREY_900),
                                                    ## Indicadores
                                                    ft.Container(
                                                        expand=True,
                                                        #bgcolor="blue",
                                                        content=ft.Column(
                                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                            controls=[
                                                                ft.Container(
                                                                    width=True,
                                                                    height=50,
                                                                    padding=ft.padding.only(left=5),
                                                                    alignment=ft.alignment.center_left,
                                                                    content=TEXTO_INDICADORES
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
                                                                                            controls=[TITULO_FIOS]),
                                                                                        VALOR_INDICADOR_FIOS
                                                                                    ]
                                                                                )
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
                                                                                        )
                                                                                    ]
                                                                                )
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
                                                                                            controls=[TITULO_AREA_TOTAL]),
                                                                                        VALOR_AREA_TOTAL
                                                                                    ]
                                                                                )
                                                                            )
                                                                        ]
                                                                    )
                                                                )
                                                            ]
                                                        )
                                                    )
                                                ]
                                            )
                                        ),
                                        ## Container Graph
                                        ft.Container(
                                            width=500,
                                            height=800,
                                            #bgcolor="yellow",
                                            content=None
                                        ),
                                    ]
                                )
                            ),
                            ft.Container(height=20),
                            ## VALIDACAO
                            ft.Container(
                                width=True,
                                height=40,
                                padding=ft.padding.only(right=15, left=15),
                                content=CONTAINER_VALIDACAO_SIMULACAO
                            ),
                            
                            #ft.Divider(height=1, color=ft.Colors.GREY_900),
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
                                                controls=[
                                                    TITULO_LOGS_SIMULACAO
                                                ]
                                            )
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
                                                                content=BOTAO_BAIXAR_RELATORIO
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        )
                                    ]
                                )
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
                                        TITULO_DESENVOLVEDOR, VALOR_DESENVOLVEDOR
                                    ]
                                )
                            )
                        ]
                    )
                )
            ]
        )