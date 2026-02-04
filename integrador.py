from datetime import datetime
from bs4 import BeautifulSoup
import unicodedata
import os

HTML_FILE = "index.html"

# -----------------------------
# Utils
# -----------------------------
def slugify(text: str) -> str:
    nf = unicodedata.normalize("NFD", text)
    no_accents = "".join(ch for ch in nf if unicodedata.category(ch) != "Mn")
    return no_accents.strip().lower().replace(" ", "-")

# -----------------------------
# Calendários Litúrgicos
# -----------------------------
calendarios = {

    # =========================
    # 2025 (inalterado)
    # =========================
    2025: {
        "05/01/2025": "Epifania - 1º Domingo da Epifania",
        "12/01/2025": "Epifania - 2º Domingo da Epifania",
        "19/01/2025": "Epifania - 3º Domingo da Epifania",
        "02/02/2025": "Epifania - 5º Domingo da Epifania",
        "09/02/2025": "Epifania - 6º Domingo da Epifania",

        "09/03/2025": "Quaresma - 1º Domingo da Quaresma",
        "16/03/2025": "Quaresma - 2º Domingo da Quaresma",
        "23/03/2025": "Quaresma - 3º Domingo da Quaresma",
        "30/03/2025": "Quaresma - 4º Domingo da Quaresma",
        "06/04/2025": "Quaresma - 5º Domingo da Quaresma",
        "13/04/2025": "Quaresma - Domingo de Ramos",

        "20/04/2025": "Páscoa - Domingo da Ressurreição",
        "27/04/2025": "Páscoa - 2º Domingo da Páscoa",
        "04/05/2025": "Páscoa - 3º Domingo da Páscoa",
        "11/05/2025": "Páscoa - 4º Domingo da Páscoa",
        "18/05/2025": "Páscoa - 5º Domingo da Páscoa",
        "25/05/2025": "Páscoa - 6º Domingo da Páscoa",
        "01/06/2025": "Páscoa - 7º Domingo da Páscoa",

        "08/06/2025": "Pentecostes",

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
        "23/11/2025": "Tempo Comum - Domingo de Cristo Rei",

        "30/11/2025": "Advento - 1º Domingo do Advento",
        "07/12/2025": "Advento - 2º Domingo do Advento",
        "14/12/2025": "Advento - 3º Domingo do Advento",
        "21/12/2025": "Advento - 4º Domingo do Advento",

        "28/12/2025": "Natal - 1º Domingo após o Natal",
    },

    # =========================
    # 2026 (AGORA CORRETO)
    # =========================
    2026: {

        # EPIFANIA
        "04/01/2026": "Epifania - 1º Domingo da Epifania",
        "11/01/2026": "Epifania - 2º Domingo da Epifania",
        "18/01/2026": "Epifania - 3º Domingo da Epifania",
        "25/01/2026": "Epifania - 4º Domingo da Epifania",
        "01/02/2026": "Epifania - 5º Domingo da Epifania",

        # QUARESMA
        "22/02/2026": "Quaresma - 1º Domingo da Quaresma",
        "01/03/2026": "Quaresma - 2º Domingo da Quaresma",
        "08/03/2026": "Quaresma - 3º Domingo da Quaresma",
        "15/03/2026": "Quaresma - 4º Domingo da Quaresma",
        "22/03/2026": "Quaresma - 5º Domingo da Quaresma",
        "29/03/2026": "Quaresma - Domingo de Ramos",

        # PÁSCOA
        "05/04/2026": "Páscoa - Domingo da Ressurreição",
        "12/04/2026": "Páscoa - 2º Domingo da Páscoa",
        "19/04/2026": "Páscoa - 3º Domingo da Páscoa",
        "26/04/2026": "Páscoa - 4º Domingo da Páscoa",
        "03/05/2026": "Páscoa - 5º Domingo da Páscoa",
        "10/05/2026": "Páscoa - 6º Domingo da Páscoa",
        "17/05/2026": "Páscoa - 7º Domingo da Páscoa",

        # PENTECOSTES
        "24/05/2026": "Pentecostes",

        # TEMPO COMUM
        "31/05/2026": "Tempo Comum - 1º Domingo após Pentecostes",
        "07/06/2026": "Tempo Comum - 2º Domingo após Pentecostes",
        "14/06/2026": "Tempo Comum - 3º Domingo após Pentecostes",
        "21/06/2026": "Tempo Comum - 4º Domingo após Pentecostes",
        "28/06/2026": "Tempo Comum - 5º Domingo após Pentecostes",

        # ADVENTO
        "29/11/2026": "Advento - 1º Domingo do Advento",
        "06/12/2026": "Advento - 2º Domingo do Advento",
        "13/12/2026": "Advento - 3º Domingo do Advento",
        "20/12/2026": "Advento - 4º Domingo do Advento",

        # NATAL
        "27/12/2026": "Natal - 1º Domingo após o Natal",
    }
}

# -----------------------------
# Core (inalterado)
# -----------------------------
def adicionar_sermao():
    preletor = input("Nome do Preletor: ").strip()
    data_str = input("Data (dd/mm/yyyy): ").strip()
    serie = input("Série: ").strip()
    titulo = input("Nome do sermão: ").strip()
    link = input("Link do Drive: ").strip()

    data_dt = datetime.strptime(data_str, "%d/%m/%Y")
    ano = data_dt.year

    if ano not in calendarios:
        print(f"❌ Calendário {ano} não cadastrado.")
        return

    calendario = calendarios[ano]
    key = data_dt.strftime("%d/%m/%Y")

    if key not in calendario:
        print(f"❌ Data não mapeada no calendário litúrgico {ano}.")
        return

    descricao_completa = calendario[key]
    estacao, descricao = descricao_completa.split(" - ", 1)
    estacao_slug = slugify(estacao)

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    main = soup.find("main")

    secao = soup.find("section", class_=estacao_slug)
    if not secao:
        secao = soup.new_tag("section", **{"class": ["season", estacao_slug]})
        h2 = soup.new_tag("h2"); h2.string = estacao
        secao.append(h2)
        grid = soup.new_tag("div", **{"class": "grid"})
        secao.append(grid)
        main.append(secao)
    else:
        grid = secao.find("div", class_="grid")

    card = soup.new_tag("div", **{"class": "day"})
    card["data-date"] = data_dt.strftime("%Y-%m-%d")

    info = soup.new_tag("div", **{"class": "info"})
    d = soup.new_tag("div", **{"class": "date"}); d.string = data_str
    l = soup.new_tag("div", **{"class": "label"}); l.string = descricao
    info.extend([d, l])
    card.append(info)

    a = soup.new_tag("a", href=link, target="_blank", rel="noopener", **{"class": "link"})
    a.string = f'Série "{serie}" - {titulo} - {preletor}'
    card.append(a)

    grid.append(card)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    print("✅ Sermão adicionado com sucesso.")

if __name__ == "__main__":
    adicionar_sermao()