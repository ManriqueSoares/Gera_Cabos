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
                    bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLUE_GREY_100),
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
                                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                                        ft.Container(height=10),
                                        FIO_RETANGULAR_TITLE,
                                        ENTRADA_TEXT_AXIAL,
                                        ENTRADA_TEXT_RADIAL,
                                        ENTRADA_TEXT_QUANTIDADE,
                                        ft.Container(height=10),    
                                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                                        ft.Container(height=10),
                                        CABO_CIRCULAR_TITLE,
                                        ft.Container(padding=ft.padding.only(left=60), alignment=ft.alignment.center, content=CHECK_BOX_EXCLUIR_CABO_CIRCULAR,),
                                        ft.Container(height=10),    
                                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                                        ft.Container(height=10),
                                        DROPDOWN_SECAO_NOMINAL_CABO,
                                        ENTRADA_SECAO_PERSONALIZADA_CABO,
                                        ft.Container(height=10),    
                                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                                        ft.Container(height=10),
                                        TEXT_DIAMETRO,
                                        ft.Container(height=10),    
                                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                                        ft.Container(height=10),
                                        ft.Row(spacing=1, alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                                            ENTRADA_TEXT_GRANULARIDADE,
                                            ICONE_PERGUNTA_GRANULARIDADE,
                                        ]),
                                        SLIDER_GRANULARIDADE,
                                        ft.Container(height=10),    
                                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                                        ft.Container(height=10),
                                        ft.Row(alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                                            TITULO_CONFIGURACOES,
                                            ICONE_PERGUNTA_CONFIGURACOES,
                                        ]),
                                        ENTRADA_LIMITE_CONFIGURACAO,
                                        SLIDER_LIMITE_OCUPACAO,
                                        ft.Container(height=10),    
                                        ft.Divider(height=1, color=ft.Colors.GREY_200),
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
                    content=None
                )
            ]
        )