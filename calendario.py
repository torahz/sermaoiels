"""Calendário gregoriano, conforme PDF de 2026 e regras confirmadas pela igreja.

Regras locais: setembro = Criação; aniversário = segundo domingo de setembro;
Reforma = último domingo de outubro; após Pentecostes até junho, Tempo Comum
a partir de julho. A contagem após Pentecostes continua durante a Criação.
O histórico publicado nunca é recalculado por este módulo.
"""
from datetime import date, timedelta


def pascoa(ano):
    if not 1583 <= ano <= 4099:
        raise ValueError("Escolha um ano entre 1583 e 4099.")
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    n = h + l - 7 * m + 114
    return date(ano, n // 31, n % 31 + 1)


def proximo_domingo(d, incluir=True):
    dias = (6 - d.weekday()) % 7
    return d + timedelta(days=dias if incluir or dias else 7)


def primeiro_advento(ano):
    return proximo_domingo(date(ano, 11, 27))


def classificar(d):
    if d.weekday() != 6:
        raise ValueError("A data deve ser um domingo.")
    p = pascoa(d.year)
    pentecostes = p + timedelta(days=49)
    advento = primeiro_advento(d.year)
    if d.month == 12 and d.day >= 25:
        natal = date(d.year, 12, 25)
        n = (d - proximo_domingo(natal, incluir=False)).days // 7 + 1
        return ("Natal", "Domingo de Natal" if d == natal else f"{n}º Domingo depois do Natal")
    if d.month == 1 and d.day < 6:
        natal = date(d.year - 1, 12, 25)
        n = (d - proximo_domingo(natal, incluir=False)).days // 7 + 1
        return "Natal", f"{n}º Domingo depois do Natal"
    if d >= advento:
        return "Advento", f"{(d-advento).days // 7 + 1}º Domingo de Advento"
    if d == advento - timedelta(days=7):
        return "Cristo Rei", "Domingo de Cristo Rei"
    if d < p - timedelta(days=49):
        epifania = date(d.year, 1, 6)
        if d == epifania:
            return "Epifania", "Domingo da Epifania"
        n = (d - proximo_domingo(epifania, incluir=False)).days // 7 + 1
        label = f"{n}º Domingo após a Epifania"
        return "Epifania", label + (" (Batismo do Senhor)" if n == 1 else "")
    if d == p - timedelta(days=49):
        return "Epifania", "Último Domingo da Epifania (Transfiguração)"
    if d < p:
        if d == p - timedelta(days=7):
            return "Quaresma", "Domingo de Ramos (6º da Quaresma)"
        return "Quaresma", f"{7 - (p-d).days // 7}º Domingo da Quaresma"
    if d == p:
        return "Páscoa", "Domingo de Páscoa"
    if d < pentecostes:
        n = (d-p).days // 7 + 1
        return "Páscoa", f"{n}º Domingo de Páscoa" + (" (Ascensão)" if n == 7 else "")
    if d == pentecostes:
        return "Pentecostes", "Domingo de Pentecostes"
    n = (d-pentecostes).days // 7
    if n == 1:
        return "Trindade", "Domingo da Trindade (1º após Pentecostes)"
    if d.month == 9:
        numero = (d.day - 1) // 7 + 1
        return "Estação da Criação", f"{numero}º Domingo da Estação da Criação" + (" (Aniversário da Igreja)" if numero == 2 else "")
    if d.month <= 6:
        return "Após Pentecostes", f"{n}º Domingo após Pentecostes"
    label = f"{n}º Domingo do Tempo Comum"
    if d.month == 10 and (d + timedelta(days=7)).month == 11:
        label += " (Reforma Protestante)"
    return "Tempo Comum", label


def domingos(ano):
    pascoa(ano)  # valida o intervalo antes de construir datas
    d = proximo_domingo(date(ano, 1, 1))
    resultado = []
    while d.year == ano:
        estacao, celebracao = classificar(d)
        resultado.append({"date": d.isoformat(), "season": estacao,
                          "celebration": celebracao,
                          "liturgicalYear": ano + (d >= primeiro_advento(ano))})
        d += timedelta(days=7)
    return resultado
