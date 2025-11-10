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
   # === Epifania ===
    "05/01/2025": "Epifania - 1º Domingo após Epifania",
    "12/01/2025": "Epifania - 2º Domingo após Epifania",
    "19/01/2025": "Epifania - 3º Domingo após Epifania",
    "26/01/2025": "Epifania - 4º Domingo após Epifania",
    "02/02/2025": "Epifania - 5º Domingo após Epifania",
    "09/02/2025": "Epifania - 6º Domingo após Epifania",
    "16/02/2025": "Epifania - 7º Domingo após Epifania",
    "23/02/2025": "Epifania - 8º Domingo após Epifania",

    # === Quaresma ===
    "02/03/2025": "Quaresma - 1º Domingo da Quaresma",
    "09/03/2025": "Quaresma - 2º Domingo da Quaresma",
    "16/03/2025": "Quaresma - 3º Domingo da Quaresma",
    "23/03/2025": "Quaresma - 4º Domingo da Quaresma",
    "30/03/2025": "Quaresma - 5º Domingo da Quaresma",
    "06/04/2025": "Quaresma - Domingo da Paixão",
    "13/04/2025": "Quaresma - Domingo de Ramos",

    # === Páscoa ===
    "20/04/2025": "Páscoa - Domingo da Ressurreição",
    "27/04/2025": "Páscoa - 2º Domingo da Páscoa",
    "04/05/2025": "Páscoa - 3º Domingo da Páscoa",
    "11/05/2025": "Páscoa - 4º Domingo da Páscoa",
    "18/05/2025": "Páscoa - 5º Domingo da Páscoa",
    "25/05/2025": "Páscoa - 6º Domingo da Páscoa",
    "01/06/2025": "Páscoa - 7º Domingo da Páscoa",

    # === Pentecostes ===
    "08/06/2025": "Pentecostes",

    # === Tempo Comum ===
    "15/06/2025": "Tempo Comum - 2º Domingo após Pentecostes",
    "22/06/2025": "Tempo Comum - 3º Domingo após Pentecostes",
    "29/06/2025": "Tempo Comum - 4º Domingo após Pentecostes",
    "06/07/2025": "Tempo Comum - 5º Domingo após Pentecostes",
    "13/07/2025": "Tempo Comum - 6º Domingo após Pentecostes",
    "20/07/2025": "Tempo Comum - 7º Domingo após Pentecostes",
    "27/07/2025": "Tempo Comum - 8º Domingo após Pentecostes",
    "03/08/2025": "Tempo Comum - 9º Domingo após Pentecostes",
    "10/08/2025": "Tempo Comum - 10º Domingo após Pentecostes",
    "17/08/2025": "Tempo Comum - 11º Domingo após Pentecostes",
    "24/08/2025": "Tempo Comum - 12º Domingo após Pentecostes",
    "31/08/2025": "Tempo Comum - 13º Domingo após Pentecostes",
    "07/09/2025": "Tempo Comum - 14º Domingo após Pentecostes",
    "14/09/2025": "Tempo Comum - 15º Domingo após Pentecostes",
    "21/09/2025": "Tempo Comum - 16º Domingo após Pentecostes",
    "28/09/2025": "Tempo Comum - 17º Domingo após Pentecostes",
    "05/10/2025": "Tempo Comum - 18º Domingo após Pentecostes",
    "12/10/2025": "Tempo Comum - 19º Domingo após Pentecostes",
    "19/10/2025": "Tempo Comum - 20º Domingo após Pentecostes",
    "26/10/2025": "Tempo Comum - 21º Domingo após Pentecostes",
    "02/11/2025": "Tempo Comum - 22º Domingo após Pentecostes",
    "09/11/2025": "Tempo Comum - 23º Domingo após Pentecostes",
    "16/11/2025": "Tempo Comum - 24º Domingo após Pentecostes",
    "23/11/2025": "Tempo Comum - 25º Domingo após Pentecostes",
    "30/11/2025": "Tempo Comum - Domingo de Cristo Rei",

    # === Advento ===
    "30/11/2025": "Advento - 1º Domingo do Advento",
    "07/12/2025": "Advento - 2º Domingo do Advento",
    "14/12/2025": "Advento - 3º Domingo do Advento",
    "21/12/2025": "Advento - 4º Domingo do Advento",

    # === Natal ===
    "25/12/2025": "Natal do Senhor",
    "28/12/2025": "Natal - 1º Domingo após o Natal",
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

    descricao_completa = calendario[key]
    partes = descricao_completa.split(" - ", 1)
    estacao_slug = slugify(partes[0])
    descricao = partes[1] if len(partes) > 1 else partes[0]

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
