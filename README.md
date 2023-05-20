# Kamerový bezpečnostní systém s rozpoznáváním obrazu
__Jaroslav Pryjmak__
## Obsah
- __Raspberry Pi__
  - [Spuštění "aplikace" (main skript)](piApp/main.py)
  - [Detekce](piApp/src_detection/detect.py)
  - [Rozpoznávání](piApp/src_detection/recognize_faces_image.py)
  - [Synchronizace s databází](piApp/src_sync_data/sync_data.py)
- __Webová aplikace__
  - __Back-end__
    - [Spuštění aplikace (main skript)](app/main.py)
    - [Inicializace, konfigurace aplikace](app/website/__init__.py)
    - [Správa přístupu (login, logout, aktivita uživatele)](app/website/auth.py)
    - [Funkce uživatele](app/website/models.py)
    - [Hlavní funkce aplikace](app/website/views.py)
  - __Front-end__
    - [Layout stránek (HTML)](app/templates/layout.html)
    - [Domovská stránka (HTML)](app/templates/home.html)
    - [Stránka s logy (HTML)](app/templates/dat_logs.html)
    - [Login stránka (HTML)](app/templates/login.html)
    - [Sign-up stránka (HTML)](app/templates/sign_up.html)
    - [Výpis všech logů (HTML)](app/templates/logs_all.html)
    - [Hlavní motiv aplikace (CSS)](app/static/css/light.css)
    - [Funkce tmavého režimu (JS)](app/static/js/darkmode.js)
    - [Zobrazení nastavení (JS)](app/static/js/settings.js)
- __Server__
  - [Konfigurace nginx](config/nginx.conf)
  - [Konfigurace aplikace jako služby](config/flask.service)
