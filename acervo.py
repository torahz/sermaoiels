"""Leitura e escrita atômica do acervo incorporado ao index.html. Só biblioteca padrão."""
from collections import Counter
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlparse
import hashlib
import json
import os
import re
import tempfile

DATA_RE = re.compile(r'(<script id="sermoes-data" type="application/json">)(.*?)(</script>)', re.S)
CARDS_RE = re.compile(r'(<!-- SERMOES:CARDS:START -->).*?(<!-- SERMOES:CARDS:END -->)', re.S)


def ler(path):
    raw = Path(path).read_bytes()
    text = raw.decode("utf-8-sig")
    match = DATA_RE.search(text)
    if not match:
        raise ValueError("Selecione o index.html da versão atualizada do site.")
    data = json.loads(match.group(2))
    if data.get("version") != 2 or not isinstance(data.get("sermons"), list):
        raise ValueError("Formato de acervo incompatível.")
    ids = [r["id"] for r in data["sermons"]]
    if len(ids) != len(set(ids)):
        raise ValueError("O acervo contém identificadores repetidos.")
    return text, data, hashlib.sha256(raw).hexdigest()


def json_seguro(data):
    return json.dumps(data, ensure_ascii=False, indent=2).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def cards_html(records):
    cards = []
    for r in sorted(records, key=lambda r: (r["date"], r["id"]), reverse=True):
        e = lambda key: escape(str(r.get(key, "")), quote=True)
        date_label = date.fromisoformat(r["date"]).strftime("%d/%m/%Y")
        series = f'<p class="series">{e("series")}</p>' if r.get("series") and r.get("series") != r.get("title") else ""
        cards.append(f'''<article class="sermon-card" id="sermao-{e('id')}" data-id="{e('id')}">
  <div class="card-meta"><time datetime="{e('date')}">{date_label}</time><span class="season">{e('season')}</span></div>
  {series}<h3><a href="{e('url')}" target="_blank" rel="noopener">{e('title')}</a></h3>
  <p class="preacher">{e('preacher')}</p><p class="celebration">{e('celebration')}</p>
  <div class="card-actions"><a class="listen" href="{e('url')}" target="_blank" rel="noopener">Abrir gravação <span aria-hidden="true">↗</span></a><button class="share-sermon" type="button" data-share="{e('id')}" aria-label="Compartilhar sermão: {e('title')}">Compartilhar</button></div>
</article>''')
    return "\n".join(cards)


def render(text, data):
    if len(DATA_RE.findall(text)) != 1 or len(CARDS_RE.findall(text)) != 1:
        raise ValueError("O arquivo não contém os marcadores esperados. Nenhuma alteração foi feita.")
    text = DATA_RE.sub(lambda m: m[1] + "\n" + json_seguro(data) + "\n" + m[3], text)
    return CARDS_RE.sub(lambda m: m[1] + "\n" + cards_html(data["sermons"]) + "\n" + m[2], text)


def validar_novo(record):
    for key in ("id", "date", "title", "preacher", "series", "url", "season", "celebration"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError("Preencha todos os campos do sermão.")
    if date.fromisoformat(record["date"]).weekday() != 6:
        raise ValueError("Selecione um domingo válido.")
    u = urlparse(record["url"])
    if u.scheme != "https" or u.hostname != "drive.google.com" or u.username or u.password:
        raise ValueError("Informe o link HTTPS original de compartilhamento do Google Drive.")
    if not re.search(r"/file/d/[^/]+", u.path) and not (u.path == "/open" and "id=" in u.query):
        raise ValueError("Use o link de um arquivo do Drive, não de uma pasta.")


def adicionar(path, record, expected_hash):
    validar_novo(record)
    path = Path(path)
    text, data, fingerprint = ler(path)
    if fingerprint != expected_hash:
        raise ValueError("O arquivo mudou desde que foi aberto. Reabra o index.html antes de salvar.")
    before = json.dumps(data["sermons"], ensure_ascii=False, sort_keys=True)
    if any(r["id"] == record["id"] for r in data["sermons"]):
        raise ValueError("Este sermão já foi cadastrado.")
    # A inclusão nunca altera, corrige, renomeia ou recalcula registros anteriores.
    data["sermons"].append(dict(record))
    if json.dumps(data["sermons"][:-1], ensure_ascii=False, sort_keys=True) != before:
        raise ValueError("A preservação do acervo falhou.")
    updated = render(text, data)
    backup_dir = path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = backup_dir / f"index-{stamp}.html"
    original = path.read_bytes()
    if hashlib.sha256(original).hexdigest() != expected_hash:
        raise ValueError("O arquivo foi alterado. Reabra antes de salvar.")
    backup.write_bytes(original)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, suffix=".tmp", delete=False, newline="\n") as f:
            tmp = Path(f.name)
            f.write(updated)
            f.flush()
            os.fsync(f.fileno())
        _, check, _ = ler(tmp)
        if check != data:
            raise ValueError("Não foi possível validar o arquivo gerado.")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
            raise ValueError("O arquivo foi alterado durante o salvamento. Reabra antes de salvar.")
        os.replace(tmp, path)
    finally:
        if tmp and tmp.exists():
            tmp.unlink()
    return backup
