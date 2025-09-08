# integrador.py (corrigido)
from datetime import datetime
from bs4 import BeautifulSoup
import unicodedata
import sys

# ---------- utilitários ----------
def slugify(text: str) -> str:
    # remove acentos e transforma em slug (lower + '-' por espaços)
    nf = unicodedata.normalize("NFD", text)
    no_accents = "".join(ch for ch in nf if unicodedata.category(ch) != "Mn")
    return no_accents.strip().lower().replace(" ", "-")

# meses em português
MESES_PT = [
    "janeiro","fevereiro","março","abril","maio","junho",
    "julho","agosto","setembro","outubro","novembro","dezembro"
]

# ==============================
# Calendário litúrgico 2025 (ajustado: setembro = estação 'Criacao')
# ==============================
calendario = {
    # Epifania
    "05/01/2025": "Epifania - 1º Domingo após Epifania",
    "12/01/2025": "Epifania - 2º Domingo após Epifania",
    "19/01/2025": "Epifania - 3º Domingo após Epifania",
    "26/01/2025": "Epifania - 4º Domingo após Epifania",
    "02/02/2025": "Epifania - 5º Domingo após Epifania",
    "09/02/2025": "Epifania - 6º Domingo após Epifania",
    "16/02/2025": "Epifania - 7º Domingo após Epifania",
    "23/02/2025": "Epifania - 8º Domingo após Epifania",

    # Quaresma / Semana Santa
    "02/03/2025": "Quaresma - 1º Domingo da Quaresma",
    "09/03/2025": "Quaresma - 2º Domingo da Quaresma",
    "16/03/2025": "Quaresma - 3º Domingo da Quaresma",
    "23/03/2025": "Quaresma - 4º Domingo da Quaresma",
    "30/03/2025": "Quaresma - 5º Domingo da Quaresma",
    "06/04/2025": "Quaresma - Domingo da Paixão",
    "13/04/2025": "Quaresma - Domingo de Ramos",

    # Páscoa
    "20/04/2025": "Páscoa - Domingo da Ressurreição",
    "27/04/2025": "Páscoa - 2º Domingo da Páscoa",
    "04/05/2025": "Páscoa - 3º Domingo da Páscoa",
    "11/05/2025": "Páscoa - 4º Domingo da Páscoa",
    "18/05/2025": "Páscoa - 5º Domingo da Páscoa",
    "25/05/2025": "Páscoa - 6º Domingo da Páscoa",
    "01/06/2025": "Páscoa - 7º Domingo da Páscoa",

    # Pentecostes
    "08/06/2025": "Pentecostes",

    # Tempo Comum (início após Pentecostes)
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

    # === CRIAÇÃO (ajustado conforme sua solicitação) ===
    "07/09/2025": "Criacao - 1º Domingo da Criação",
    "14/09/2025": "Criacao - 2º Domingo da Criação",
    "21/09/2025": "Criacao - 3º Domingo da Criação",
    "28/09/2025": "Criacao - 4º Domingo da Criação",

    # volta ao Tempo Comum após o ciclo da Criação (ex.: outubro em diante)
    "05/10/2025": "Tempo Comum - 11º Domingo após Pentecostes",
    "12/10/2025": "Tempo Comum - 12º Domingo após Pentecostes",
    "19/10/2025": "Tempo Comum - 13º Domingo após Pentecostes",
    "26/10/2025": "Tempo Comum - 14º Domingo após Pentecostes",
    "02/11/2025": "Tempo Comum - 15º Domingo após Pentecostes",
    "09/11/2025": "Tempo Comum - 16º Domingo após Pentecostes",
    "16/11/2025": "Tempo Comum - 17º Domingo após Pentecostes",
    "23/11/2025": "Tempo Comum - 18º Domingo após Pentecostes",
    "30/11/2025": "Tempo Comum - Domingo de Cristo Rei",

    # Advento / Natal
    "30/11/2025": "Advento - 1º Domingo do Advento",
    "07/12/2025": "Advento - 2º Domingo do Advento",
    "14/12/2025": "Advento - 3º Domingo do Advento",
    "21/12/2025": "Advento - 4º Domingo do Advento",
    "25/12/2025": "Natal do Senhor",
    "28/12/2025": "Natal - 1º Domingo após o Natal",
}

