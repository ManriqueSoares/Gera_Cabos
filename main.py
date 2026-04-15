import flet as ft
from app.layout.raiz import raiz
from app.layout.pages.home import Home

def main(page: ft.Page):

    home_page = Home(page)
    raiz.controls.append(home_page)

    page.title = "Gerar Cabos"
    page.window.width = 1100
    page.window.height = 700
    page.padding = 0
    page.theme_mode = "dark"
    page.add(
        ft.Container(
            expand=True,
            content=raiz
        )
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)