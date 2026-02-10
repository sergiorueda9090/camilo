# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django 4.2 personal website/blog for a legal author. Spanish-language content about constitutional law and political analysis. Single app (`main`) with MySQL database, CKEditor for rich text, and environment config via `.env` + `python-dotenv`.

## Commands

```bash
# Activate virtual environment (Windows)
env\Scripts\activate

# Run development server
python manage.py runserver

# Run migrations
python manage.py migrate

# Run tests
python manage.py test main

# Seed initial content
python manage.py crear_contenido_inicial
```

## Architecture

- **camilo/** - Django project settings and root URL configuration
- **main/** - Primary app: models, views, admin, templates at `main/templates/main/`
- **static/** - Static assets (`static/main/images/`)
- **media/** - User uploads (gitignored), served in DEBUG mode

Root URLs delegate to `main.urls`. Two routes: home (`/`) and article detail (`/articulo/<slug>/`). Admin at `/admin/`.

## Key Models

- **PerfilAutor** - Singleton author profile (enforced in `save()`). Access via `PerfilAutor.get_perfil()`.
- **Articulo** - Blog articles with CKEditor `RichTextField` for content, slug auto-generation, view counter, draft/published workflow, and SEO fields. Featured article via `destacado` flag.
- **CapsulaJuridica** - Short legal tips for sidebar, capped at 5 (enforced in `save()`).
- **Categoria** - Article categories with auto-generated slugs.
- **RedSocial** - Social media links for footer, uses Bootstrap Icons classes.

All models use Spanish field names and labels. Views pass shared context (perfil, capsulas, redes_sociales, articulos_footer) to every template.

## Configuration

Database and secrets loaded from `.env` file (SECRET_KEY, DEBUG, DB_ENGINE, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT). Default database engine is MySQL.
