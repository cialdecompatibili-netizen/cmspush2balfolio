# CLAUDE.md

## 🚩 PROGETTO MIRCO — cmspush2balfolio (leggi questa sezione prima di tutto)

**Cos'è:** sito personale (portfolio/blog) di Mirco, clone al-folio, deploy automatico
su GitHub Pages via GitHub Actions.

- Path locale: `C:\Users\mirco\Desktop\cmspush2balfolio\`
- Repo: https://github.com/cialdecompatibili-netizen/cmspush2balfolio
- Sito live: https://cialdecompatibili-netizen.github.io/cmspush2balfolio/
- Build/Actions: https://github.com/cialdecompatibili-netizen/cmspush2balfolio/actions
- Toolbox Python: `automation\cmspush2balfolio_tools.py` — TUTTO va pilotato da qui
  (edit chirurgico + git add/commit/push + verifica live), mai a mano nei file
  salvo casi non ancora coperti dalla toolbox.

### Contenuti (post/progetti/categorie)

```python
import cmspush2balfolio_tools as site
site.create_post(title=..., date="YYYY-MM-DD", description=..., tags=..., categories=..., body=...)
site.create_project(slug=..., title=..., category="work", body=...)  # auto-crea la categoria se non esiste
site.list_project_categories()      # categorie VINCOLATE (solo queste comparono su /projects/)
site.add_project_category("nome")   # aggiunge categoria progetti
site.remove_project_category("nome")
site.list_blog_categories()         # categorie blog LIBERE, nessun vincolo — solo per coerenza/riuso
```

### Menu navbar / dropdown / footer

```python
site.list_nav_menu()                # stato COMPLETO del menu: ordine, titolo, nav true/false, dropdown
site.toggle_nav_page("cv.md", False)  # mostra/nasconde una voce dal menu (non cancella la pagina)
site.list_dropdown_children()       # voci del sottomenu "submenus"
site.add_dropdown_child("titolo", "/permalink/")
site.list_socials()                 # icone footer (_data/socials.yml)
site.update_social("email", "nuovo@indirizzo.it")
site.update_social("rss_icon", None)  # commenta/nasconde una icona
```

**Mappa pagine → menu (stato al 12/09/2026, verificare sempre con `list_nav_menu()` perché cambia):**

| Voce                | File in `_pages/` | nav                     | note                                                                                 |
| ------------------- | ----------------- | ----------------------- | ------------------------------------------------------------------------------------ |
| home                | about.md          | (sempre, è la root `/`) | bio, subtitle, more_info                                                             |
| blog                | blog.md           | true                    |                                                                                      |
| projects            | projects.md       | true                    | `display_categories` vincola le category progetti                                    |
| CV                  | cv.md             | **false**               | tolto dal menu su richiesta Mirco (12/09/2026), pagina resta raggiungibile su `/cv/` |
| teaching            | teaching.md       | true                    |                                                                                      |
| people              | profiles.md       | true                    |                                                                                      |
| submenus (dropdown) | dropdown.md       | true                    | children: bookshelf, blog                                                            |
| publications        | publications.md   | false                   | contiene demo Einstein in `_bibliography/papers.bib`, mai attivata nel menu          |
| repositories        | repositories.md   | false                   |                                                                                      |
| plugins             | plugins.md        | false                   | doc del tema, non toccare                                                            |
| news                | news.md           | (nessun campo nav)      | alimenta la sezione "novità" in home                                                 |

**Regola:** per aggiungere/togliere qualsiasi voce dal menu usa SEMPRE
`toggle_nav_page()` (edit chirurgico sul campo `nav`), mai riscrivere il file intero.
Stessa logica per footer/social: SEMPRE `update_social()`, mai riscrivere `socials.yml`.

### Home (about.md)

- `selected_papers: false` (12/09/2026) — rimossa sezione "pubblicazioni selezionate"
  demo (Einstein/Podolsky/Rosen) dalla home su richiesta Mirco.
- Tradotto in italiano: "news"→"novità", "latest posts"→"ultimi articoli" via override
  sicuro `_layouts/about.liquid` (solo 3 stringhe, non tocca header/menu).
- Logo assente in home = comportamento standard del tema (si nasconde quando c'è la
  foto profilo), non un bug.

### Pubblicazione

```python
site.publish("messaggio commit")   # git add+commit+push, poi attende 90s e verifica live
site.verify_live()                 # solo verifica 200, senza push
```

⚠️ `publish()` può superare il timeout della shell per via del `time.sleep(90)` —
il push va comunque a buon fine, basta verificare con `verify_live()` o controllare
lo stato della build su Actions (vedi link sopra) subito dopo.

### ⚠️ NON toccare senza motivo

`AGENTS.md` e tutto il resto di questo `CLAUDE.md` sotto questa sezione sono
documentazione ORIGINALE del tema al-folio (per chi sviluppa il tema/le gem a monte,
tipo `al_folio_core`). Non riguardano la gestione contenuti di Mirco — utili solo
come riferimento tecnico se serve capire l'architettura interna del tema.

---

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@AGENTS.md

`AGENTS.md` (imported above) is the **authoritative** agent entry point: change routing, the stop sign for gem-owned paths, the three silent failure modes, and the validated command set. Keep it short and ecosystem-neutral. Cross-repo architecture — the wrapper/tag/gem delegation table, feature gating, the v1 config contract, local overrides — lives in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md); area-to-gem ownership lives in [`docs/BOUNDARIES.md`](docs/BOUNDARIES.md).

**Read those three before editing anything.** Everything below is Claude-specific or longer-form operational detail that does not belong in the short entry point. Do not restate facts from those files here — link to them.

## Daily dev loop

```bash
bundle install                                # ruby gems
bundle exec jekyll serve                      # dev server → http://localhost:4000/al-folio/  (NOTE baseurl)
bundle exec jekyll build --baseurl /al-folio  # production-style build to _site/
bash test/integration_distill.sh              # run ONE integration test (any of the seven in test/)
npm run test:visual:update                    # refresh playwright snapshots after intentional UI change
bundle exec al-folio upgrade apply --safe     # deterministic codemods (font-weight-* → font-*, remote→local URLs)
bundle exec al-folio upgrade overrides diff <path>    # then `overrides accept <path>` to acknowledge an override
```

## Optional toolchains

- **Jupyter posts.** `bin/setup-python-deps` installs _only_ `jupyter` and `nbconvert` (via `pip --user --break-system-packages`) for `jekyll-jupyter-notebook`. It does **not** read `requirements.txt`. Missing `jupyter-nbconvert` is warn-and-continue; notebook rendering is skipped.
- **Everything else Python.** [`requirements.txt`](requirements.txt) is the fuller list and must be installed separately (`python3 -m pip install -r requirements.txt`): `rendercv[full]` for CV rendering, `scholarly` for `bin/update_scholar_citations.py`, plus `nbconvert` and `pyyaml`.
- **Responsive images.** `imagemagick.enabled: true` needs ImageMagick `convert` on `PATH`.
- **Manual deploy.** `bin/deploy` is the manual `gh-pages` build + purgecss + force-push path; CI normally deploys. `purgecss` is not a devDependency — install it with `npm install -g purgecss`.

## Docker serving model (v1-specific)

`docker compose up -d` bind-mounts the repo to `/srv/jekyll` and runs `bin/entry_point.sh`, which serves with `--force_polling --destination /tmp/_site`. The build output deliberately goes to **container-local `/tmp/_site`, not the bind-mounted `_site`** — writing `_site` back across the host bind mount caused write deadlocks. The container also `inotifywait`s `_config.yml` and restarts Jekyll on change (config edits aren't hot-reloaded by `--watch`). Verify with the `/al-folio` baseurl: `curl -fsS http://127.0.0.1:8080/al-folio/`. `docker-compose-slim.yml` pulls a prebuilt `:slim` image instead of building locally.

