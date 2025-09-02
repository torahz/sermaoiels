from datetime import datetime
from bs4 import BeautifulSoup

# ==============================
# Calendário litúrgico 2025
# ==============================
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

# ==============================
# Entrada de dados
# ==============================
print("=== Cadastro de Sermão ===")
preletor = input("Nome do Preletor: ")
data_str = input("Data (dd/mm/yyyy): ")
serie = input("Série: ")
titulo = input("Nome do sermão: ")
link = input("Link do Drive: ")

# Conversão de data
try:
    data = datetime.strptime(data_str, "%d/%m/%Y")
    data_fmt = data.strftime("%d/%m/%Y")
except ValueError:
    print("⚠️ Data inválida! Use o formato dd/mm/yyyy.")
    exit()

# Buscar no calendário
if data_fmt not in calendario:
    print("⚠️ Data não encontrada no calendário litúrgico 2025!")
    exit()

descricao = calendario[data_fmt]

# ==============================
# Editar o index.html
# ==============================
with open("index.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

main = soup.find("main")
if not main:
    print("⚠️ Estrutura inválida: não encontrei <main> no index.html")
    exit()

# Criar card do sermão
novo_card = soup.new_tag("div", **{"class": "day"})
info = soup.new_tag("div", **{"class": "info"})
info.string = f"{data.strftime('%B')} - {descricao}"
novo_card.append(info)

link_tag = soup.new_tag("a", href=link)
link_tag.string = f"Série \"{serie}\" - {titulo} - {preletor}"
novo_card.append(link_tag)

# Inserir no final da seção correspondente
estacao = descricao.split(" - ")[0].lower().replace(" ", "-")
secao = main.find("section", {"class": estacao})
if secao:
    grid = secao.find("div", {"class": "grid"})
    grid.append(novo_card)
else:
    print(f"⚠️ Seção {estacao} não encontrada, criando...")
    secao = soup.new_tag("section", **{"class": estacao})
    h2 = soup.new_tag("h2")
    h2.string = estacao.capitalize()
    secao.append(h2)
    grid = soup.new_tag("div", **{"class": "grid"})
    grid.append(novo_card)
    secao.append(grid)
    main.append(secao)

# ==============================
# Atualizar dropdown de preletores
# ==============================
select_preletor = soup.find("select", {"id": "filterPreletor"})
if select_preletor:
    values = [opt.get("value") for opt in select_preletor.find_all("option")]
    if preletor not in values:
        nova_opt = soup.new_tag("option", value=preletor)
        nova_opt.string = preletor
        select_preletor.append(nova_opt)

# Salvar arquivo atualizado
with open("index.html", "w", encoding="utf-8") as f:
    f.write(str(soup.prettify()))

print("✅ Sermão adicionado com sucesso!")
