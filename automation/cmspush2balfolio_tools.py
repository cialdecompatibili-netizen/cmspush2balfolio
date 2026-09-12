"""
cmspush2balfolio_tools.py (v2)
Toolbox Python completa per gestire il sito cmspush2balfolio (clone al-folio).

Path progetto: C:\\Users\\mirco\\Desktop\\cmspush2balfolio
Sito live:     https://cialdecompatibili-netizen.github.io/cmspush2balfolio/
Repo:          https://github.com/cialdecompatibili-netizen/cmspush2balfolio

Verificato sui file reali del tema (non assunto): i campi tags/categories nei
post sono stringhe separate da spazio (es. "jekyll blog"), NON liste YAML.

USO:
    import cmspush2balfolio_tools as site

    # --- HOME (about.md) ---
    site.update_about(subtitle="Nuovo sottotitolo")
    site.update_about(bio="Nuovo testo biografia.")

    # --- BLOG (_posts/) ---
    site.create_post(
        title="Il mio articolo",
        date="2026-09-12",
        description="Breve descrizione per l'anteprima",
        tags="jekyll python",
        categories="novità",
        body="Testo dell'articolo in markdown."
    )
    site.list_posts()

    # --- PROGETTI (_projects/) ---
    site.create_project(
        slug="10_project",
        title="Nome progetto",
        description="Descrizione breve",
        category="work",   # work o fun (vedi display_categories in _pages/projects.md)
        importance=1,
        body="Testo lungo del progetto in markdown."
    )
    site.list_projects()

    # --- PUBBLICAZIONE ---
    site.publish("Descrizione della modifica")   # git add+commit+push+verifica live
    site.verify_live()                            # solo verifica, senza push

NOTE IMPORTANTI:
- Le funzioni update_* modificano SOLO il campo richiesto (edit chirurgico).
- Il tema è "thin starter": build reale su GitHub Actions (bundle install +
  jekyll build + deploy su branch gh-pages). Il push su main triggera il
  workflow, ci vogliono 1-3 minuti (la funzione publish() attende 90s).
- I "title" delle pagine _pages/*.md (voci del menu navbar: blog/projects/cv
  ecc.) NON vanno tradotti/cambiati: sono usati come identificatori interni
  dal tema e cambiarli può rompere permalink/collegamenti. Solo i CONTENUTI
  (testi, articoli, progetti) sono sicuri da tradurre/modificare.
- Il logo scompare in home: è comportamento standard del tema al-folio
  (nasconde il logo quando la pagina mostra la foto profilo), non un bug.
"""

import os
import re
import subprocess
import time
import urllib.request

PROJECT_PATH = r"C:\Users\mirco\Desktop\cmspush2balfolio"
ABOUT_PATH = os.path.join(PROJECT_PATH, "_pages", "about.md")
POSTS_DIR = os.path.join(PROJECT_PATH, "_posts")
PROJECTS_DIR = os.path.join(PROJECT_PATH, "_projects")
PAGES_DIR = os.path.join(PROJECT_PATH, "_pages")
SITE_URL = "https://cialdecompatibili-netizen.github.io/cmspush2balfolio/"


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# HOME (about.md)
# ---------------------------------------------------------------------------

def update_about(subtitle=None, bio=None, more_info_html=None):
    """
    Modifica chirurgicamente about.md (la homepage).

    subtitle: riga sotto il titolo (es. "Sviluppatore indipendente...")
    bio: sostituisce TUTTO il testo del corpo pagina (sotto il frontmatter)
    more_info_html: sostituisce il blocco <p>...</p> sotto la foto profilo
                     (passare l'HTML completo, es. "<p>Italia</p>")
    """
    content = _read(ABOUT_PATH)

    if subtitle is not None:
        content = re.sub(
            r"^subtitle:.*$",
            f"subtitle: {subtitle}",
            content,
            count=1,
            flags=re.MULTILINE,
        )

    if more_info_html is not None:
        content = re.sub(
            r"(more_info: >\n)(?:.*\n)*?(\n)",
            rf"\1    {more_info_html}\n\2",
            content,
            count=1,
        )

    if bio is not None:
        parts = content.split("---")
        if len(parts) >= 3:
            content = "---" + parts[1] + "---\n\n" + bio + "\n"

    _write(ABOUT_PATH, content)
    print(f"about.md aggiornato: {ABOUT_PATH}")


# ---------------------------------------------------------------------------
# BLOG (_posts/)
# ---------------------------------------------------------------------------

def create_post(title, date, description="", tags="", categories="", body="", thumbnail=None):
    """
    Crea un nuovo articolo blog in _posts/YYYY-MM-DD-slug.md

    date: formato 'YYYY-MM-DD'
    tags, categories: stringhe separate da spazio, es. "jekyll python" (NON liste)
    """
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    filename = f"{date}-{slug}.md"
    path = os.path.join(POSTS_DIR, filename)

    frontmatter = "---\n"
    frontmatter += "layout: post\n"
    frontmatter += f"title: {title}\n"
    frontmatter += f"date: {date} 12:00:00\n"
    if description:
        frontmatter += f"description: {description}\n"
    if tags:
        frontmatter += f"tags: {tags}\n"
    if categories:
        frontmatter += f"categories: {categories}\n"
    if thumbnail:
        frontmatter += f"thumbnail: {thumbnail}\n"
    frontmatter += "---\n\n"

    _write(path, frontmatter + body + "\n")
    print(f"Articolo creato: {path}")
    return path


