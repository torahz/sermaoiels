import re
import PySimpleGUI as sg
from bs4 import BeautifulSoup
from datetime import datetime

# --- calendário litúrgico 2025 ---
liturgico_2025 = {
    "05/01/2025": "Epifania - 2º Domingo",
    "12/01/2025": "Epifania - 3º Domingo",
    "19/01/2025": "Epifania - 4º Domingo",
    "26/01/2025": "Epifania - 5º Domingo",
    "02/03/2025": "Quaresma - 1º Domingo",
    "09/03/2025": "Quaresma - 2º Domingo",
    "16/03/2025": "Quaresma - 3º Domingo",
    "23/03/2025": "Quaresma - 4º Domingo",
    "30/03/2025": "Quaresma - 5º Domingo",
    "20/04/2025": "Páscoa - 1º Domingo",
    "27/04/2025": "Páscoa - 2º Domingo",
    "04/05/2025": "Páscoa - 3º Domingo",
    "11/05/2025": "Páscoa - 4º Domingo",
    "18/05/2025": "Páscoa - 5º Domingo",
    "25/05/2025": "Páscoa - 6º Domingo",
    "01/06/2025": "Páscoa - 7º Domingo",
    "08/06/2025": "Pentecostes",
    "15/06/2025": "Tempo Comum - 1º Domingo após Pentecostes",
    "22/06/2025": "Tempo Comum - 2º Domingo após Pentecostes",
    "29/06/2025": "Tempo Comum - 3º Domingo após Pentecostes",
    "06/07/2025": "Tempo Comum - 4º Domingo após Pentecostes",
    "13/07/2025": "Tempo Comum - 5º Domingo após Pentecostes",
    "20/07/2025": "Tempo Comum - 6º Domingo após Pentecostes",
    "27/07/2025": "Tempo Comum - 7º Domingo após Pentecostes",
    "03/08/2025": "Tempo Comum - 8º Domingo após Pentecostes",
    "10/08/2025": "Tempo Comum - 9º Domingo após Pentecostes",
    "17/08/2025": "Tempo Comum - 10º Domingo após Pentecostes",
    "24/08/2025": "Tempo Comum - 11º Domingo após Pentecostes",
    "31/08/2025": "Tempo Comum - 12º Domingo após Pentecostes",
    "07/09/2025": "Tempo Comum - 13º Domingo após Pentecostes",
    "14/09/2025": "Tempo Comum - 14º Domingo após Pentecostes",
    "21/09/2025": "Tempo Comum - 15º Domingo após Pentecostes",
    "28/09/2025": "Tempo Comum - 16º Domingo após Pentecostes",
    "05/10/2025": "Tempo Comum - 17º Domingo após Pentecostes",
    "12/10/2025": "Tempo Comum - 18º Domingo após Pentecostes",
    "19/10/2025": "Tempo Comum - 19º Domingo após Pentecostes",
    "26/10/2025": "Tempo Comum - 20º Domingo após Pentecostes",
    "02/11/2025": "Tempo Comum - 21º Domingo após Pentecostes",
    "09/11/2025": "Tempo Comum - 22º Domingo após Pentecostes",
    "16/11/2025": "Tempo Comum - 23º Domingo após Pentecostes",
    "23/11/2025": "Tempo Comum - 24º Domingo após Pentecostes",
    "30/11/2025": "Advento - 1º Domingo",
    "07/12/2025": "Advento - 2º Domingo",
    "14/12/2025": "Advento - 3º Domingo",
    "21/12/2025": "Advento - 4º Domingo",
    "28/12/2025": "Natal - 1º Domingo",
}

# --- função para adicionar sermão ---
def adicionar_sermao(preletor, data_str, serie, titulo, link):
    try:
        data = datetime.strptime(data_str, "%d/%m/%Y").strftime("%d/%m/%Y")
    except ValueError:
        return False, "Data inválida! Use o formato dd/mm/yyyy."

    if data not in liturgico_2025:
        return False, f"⚠️ Data {data} não encontrada no calendário litúrgico 2025!"

    domingo = liturgico_2025[data]

    # abrir index.html
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except FileNotFoundError:
        return False, "Arquivo index.html não encontrado na pasta do programa!"

    # verificar se o preletor já está no dropdown
    preletor_select = soup.find("select", {"id": "filterPreletor"})
    if preletor_select:
        options = [opt.text for opt in preletor_select.find_all("option")]
        if preletor not in options:
            new_option = soup.new_tag("option", value=preletor)
            new_option.string = preletor
            preletor_select.append(new_option)

    # localizar a seção correta pelo nome da estação
    estacao = domingo.split(" - ")[0].lower()
    section = soup.find("section", {"class": estacao})
    if not section:
        return False, f"Seção {estacao} não encontrada no index.html."

    grid = section.find("div", {"class": "grid"})
    if not grid:
        return False, f"Grid não encontrada na seção {estacao}."

    # criar novo card
    new_day = soup.new_tag("div", **{"class": "day"})
    info = soup.new_tag("div", **{"class": "info"})
    info.string = f"{data.split('/')[1]}/{data.split('/')[2]} - {domingo}"
    new_day.append(info)

    link_tag = soup.new_tag("a", href=link)
    link_tag.string = f"Série \"{serie}\" - {titulo} - {preletor}"
    new_day.append(link_tag)

    grid.append(new_day)

    # salvar alterações
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(str(soup.prettify()))

    return True, f"Sermão de {preletor} adicionado em {domingo} ({data})!"

# --- interface gráfica ---
sg.theme("DarkBlue3")

layout = [
    [sg.Text("Nome do Preletor"), sg.Input(key="preletor")],
    [sg.Text("Data (dd/mm/yyyy)"), sg.Input(key="data")],
    [sg.Text("Série"), sg.Input(key="serie")],
    [sg.Text("Nome do Sermão"), sg.Input(key="titulo")],
    [sg.Text("Link do Drive"), sg.Input(key="link")],
    [sg.Button("Salvar", size=(10,1), button_color=("white", "#3C667F")), sg.Button("Cancelar")]
]

window = sg.Window("Cadastro de Sermões - Esperança", layout, finalize=True)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Cancelar"):
        break
    if event == "Salvar":
        ok, msg = adicionar_sermao(
            values["preletor"].strip(),
            values["data"].strip(),
            values["serie"].strip(),
            values["titulo"].strip(),
            values["link"].strip()
        )
        if ok:
            sg.popup("✅ Sucesso", msg)
        else:
            sg.popup_error("❌ Erro", msg)

window.close()