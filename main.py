import flet as ft

from app.layout.pages.home import Home
from app.layout.raiz import raiz


def main(page: ft.Page) -> None:
    page.title = "Gerar Cabos"
    page.window.width = 1100
    page.window.height = 700
    page.window.min_width = 900
    page.window.min_height = 600
    page.padding = 0
    page.theme_mode = "dark"

    home_page = Home(page)
    raiz.controls.append(home_page)

    page.add(ft.Container(expand=True, content=raiz))
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
