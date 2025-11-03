# integrador.py
from datetime import datetime
from bs4 import BeautifulSoup
import unicodedata
import os

HTML_FILE = "index.html"

def slugify(text: str) -> str:
    nf = unicodedata.normalize("NFD", text)
    no_accents = "".join(ch for ch in nf if unicodedata.category(ch) != "Mn")
    return no_accents.strip().lower().replace(" ", "-")

MESES_PT = [
    "janeiro","fevereiro","março","abril","maio","junho",
    "julho","agosto","setembro","outubro","novembro","dezembro"
]

# calendário (mantido igual)
calendario = {
    "05/01/2025": ("1º Domingo após o Natal", "natal"),
    "12/01/2025": ("1º Domingo após a Epifania", "epifania"),
    "19/01/2025": ("2º Domingo após a Epifania", "epifania"),
    "26/01/2025": ("3º Domingo após a Epifania", "epifania"),
    "02/02/2025": ("4º Domingo após a Epifania", "epifania"),
    "09/02/2025": ("5º Domingo após a Epifania", "epifania"),
    "16/02/2025": ("6º Domingo após a Epifania", "epifania"),
    "23/02/2025": ("7º Domingo após a Epifania", "epifania"),
    "02/03/2025": ("Domingo da Transfiguração do Senhor", "epifania"),
    "09/03/2025": ("1º Domingo da Quaresma", "quaresma"),
    "16/03/2025": ("2º Domingo da Quaresma", "quaresma"),
    "23/03/2025": ("3º Domingo da Quaresma", "quaresma"),
    "30/03/2025": ("4º Domingo da Quaresma", "quaresma"),
    "06/04/2025": ("5º Domingo da Quaresma", "quaresma"),
    "13/04/2025": ("Domingo de Ramos", "quaresma"),
    "20/04/2025": ("Domingo da Ressurreição", "pascoa"),
    "27/04/2025": ("2º Domingo de Páscoa", "pascoa"),
    "04/05/2025": ("3º Domingo de Páscoa", "pascoa"),
    "11/05/2025": ("4º Domingo de Páscoa", "pascoa"),
    "18/05/2025": ("5º Domingo de Páscoa", "pascoa"),
    "25/05/2025": ("6º Domingo de Páscoa", "pascoa"),
    "01/06/2025": ("7º Domingo de Páscoa", "pascoa"),
    "08/06/2025": ("Domingo de Pentecostes", "pentecostes"),
    "15/06/2025": ("1º Domingo após Pentecostes", "tempo-comum"),
    "22/06/2025": ("2º Domingo após Pentecostes", "tempo-comum"),
    "29/06/2025": ("3º Domingo após Pentecostes", "tempo-comum"),
    "06/07/2025": ("4º Domingo após Pentecostes", "tempo-comum"),
    "13/07/2025": ("5º Domingo após Pentecostes", "tempo-comum"),
    "20/07/2025": ("6º Domingo após Pentecostes", "tempo-comum"),
    "27/07/2025": ("7º Domingo após Pentecostes", "tempo-comum"),
    "03/08/2025": ("8º Domingo após Pentecostes", "tempo-comum"),
    "10/08/2025": ("9º Domingo após Pentecostes", "tempo-comum"),
    "17/08/2025": ("10º Domingo após Pentecostes", "tempo-comum"),
    "24/08/2025": ("11º Domingo após Pentecostes", "tempo-comum"),
    "31/08/2025": ("12º Domingo após Pentecostes", "tempo-comum"),
    "07/09/2025": ("1º Domingo da Criação", "criacao"),
    "14/09/2025": ("2º Domingo da Criação", "criacao"),
    "21/09/2025": ("3º Domingo da Criação", "criacao"),
    "28/09/2025": ("4º Domingo da Criação", "criacao"),
    "05/10/2025": ("13º Domingo após Pentecostes", "tempo-comum"),
    "12/10/2025": ("14º Domingo após Pentecostes", "tempo-comum"),
    "19/10/2025": ("15º Domingo após Pentecostes", "tempo-comum"),
    "26/10/2025": ("16º Domingo após Pentecostes (Reforma Protestante)", "tempo-comum"),
    "02/11/2025": ("17º Domingo após Pentecostes", "tempo-comum"),
    "09/11/2025": ("18º Domingo após Pentecostes", "tempo-comum"),
    "16/11/2025": ("19º Domingo após Pentecostes", "tempo-comum"),
    "23/11/2025": ("Domingo de Cristo Rei", "tempo-comum"),
    "30/11/2025": ("1º Domingo do Advento", "advento"),
    "07/12/2025": ("2º Domingo do Advento", "advento"),
    "14/12/2025": ("3º Domingo do Advento", "advento"),
    "21/12/2025": ("Culto de Natal", "natal"),
    "28/12/2025": ("1º Domingo após o Natal", "natal")
}

