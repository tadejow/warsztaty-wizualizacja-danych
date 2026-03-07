##📊 Warsztaty: Wizualizacja i Analiza Danych w Pythonie

Witaj w repozytorium poświęconym warsztatom z analizy i wizualizacji danych! Cel tego projektu jest prosty: **chcemy, abyś skupił się na wyciąganiu wniosków i tworzeniu pięknych wykresów, zamiast tracić czas na żmudne czyszczenie danych i debugowanie kodu.**

Aby to umożliwić, przygotowaliśmy dedykowany zestaw narzędziowy (pipeline), który automatyzuje powtarzalne czynności analityczne.

---

## 🚀 Cel Projektu
Głównym celem warsztatów jest przeprowadzenie kompleksowej analizy korelacji między wskaźnikami ekonomicznymi, społecznymi a subiektywnym poczuciem szczęścia mieszkańców różnych krajów. Odpowiadamy na pytania takie jak:
* Czy PKB jest jedynym wyznacznikiem szczęścia?
* Jak koszty życia i ceny nieruchomości korelują z jakością życia?
* Czy zanieczyszczenie środowiska i korki drogowe mają mierzalny wpływ na satysfakcję obywateli?

---

## 📂 Struktura Repozytorium

```text
warsztaty-wizualizacja-danych/
├── data/                   # Zbiory danych w formacie .csv
│   ├── world_data.csv      # Dane demograficzne i ogólne o państwach
│   ├── happiness_index.csv # Główne dane o poczuciu szczęścia
│   └── [pozostałe indeksy: crime, health, pollution, traffic itd.]
├── docs/                   # Dokumentacja warsztatowa
│   └── zestaw_narzedzi.pdf # Opis funkcji w formacie LaTeX (PDF)
├── notebooks/              # Gotowe scenariusze analizy
│   ├── demo.ipynb          # Prezentacja wszystkich dostępnych funkcji
│   └── correlations.ipynb  # Zaawansowana analiza korelacji między zbiorami
├── pipeline/               # Serce projektu
│   └── utils.py            # Skrypt Python z gotowymi funkcjami analitycznymi
└── requirements.txt        # Lista wymaganych bibliotek
```

---

## 🛠️ Instalacja i Przygotowanie

### 1. Klonowanie repozytorium
```bash
git clone https://github.com/tadejow/warsztaty-wizualizacja-danych.git
cd warsztaty-wizualizacja-danych
```

### 2. Instalacja zależności
Zalecamy użycie wirtualnego środowiska (venv):
```bash
# Tworzenie środowiska
python -m venv venv

# Aktywacja (Windows)
venv\Scripts\activate
# Aktywacja (Mac/Linux)
source venv/bin/activate

# Instalacja bibliotek
pip install -r requirements.txt
```

---

## 💻 Jak pracować z kodem?

### Wykorzystanie narzędzi (`pipeline/utils.py`)
W pliku `utils.py` znajdziesz autorskie funkcje, które ustandaryzują Twoją pracę. Najważniejsze z nich to:
*   **Wczytywanie i Czyszczenie:** `wczytaj_dane()` (automatycznie naprawia nazwy kolumn i usuwa błędy).
*   **Łączenie:** `polacz_dane()` (inteligentnie łączy tabele, dbając o spójność typów).
*   **Analiza:** `tabela_korelacji()` (tworzy czytelne mapy ciepła dla wybranych zmiennych).
```bash
jupyter notebook
```
---

**Autorzy:** [tadejow](https://github.com/tadejow), [Jacek Kowalski](https://github.com/346112-gif)
**Licencja:** MIT
*Udanych warsztatów! Powodzenia w odkrywaniu prawdy ukrytej w danych!* 📈✨---


W pliku `notebooks/correlations.ipynb` zastosowano technikę "odchudzonego łączenia", co pozwala na precyzyjną analizę korelacji bez dublowania zbędnych informacji (np. rolnictwa czy klimatu w tabelach dotyczących kosztów życia).

## ⚠️ Ważne informacje o danych
Dane są pobierane bezpośrednio z wersji **RAW** tego repozytorium na GitHubie. Dzięki temu, pracując w Google Colab lub lokalnie, zawsze masz dostęp do najświeższych zbiorów danych bez konieczności ich ręcznego pobierania na dysk.

Następnie otwórz `demo.ipynb`, aby zobaczyć jak krok po kroku przejść od surowych danych do zaawansowanych wniosków.
Aby uruchomić demo warsztatowe, przejdź do folderu `notebooks` i uruchom Jupyter Notebook lub Jupyter Lab:
*   **Wizualizacja:** `wykres_babelkowy()`, `wykres_punktowy()` i inne (estetyczne wykresy gotowe do prezentacji).