def update_post(filename, **fields):
    """
    Modifica un post esistente per nome file (es. '2026-09-12-slug.md').
    Aggiorna solo i campi frontmatter passati come kwargs.
    """
    path = os.path.join(POSTS_DIR, filename)
    content = _read(path)

    for key, value in fields.items():
        pattern = rf"^{key}:.*$"
        if re.search(pattern, content, flags=re.MULTILINE):
            content = re.sub(pattern, f"{key}: {value}", content, count=1, flags=re.MULTILINE)
        else:
            content = content.replace("---\n\n", f"{key}: {value}\n---\n\n", 1)

    _write(path, content)
    print(f"Post aggiornato: {path}")


def list_posts():
    """Elenca tutti gli articoli blog esistenti."""
    files = sorted(os.listdir(POSTS_DIR))
    for f in files:
        print(f)
    return files


# ---------------------------------------------------------------------------
# PROGETTI (_projects/)
# ---------------------------------------------------------------------------

def create_project(slug, title, description="", category="work", importance=1, img=None, body=""):
    """
    Crea un nuovo progetto in _projects/<slug>.md
    slug: nome file senza estensione, es. "10_project"
    category: deve essere una tra quelle in _pages/projects.md -> display_categories (work, fun)
    importance: numero, ordina i progetti (1 = primo)
    """
    filename = f"{slug}.md" if not slug.endswith(".md") else slug
    path = os.path.join(PROJECTS_DIR, filename)

    frontmatter = "---\n"
    frontmatter += "layout: page\n"
    frontmatter += f"title: {title}\n"
    if description:
        frontmatter += f"description: {description}\n"
    if img:
        frontmatter += f"img: {img}\n"
    frontmatter += f"importance: {importance}\n"
    frontmatter += f"category: {category}\n"
    frontmatter += "---\n\n"

    _write(path, frontmatter + body + "\n")
    print(f"Progetto creato: {path}")
    return path


def update_project(filename, **fields):
    """
    Modifica un progetto esistente per nome file (es. '1_project.md').
    Aggiorna solo i campi frontmatter passati come kwargs.
    """
    path = os.path.join(PROJECTS_DIR, filename)
    content = _read(path)

    for key, value in fields.items():
        pattern = rf"^{key}:.*$"
        if re.search(pattern, content, flags=re.MULTILINE):
            content = re.sub(pattern, f"{key}: {value}", content, count=1, flags=re.MULTILINE)
        else:
            content = content.replace("---\n\n", f"{key}: {value}\n---\n\n", 1)

    _write(path, content)
    print(f"Progetto aggiornato: {path}")


def list_projects():
    """Elenca tutti i progetti esistenti."""
    files = sorted(os.listdir(PROJECTS_DIR))
    for f in files:
        print(f)
    return files


# ---------------------------------------------------------------------------
# PAGINE GENERICHE (_pages/) — solo campi sicuri (description, ecc.)
# NON modificare 'title' delle pagine: rischio rottura permalink/menu.
# ---------------------------------------------------------------------------

def update_page_field(page_filename, field, value):
    """
    Modifica UN campo sicuro del frontmatter di una pagina in _pages/.
    Esempio: update_page_field("projects.md", "description", "I miei progetti")
    Evita di toccare 'title', 'permalink', 'nav', 'nav_order'.
    """
    if field in ("title", "permalink", "nav", "nav_order", "layout"):
        print(f"ATTENZIONE: campo '{field}' bloccato per sicurezza. Nessuna modifica fatta.")
        return

    path = os.path.join(PAGES_DIR, page_filename)
    content = _read(path)
    pattern = rf"^{field}:.*$"
    if re.search(pattern, content, flags=re.MULTILINE):
        content = re.sub(pattern, f"{field}: {value}", content, count=1, flags=re.MULTILINE)
    else:
        content = content.replace("---\n", f"{field}: {value}\n---\n", 1)

    _write(path, content)
    print(f"{page_filename} aggiornato ({field}).")


# ---------------------------------------------------------------------------
# PUBBLICAZIONE
# ---------------------------------------------------------------------------

def publish(message="Aggiornamento contenuti"):
    """
    git add + commit + push, poi verifica che il sito live risponda 200.
    La build su GitHub Actions impiega 1-3 minuti dopo il push.
    """
    subprocess.run(["git", "add", "."], cwd=PROJECT_PATH, check=True)
    result = subprocess.run(
        ["git", "commit", "-m", message], cwd=PROJECT_PATH, capture_output=True, text=True
    )
    print(result.stdout or result.stderr)

    subprocess.run(["git", "push"], cwd=PROJECT_PATH, check=True)
    print("Push completato. Attendo build GitHub Actions (~90s)...")
    time.sleep(90)
    verify_live()


def verify_live(url=SITE_URL):
    """Verifica che il sito risponda 200 OK (no-cache)."""
    try:
        req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            print(f"Sito live: {status} OK -> {url}")
            return status == 200
    except Exception as e:
        print(f"Errore verifica live: {e}")
        return False


if __name__ == "__main__":
    print("cmspush2balfolio_tools v2 caricato.")
    print(f"Progetto: {PROJECT_PATH}")
    print(f"Sito: {SITE_URL}")