def parse_date_from_card(card):
    if card.has_attr("data-date"):
        try:
            return datetime.strptime(card["data-date"], "%Y-%m-%d")
        except:
            pass
    date_div = card.find("div", {"class": "date"})
    if date_div:
        try:
            return datetime.strptime(date_div.text.strip(), "%d/%m/%Y")
        except:
            pass
    return None

def ordenar_grid_python(grid_tag):
    cards = grid_tag.find_all("div", {"class": "day"})
    parsed = []
    for c in cards:
        dt = parse_date_from_card(c)
        parsed.append((c, dt if dt else datetime.min))
    parsed.sort(key=lambda x: x[1], reverse=True)
    for card, _ in parsed:
        grid_tag.append(card)

def adicionar_sermao():
    preletor = input("Nome do Preletor: ").strip()
    data_str = input("Data (dd/mm/yyyy): ").strip()
    serie = input("Série: ").strip()
    titulo = input("Nome do sermão: ").strip()
    link = input("Link do Drive: ").strip()

    try:
        data_dt = datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        print("Data inválida. Use dd/mm/yyyy")
        return

    key = data_dt.strftime("%d/%m/%Y")
    if key not in calendario:
        print("Data não mapeada no calendário litúrgico 2025.")
        return

    descricao, estacao_slug = calendario[key]

    if not os.path.isfile(HTML_FILE):
        print("index.html não encontrado.")
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    main = soup.find("main")
    if not main:
        print("<main> não encontrado no index.html")
        return

    secao = None
    for s in soup.find_all("section"):
        classes = s.get("class", []) or []
        if estacao_slug in classes:
            secao = s
            break

    if not secao:
        secao = soup.new_tag("section")
        secao["class"] = ["season", estacao_slug]
        h2 = soup.new_tag("h2")
        display_name = "Criação" if estacao_slug == "criacao" else estacao_slug.replace("-", " ").capitalize()
        h2.string = display_name
        secao.append(h2)
        grid = soup.new_tag("div"); grid["class"] = "grid"
        secao.append(grid)
        main.append(secao)
    else:
        grid = secao.find("div", {"class": "grid"})
        if not grid:
            grid = soup.new_tag("div"); grid["class"] = "grid"; secao.append(grid)

    novo = soup.new_tag("div"); novo["class"] = "day"
    novo["data-date"] = data_dt.strftime("%Y-%m-%d")

    info = soup.new_tag("div"); info["class"] = "info"
    date_span = soup.new_tag("div"); date_span["class"] = "date"; date_span.string = data_dt.strftime("%d/%m/%Y")
    label_span = soup.new_tag("div"); label_span["class"] = "label"; label_span.string = descricao
    info.append(date_span); info.append(label_span)
    novo.append(info)

    a = soup.new_tag("a", href=link, target="_blank", rel="noopener"); a["class"] = "link"
    a.string = f'Série "{serie}" - {titulo} - {preletor}'
    novo.append(a)

    grid.append(novo)
    ordenar_grid_python(grid)

    select = soup.find("select", {"id": "filterPreletor"})
    if select:
        existing = [ (opt.get("value") or opt.text or "").strip() for opt in select.find_all("option") ]
        if not any(existing_val.lower() == preletor.lower() for existing_val in existing if existing_val):
            opt = soup.new_tag("option", value=preletor)
            opt.string = preletor
            select.append(opt)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup.prettify(formatter="html")))

    print("✅ Sermão adicionado e ordenado com sucesso.")

if __name__ == "__main__":
    adicionar_sermao()