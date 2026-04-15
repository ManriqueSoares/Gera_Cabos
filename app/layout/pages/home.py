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
                    width=270,
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
                                height=200,
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
                                content=None
                            ),
                            ## BOTTOM
                            ft.Container(
                                width=True,
                                padding=5,
                                height=80,
                                #bgcolor="blue",
                                content=ft.Column(
                                    alignment=ft.MainAxisAlignment.END,
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                    controls=[
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