## CI gates and the style contract

`npm run lint:style-contract` (`test/style_contract.js`) is the automated enforcement of the thin-starter boundary and will fail CI if you cross it. Beyond the forbidden paths listed in `AGENTS.md`, it also asserts that `_config.yml` keeps `theme: al_folio_core` and the required plugins, that the `third_party_libraries` SRI pins are present, and that the `al_math` Gemfile pin stays on a released version rather than a git branch.

Other gates:

- `unit-tests.yml` — style contract plus all seven `test/integration_*.sh` scripts (`comments`, `plugin_toggles`, `distill`, `bootstrap_compat`, `upgrade_cli`, `css_minify`, `new_plugins`).
- `visual-regression.yml` — Playwright on chromium + webkit, diffing the candidate build against a `v0.16.3` baseline worktree served on `:4100` via `BASELINE_URL`.
- `upgrade-check.yml` — `bundle exec al-folio upgrade audit`.
- `prettier.yml` — Prettier with `@shopify/prettier-plugin-liquid` and `printWidth: 150`. Run `npm run lint:prettier` before pushing; `npx prettier . --write` fixes.
- `update-tocs.yml` — regenerates `<!--ts-->…<!--te-->` blocks in changed root and `docs/` Markdown files. If you add or rename a heading, expect a follow-up auto-commit on `main`.

## Gem version pins

`Gemfile` pins every `al-*` gem to an exact released version in `group :al_folio_plugins`, and `_config.yml` lists the same gems under `plugins:`. Read the current pins from the `Gemfile` rather than trusting any version quoted in prose — including here. To test a gem fix against this site, repoint the `Gemfile` at a sibling checkout (`path:`, `git:`, or `branch:`) and `bundle install`; see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#working-on-a-gem-alongside-the-starter). Revert the pin before committing.
