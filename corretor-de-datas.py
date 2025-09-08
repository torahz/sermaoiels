# corrigir_sermao.py
from bs4 import BeautifulSoup
from datetime import datetime
import unicodedata

def slugify(text: str) -> str:
    nf = unicodedata.normalize("NFD", text)
    no_accents = "".join(ch for ch in nf if unicodedata.category(ch) != "Mn")
    return no_accents.strip().lower().replace(" ", "-")

MESES_PT = [
    "janeiro","fevereiro","março","abril","maio","junho",
    "julho","agosto","setembro","outubro","novembro","dezembro"
]

# mapa mínimo — pode ser reutilizado do integrador.py (aqui você pode importar em vez de repetir)
calendario = {
    "07/09/2025": "Criacao - 1º Domingo da Criação",
    "14/09/2025": "Criacao - 2º Domingo da Criação",
    "21/09/2025": "Criacao - 3º Domingo da Criação",
    "28/09/2025": "Criacao - 4º Domingo da Criação",
    # adicione outras datas se desejar
}

def corrigir_por_link(link_substr, data_str):
    # carregar index
    with open("index.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # localizar a tag <a> que contenha a substring do link
    a_tag = None
    for a in soup.find_all("a", href=True):
        if link_substr in a['href']:
            a_tag = a
            break

    if not a_tag:
        print("❌ Link não encontrado no index.html.")
        return

    day_div = a_tag.find_parent("div", class_="day")
    if not day_div:
        print("❌ Estrutura inesperada: não encontrei o card (.day) que contém esse link.")
        return

    # verificar data no calendário
    try:
        dt = datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        print("❌ Data inválida. Use dd/mm/YYYY.")
        return

    if data_str not in calendario:
        print("❌ Data não encontrada no calendário (calendario do script).")
        return

    descricao = calendario[data_str]  # ex: "Criacao - 1º Domingo da Criação"
    partes = descricao.split(" - ", 1)
    estacao_nome = partes[0]
    detalhe = partes[1] if len(partes) > 1 else ""

    # atualiza <div class="info"> para formato pt ("Setembro - ...")
    mes_pt = MESES_PT[dt.month - 1].capitalize()
    info_div = day_div.find("div", class_="info")
    if info_div:
        info_div.string = f"{mes_pt} - {detalhe}"
    else:
        novo_info = soup.new_tag("div", **{"class": "info"})
        novo_info.string = f"{mes_pt} - {detalhe}"
        day_div.insert(0, novo_info)

    # remover day_div do local atual (extract retorna o elemento)
    day_div.extract()

    # inserir na seção correta (criacao)
    main = soup.find("main")
    if not main:
        print("❌ <main> não encontrado.")
        return

    classe_secao = slugify(estacao_nome)
    secao = main.find("section", {"class": classe_secao})
    if not secao:
        # cria seção
        secao = soup.new_tag("section", **{"class": classe_secao})
        h2 = soup.new_tag("h2")
        # título de exibição: "Criação" com acento se for criacao
        if estacao_nome.lower().startswith("criacao"):
            h2.string = "Criação"
        else:
            h2.string = estacao_nome.capitalize()
        secao.append(h2)
        grid = soup.new_tag("div", **{"class": "grid"})
        secao.append(grid)
        main.append(secao)
    else:
        grid = secao.find("div", {"class": "grid"})
        if not grid:
            grid = soup.new_tag("div", **{"class": "grid"})
            secao.append(grid)

    # agora re-inserir day_div dentro do grid da seção
    grid.append(day_div)

    # salvar
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(str(soup.prettify(formatter="html")))

    print("✅ Correção aplicada: card movido para a seção correta.")

if __name__ == "__main__":
    print("Corrigir um sermão já existente por link.")
    link = input("Cole aqui parte do link ou ID do arquivo (ex.: 1MISxTHbWeuqsPM_...): ").strip()
    data = input("Data correta do sermão (dd/mm/yyyy): ").strip()
    corrigir_por_link(link, data)