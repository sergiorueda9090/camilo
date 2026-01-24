# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django 4.2 project with a single app (`main`) serving a web page.

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
```

## Architecture

- **camilo/** - Django project settings and root URL configuration
- **main/** - Primary app with views and templates at `main/templates/main/`
- **static/** - Static assets organized by app (`static/main/images/`)

Root URLs delegate to `main.urls` for the home page at `/`. Admin is at `/admin/`.
