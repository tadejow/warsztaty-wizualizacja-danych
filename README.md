# 📊 Warsztaty: Wizualizacja i Analiza Danych w Pythonie

Witaj w repozytorium poświęconym warsztatom z analizy i wizualizacji danych! Cel tego projektu jest prosty: **chcemy, abyś skupił się na wyciąganiu wniosków i tworzeniu pięknych wykresów, zamiast tracić czas na żmudne czyszczenie danych i debugowanie kodu.**

Aby to umożliwić, przygotowaliśmy dedykowany zestaw narzędziowy (pipeline), który automatyzuje powtarzalne czynności analityczne.

## 🚀 Cel Projektu
Głównym celem warsztatów jest przeprowadzenie kompleksowej analizy korelacji między wskaźnikami ekonomicznymi, społecznymi a subiektywnym poczuciem szczęścia mieszkańców różnych krajów. Odpowiadamy na pytania takie jak:
- Czy PKB jest jedynym wyznacznikiem szczęścia?
- Jak koszty życia i ceny nieruchomości korelują z jakością życia?
- Czy zanieczyszczenie środowiska i korki drogowe mają mierzalny wpływ na satysfakcję obywateli?

## 📂 Struktura Repozytorium

- **data/**: Zbiory danych w formacie .csv (world_data, happiness_index, crime, health itp.).
- **docs/**: Dokumentacja warsztatowa i opis funkcji w formacie LaTeX (zestaw_narzedzi.pdf).
- **notebooks/**: Gotowe scenariusze analizy (demo.ipynb, correlations.ipynb).
- **pipeline/**: Skrypt Python `utils.py` z gotowymi funkcjami analitycznymi.
- **requirements.txt**: Lista wymaganych bibliotek do instalacji.

## 🛠️ Instalacja i Przygotowanie

### 1. Klonowanie repozytorium
```bash
git clone https://github.com/tadejow/warsztaty-wizualizacja-danych.git
cd warsztaty-wizualizacja-danych
```

### 2. Instalacja zależności
```bash
pip install -r requirements.txt
```

## 💻 Jak pracować z kodem?

### Wykorzystanie narzędzi (pipeline/utils.py)
W pliku `utils.py` znajdziesz autorskie funkcje, które ustandaryzują Twoją pracę:
- **Wczytywanie i Czyszczenie:** `wczytaj_dane()` (automatycznie naprawia nazwy kolumn i konwertuje typy).
- **Łączenie:** `polacz_dane()` (inteligentnie łączy tabele, dbając o spójność typów).
- **Analiza:** `tabela_korelacji()` (tworzy czytelne mapy ciepła dla wybranych zmiennych).
- **Wizualizacja:** `wykres_babelkowy()`, `wykres_punktowy()` i inne estetyczne wykresy.

### Praca z Notebookami
Otwórz Jupyter Notebook w folderze głównym i przejdź do folderu `notebooks`, aby uruchomić:
- `demo.ipynb`: Prezentacja wszystkich dostępnych funkcji pipeline'u.
- `correlations.ipynb`: Zaawansowana analiza korelacji między wieloma zbiorami danych.

## ⚠️ Ważne informacje o danych
Dane są pobierane bezpośrednio z wersji **RAW** tego repozytorium na GitHubie. Dzięki temu, pracując w Google Colab lub lokalnie, zawsze masz dostęp do najświeższych zbiorów bez konieczności ich ręcznego pobierania na dysk.

Autorzy: [tadejow](https://github.com/tadejow) [Jacek Kowalski](https://github.com/346112-gif)
Licencja: MIT