# ==============================
# Função principal de inserção
# ==============================
def adicionar_sermao():
    print("=== Cadastro de Sermão ===")
    preletor = input("Nome do Preletor: ").strip()
    data_str = input("Data (dd/mm/yyyy): ").strip()
    serie = input("Série: ").strip()
    titulo = input("Nome do sermão: ").strip()
    link = input("Link do Drive: ").strip()

    # converter data
    try:
        data = datetime.strptime(data_str, "%d/%m/%Y")
        data_fmt = data.strftime("%d/%m/%Y")
    except ValueError:
        print("⚠️ Data inválida! Use o formato dd/mm/yyyy.")
        return

    if data_fmt not in calendario:
        print("⚠️ Data não encontrada no calendário litúrgico 2025!")
        return

    descricao = calendario[data_fmt]  # ex: "Criacao - 1º Domingo da Criação"
    partes = descricao.split(" - ", 1)
    estacao_nome = partes[0]  # ex: "Criacao"
    detalhe_domingo = partes[1] if len(partes) > 1 else ""

    # abre index.html
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except FileNotFoundError:
        print("⚠️ index.html não encontrado na pasta atual.")
        return

    main = soup.find("main")
    if not main:
        print("⚠️ Estrutura inválida: <main> não encontrado no index.html")
        return

    # monta o novo card
    novo_card = soup.new_tag("div", **{"class": "day"})
    # mês em pt
    mes_pt = MESES_PT[data.month - 1].capitalize()
    info = soup.new_tag("div", **{"class": "info"})
    info.string = f"{mes_pt} - {detalhe_domingo}"
    novo_card.append(info)

    link_tag = soup.new_tag("a", href=link, **{"class": "link", "target": "_blank", "rel":"noopener"})
    link_tag.string = f"Série \"{serie}\" - {titulo} - {preletor}"
    novo_card.append(link_tag)

    # encontra seção pela classe slugificada
    classe_secao = slugify(estacao_nome)
    secao = main.find("section", {"class": classe_secao})
    if not secao:
        # cria seção se não existir (usa estacao_nome sem acento no class, titulo com espaços bonitos)
        secao = soup.new_tag("section", **{"class": classe_secao})
        h2 = soup.new_tag("h2")
        # título humano: tenta usar estacao_nome com acento se for 'Criacao' -> 'Criação'
        titulo_secao = estacao_nome
        # se for Criacao, mostrar 'Criação' com acento
        if estacao_nome.lower().startswith("criacao"):
            h2.string = "Criação"
        else:
            h2.string = estacao_nome.replace("-", " ").capitalize()
        secao.append(h2)
        grid = soup.new_tag("div", **{"class": "grid"})
        secao.append(grid)
        main.append(secao)
    else:
        grid = secao.find("div", {"class": "grid"})
        if not grid:
            grid = soup.new_tag("div", **{"class": "grid"})
            secao.append(grid)

    # insere o card
    grid.append(novo_card)

    # atualiza dropdown de preletores
    select_preletor = soup.find("select", {"id": "filterPreletor"})
    if select_preletor:
        valores = [opt.get("value") for opt in select_preletor.find_all("option")]
        # comparar sem diferença de case
        if preletor not in valores and preletor not in [v for v in valores]:
            nova_opt = soup.new_tag("option", value=preletor)
            nova_opt.string = preletor
            select_preletor.append(nova_opt)

    # salva
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(str(soup.prettify(formatter="html")))

    print(f"✅ Sermão adicionado: {estacao_nome} - {detalhe_domingo} ({data_fmt})")

if __name__ == "__main__":
    adicionar_sermao()