# ==============================================================================
# ZESTAW NARZĘDZIOWY - WARSZTATY Z ANALIZY I WIZUALIZACJI DANYCH
# ==============================================================================

import pandas as pd
import numpy as np
import re
import urllib.error
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import scipy.stats as stats
import pandas.api.types as ptypes
from typing import List, Union, Literal, Dict, Optional, Any

sns.set_theme(style="whitegrid")


# ==============================================================================
# SEKCJA 1: PRZYGOTOWANIE I CZYSZCZENIE DANYCH
# ==============================================================================

def _standaryzuj_nazwe_kolumny(nazwa: str) -> str:
    """
    Oczyszcza i standaryzuje nazwę pojedynczej kolumny.

    Zamienia wielkie litery na małe, usuwa znaki nowej linii i nawiasy,
    zamienia spacje na podkreślenia, a znaki procentów na ciąg 'perc'.

    Args:
        nazwa (str): Oryginalna nazwa kolumny.

    Returns:
        str: Ustandaryzowana nazwa kolumny.
    """
    nazwa = nazwa.lower().strip()
    nazwa = nazwa.replace('\n', '').replace(' ', '_').replace('(', '').replace(')', '').replace('%', 'perc')
    nazwa = nazwa.strip('_')
    return nazwa


def wczytaj_dane(sciezka: str) -> pd.DataFrame:
    """
    Wczytuje dane z pliku CSV lub URL i wykonuje ich podstawowe czyszczenie.

    Funkcja automatycznie standaryzuje nazwy kolumn, usuwa kolumnę 'rank'
    oraz konwertuje kolumny na odpowiednie typy numeryczne. Zawiera dedykowaną
    logikę dla pliku 'world_data.csv' obsługującą dane procentowe i przecinki.

    Args:
        sciezka (str): Ścieżka do pliku CSV lub bezpośredni link URL (np. GitHub RAW).

    Returns:
        pd.DataFrame: Oczyszczona ramka danych gotowa do analizy lub pusta ramka
        w przypadku błędu.
    """
    print(f"Wczytywanie danych z: {sciezka}...")
    try:
        df = pd.read_csv(sciezka)
        df.columns = [_standaryzuj_nazwe_kolumny(col) for col in df.columns]

        if 'rank' in df.columns:
            df = df.drop(columns=['rank'])

        kolumny_tekstowe = ['country', 'region', 'abbreviation']

        if 'world_data.csv' in sciezka:
            for col in df.columns:
                if col not in kolumny_tekstowe:
                    df[col] = pd.to_numeric(
                        df[col].astype(str).str.replace('%', '').str.replace(',', '.').str.strip(),
                        errors='coerce'
                    )
        else:
            for col in df.columns:
                if col not in kolumny_tekstowe:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

        if "year" in df.columns and pd.api.types.is_numeric_dtype(df["year"]):
            df["year"] = df["year"].astype('Int64')

        print("Wczytywanie i wstępne czyszczenie zakończone sukcesem.")
        return df

    except FileNotFoundError:
        print(f"BŁĄD: Plik o ścieżce '{sciezka}' nie został znaleziony.")
        return pd.DataFrame()
    except urllib.error.URLError as e:
        print(f"BŁĄD POBIERANIA: Nie można pobrać danych. Upewnij się, że używasz linku RAW. Szczegóły: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"BŁĄD: Wystąpił nieoczekiwany problem: {e}")
        return pd.DataFrame()


def polacz_dane(
        dane1: pd.DataFrame,
        dane2: pd.DataFrame,
        klucz: Union[str, List[str]],
        jak: Literal["inner", "left", "right", "outer"] = "inner"
) -> pd.DataFrame:
    """
    Łączy dwie ramki danych, rozwiązując konflikty typów w kolumnach kluczy.

    Args:
        dane1 (pd.DataFrame): Pierwsza (lewa) ramka danych.
        dane2 (pd.DataFrame): Druga (prawa) ramka danych.
        klucz (Union[str, List[str]]): Kolumna lub lista kolumn służących jako klucz łączenia.
        jak (Literal["inner", "left", "right", "outer"], opcjonalnie): Sposób łączenia.
            Domyślnie 'inner'.

    Returns:
        pd.DataFrame: Połączona ramka danych.

    Raises:
        ValueError: Jeśli wskazany klucz nie istnieje w którejkolwiek z ramek wejściowych.
    """
    df1 = dane1.copy()
    df2 = dane2.copy()

    df1.columns = [col.lower().strip() for col in df1.columns]
    df2.columns = [col.lower().strip() for col in df2.columns]

    standardized_keys = [klucz.lower().strip()] if isinstance(klucz, str) else [k.lower().strip() for k in klucz]

    for key in standardized_keys:
        if key not in df1.columns or key not in df2.columns:
            raise ValueError(f"Klucz '{key}' nie występuje w obu łączonych ramkach danych.")

    for key in standardized_keys:
        if df1[key].dtype != df2[key].dtype:
            try:
                df1[key] = pd.to_numeric(df1[key], errors='raise')
                df2[key] = pd.to_numeric(df2[key], errors='raise')
            except (ValueError, TypeError):
                df1[key] = df1[key].astype(str)
                df2[key] = df2[key].astype(str)

    merged_df = pd.merge(df1, df2, on=standardized_keys, how=jak)

    string_cols = ['country', 'region']
    for col in merged_df.columns:
        if col in string_cols:
            merged_df[col] = merged_df[col].astype(str)
        else:
            if col in standardized_keys and merged_df[col].dtype == 'object':
                continue
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')

    print("Operacja łączenia danych zakończona pomyślnie.")
    return merged_df


def usun_outliery(
        dane: pd.DataFrame,
        kolumny: Optional[List[str]] = None,
        wspolczynnik_iqr: float = 1.5
) -> pd.DataFrame:
    """
    Identyfikuje i usuwa wiersze zawierające wartości odstające metodą IQR.

    Args:
        dane (pd.DataFrame): Ramka danych do oczyszczenia.
        kolumny (Optional[List[str]], opcjonalnie): Lista kolumn numerycznych do analizy.
            Jeśli None, funkcja analizuje wszystkie dostępne kolumny numeryczne.
        wspolczynnik_iqr (float, opcjonalnie): Mnożnik definiujący czułość detekcji
            outlierów. Domyślnie 1.5.

    Returns:
        pd.DataFrame: Nowa ramka danych pozbawiona wierszy z outlierami.
    """
    df_roboczy = dane.copy()

    if kolumny is None:
        kolumny = df_roboczy.select_dtypes(include=np.number).columns.tolist()

    indeksy_do_usuniecia = set()

    for kolumna in kolumny:
        if not pd.api.types.is_numeric_dtype(df_roboczy[kolumna]):
            continue

        Q1 = df_roboczy[kolumna].quantile(0.25)
        Q3 = df_roboczy[kolumna].quantile(0.75)
        IQR = Q3 - Q1

        dolna_granica = Q1 - (wspolczynnik_iqr * IQR)
        gorna_granica = Q3 + (wspolczynnik_iqr * IQR)

        outliery = df_roboczy[(df_roboczy[kolumna] < dolna_granica) | (df_roboczy[kolumna] > gorna_granica)]
        indeksy_do_usuniecia.update(outliery.index)

    if indeksy_do_usuniecia:
        df_czyste = df_roboczy.drop(index=list(indeksy_do_usuniecia))
        print(f"Usunięto {len(indeksy_do_usuniecia)} wierszy zawierających wartości odstające.")
        return df_czyste

    print("Nie znaleziono wartości odstających. Zwracam oryginalną ramkę.")
    return df_roboczy


def usun_nan(dane: pd.DataFrame, kolumna: str) -> pd.DataFrame:
    """
    Usuwa wiersze z ramki danych, w których wskazana kolumna zawiera braki (NaN).

    Args:
        dane (pd.DataFrame): Wejściowa ramka danych.
        kolumna (str): Nazwa kolumny, według której filtrowane są braki.

    Returns:
        pd.DataFrame: Przefiltrowana ramka danych.
    """
    df_roboczy = dane.copy()
    fltr = df_roboczy[kolumna].notna()
    return df_roboczy[fltr]


def czyszczenie_procenty(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Przekształca kolumnę tekstową z danymi procentowymi na typ zmiennoprzecinkowy (float).

    Zastępuje przecinki kropkami oraz usuwa znaki procentów i białe znaki.

    Args:
        df (pd.DataFrame): Wejściowa ramka danych.
        col (str): Nazwa kolumny do konwersji.

    Returns:
        pd.DataFrame: Ramka danych ze zaktualizowaną kolumną.
    """
    df[col] = df[col].astype(str).str.replace('%', '', regex=False).str.strip()
    df[col] = df[col].str.replace(',', '.', regex=False)
    df[col] = df[col].astype(float)
    return df


# ==============================================================================
# SEKCJA 2: PRZEKSZTAŁCANIE I ANALIZA DANYCH
# ==============================================================================

def skategoryzuj_kolumne_numeryczna(
        dane: pd.DataFrame,
        nazwa_kolumny: str,
        grupy_niestandardowe: Optional[Dict[str, str]] = None,
        co_ile: Optional[int] = None
) -> pd.DataFrame:
    """
    Zamienia ciągłe wartości numeryczne w kolumnie na kategoryczne etykiety przedziałów.

    Args:
        dane (pd.DataFrame): Ramka danych poddawana transformacji.
        nazwa_kolumny (str): Nazwa kolumny z wartościami numerycznymi.
        grupy_niestandardowe (Optional[Dict[str, str]], opcjonalnie): Słownik precyzujący
            początki i końce przedziałów (np. {'0': '18', '19': '30'}).
        co_ile (Optional[int], opcjonalnie): Stała szerokość generowanych przedziałów.

    Returns:
        pd.DataFrame: Ramka danych ze zmienioną kolumną w formie stringów (etykiet).

    Raises:
        ValueError: Jeśli kolumna nie istnieje lub podano sprzeczne argumenty sterujące.
    """
    if nazwa_kolumny not in dane.columns:
        raise ValueError(f"Kolumna '{nazwa_kolumny}' nie istnieje w ramce danych.")

    if not ptypes.is_numeric_dtype(dane[nazwa_kolumny]):
        return dane.copy()

    if (grupy_niestandardowe and co_ile) or (not grupy_niestandardowe and not co_ile):
        raise ValueError("Musisz podać wyłącznie jeden argument kategoryzacji: 'grupy_niestandardowe' albo 'co_ile'.")

    df_roboczy = dane.copy()
    oryginalne_wartosci = pd.to_numeric(df_roboczy[nazwa_kolumny], errors='coerce')
    etykiety = oryginalne_wartosci.astype(str)

    if grupy_niestandardowe:
        for start_str, end_str in grupy_niestandardowe.items():
            try:
                start, end = int(start_str), int(end_str)
            except ValueError:
                raise ValueError(f"Słownik grup musi zawierać liczby. Błąd w: {start_str}:{end_str}")

            warunek = (oryginalne_wartosci >= start) & (oryginalne_wartosci <= end)
            etykiety.loc[warunek] = f"{start}-{end}"

    elif co_ile:
        wartosci_bez_nan = oryginalne_wartosci.dropna()
        start_przedzialu = (wartosci_bez_nan // co_ile) * co_ile
        koniec_przedzialu = start_przedzialu + co_ile - 1
        nowe_etykiety = start_przedzialu.astype(int).astype(str) + '-' + koniec_przedzialu.astype(int).astype(str)
        etykiety.loc[wartosci_bez_nan.index] = nowe_etykiety

    df_roboczy[nazwa_kolumny] = etykiety
    return df_roboczy


def filtruj_dane(dane: pd.DataFrame, filtry: Dict[str, List[Any]]) -> pd.DataFrame:
    """
    Filtruje ramkę danych na podstawie zdefiniowanego słownika warunków.

    Wszystkie warunki muszą zostać spełnione jednocześnie (logika AND).

    Args:
        dane (pd.DataFrame): Wejściowa ramka danych.
        filtry (Dict[str, List[Any]]): Słownik, gdzie klucz to kolumna, a wartość to
            lista [operator, wartość]. Dopuszczalne operatory to:
            '==', '=', '!=', '>', '>=', '<', '<=', 'in', 'not in'.

    Returns:
        pd.DataFrame: Przefiltrowana ramka danych.

    Raises:
        ValueError: W przypadku nieprawidłowej struktury filtra lub nieznanego operatora.
    """
    df_roboczy = dane.copy()

    for kolumna, warunek in filtry.items():
        if kolumna not in df_roboczy.columns:
            raise ValueError(f"Kolumna '{kolumna}' nie istnieje.")
        if not isinstance(warunek, list) or len(warunek) != 2:
            raise ValueError(f"Błędny format filtra dla '{kolumna}'. Oczekiwano: [operator, wartość].")

        operator, wartosc = warunek

        if operator in ['=', '==']:
            df_roboczy = df_roboczy[df_roboczy[kolumna] == wartosc]
        elif operator == '!=':
            df_roboczy = df_roboczy[df_roboczy[kolumna] != wartosc]
        elif operator == '>':
            df_roboczy = df_roboczy[df_roboczy[kolumna] > wartosc]
        elif operator == '>=':
            df_roboczy = df_roboczy[df_roboczy[kolumna] >= wartosc]
        elif operator == '<':
            df_roboczy = df_roboczy[df_roboczy[kolumna] < wartosc]
        elif operator == '<=':
            df_roboczy = df_roboczy[df_roboczy[kolumna] <= wartosc]
        elif operator.lower() == 'in':
            if not isinstance(wartosc, (list, tuple, set)):
                raise ValueError("Operator 'in' wymaga wartości w postaci listy lub krotki.")
            df_roboczy = df_roboczy[df_roboczy[kolumna].isin(wartosc)]
        elif operator.lower() == 'not in':
            if not isinstance(wartosc, (list, tuple, set)):
                raise ValueError("Operator 'not in' wymaga wartości w postaci listy lub krotki.")
            df_roboczy = df_roboczy[~df_roboczy[kolumna].isin(wartosc)]
        else:
            raise ValueError(f"Nieznany operator: '{operator}'.")

    return df_roboczy


def top10_wartosci(
        df: pd.DataFrame,
        col_text: str,
        col_value: str,
        granica: int = 10
) -> pd.DataFrame:
    """
    Wydziela wskazane N największych wartości i sumuje pozostałe do kategorii 'Inne'.

    Args:
        df (pd.DataFrame): Wejściowa ramka danych.
        col_text (str): Kolumna z danymi kategorycznymi (nazwami).
        col_value (str): Kolumna z danymi numerycznymi (wartościami).
        granica (int, opcjonalnie): Liczba unikalnych kategorii do zachowania. Domyślnie 10.

    Returns:
        pd.DataFrame: Podsumowana ramka danych przygotowana do wykresu kołowego.
    """
    grouped = df.groupby(col_text, as_index=False)[col_value].sum()
    sorted_df = grouped.sort_values(by=col_value, ascending=False)

    top_n = sorted_df.head(granica)
    others_sum = sorted_df[col_value].iloc[granica:].sum()

    if others_sum > 0:
        others_row = pd.DataFrame({col_text: ["Inne"], col_value: [others_sum]})
        return pd.concat([top_n, others_row], ignore_index=True)

    return top_n.reset_index(drop=True)


# ==============================================================================
# SEKCJA 3: WIZUALIZACJA DANYCH
# ==============================================================================

def wykres_liniowy(
        dane: pd.DataFrame,
        kolumna_1: str,
        kolumna_2: str,
        grupa: Optional[str] = None,
        rozmiar: tuple = (16, 9),
        paleta: str = "viridis",
        tytul: Optional[str] = None,
        ile_tickow_x: Optional[int] = None,
        ile_tickow_y: Optional[int] = None,
        tylko_calkowite_x: bool = False
) -> None:
    """
    Generuje estetyczny wykres liniowy ilustrujący rozwój zmiennej w relacji do innej.

    Args:
        dane (pd.DataFrame): Źródłowa ramka danych.
        kolumna_1 (str): Zmienna dla osi X.
        kolumna_2 (str): Zmienna dla osi Y.
        grupa (Optional[str], opcjonalnie): Zmienna kategoryczna dzieląca dane na serie.
        rozmiar (tuple, opcjonalnie): Rozmiar figury wykresu.
        paleta (str, opcjonalnie): Nazwa palety kolorów Seaborn.
        tytul (Optional[str], opcjonalnie): Niestandardowy tytuł wykresu.
        ile_tickow_x (Optional[int], opcjonalnie): Limit podziałek na osi X.
        ile_tickow_y (Optional[int], opcjonalnie): Limit podziałek na osi Y.
        tylko_calkowite_x (bool, opcjonalnie): Wymusza etykiety całkowite na osi X.
    """
    fig, ax = plt.subplots(figsize=rozmiar)
    fig.set_facecolor("white")
    ax.set_facecolor((0.95, 0.95, 0.97))

    if grupa:
        sns.lineplot(data=dane, x=kolumna_1, y=kolumna_2, hue=grupa, style=grupa,
                     markers=True, dashes=False, palette=paleta, linewidth=2.5,
                     legend=False, ax=ax)
        for kategoria in dane[grupa].unique():
            subset = dane[dane[grupa] == kategoria].sort_values(by=kolumna_1)
            if not subset.empty:
                last_point = subset.iloc[-1]
                ax.text(x=last_point[kolumna_1], y=last_point[kolumna_2],
                        s=f'  {kategoria}', fontsize=12, weight='medium', va='center')
        ax.set_xlim(dane[kolumna_1].min(), dane[kolumna_1].max() * 1.05)
    else:
        sns.lineplot(data=dane, x=kolumna_1, y=kolumna_2, markers=True,
                     linewidth=2.5, color=sns.color_palette(paleta, 1)[0], ax=ax)

    ax.set_title(tytul or f"Zależność '{kolumna_2}' od '{kolumna_1}'", fontsize=20, weight='bold', pad=20)
    ax.set_xlabel(kolumna_1.replace('_', ' ').capitalize(), fontsize=14, weight='semibold')
    ax.set_ylabel(kolumna_2.replace('_', ' ').capitalize(), fontsize=14, weight='semibold')

    ax.tick_params(axis='y', labelsize=12)
    ax.tick_params(axis='x', labelsize=12, rotation=45)
    plt.setp(ax.get_xticklabels(), ha="right")

    if ile_tickow_x:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=ile_tickow_x, integer=tylko_calkowite_x))
    if ile_tickow_y:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=ile_tickow_y))

    sns.despine(ax=ax)
    fig.tight_layout()
    plt.show()


def wykres_punktowy(
        dane: pd.DataFrame,
        kolumna_1: str,
        kolumna_2: str,
        grupa: Optional[str] = None,
        rozmiar_punktow_wg: Optional[str] = None,
        pokaz_trend: bool = False,
        rozmiar: tuple = (16, 9),
        paleta: str = "rainbow",
        tytul: Optional[str] = None,
        ile_tickow_x: Optional[int] = None,
        ile_tickow_y: Optional[int] = None
) -> None:
    """
    Rysuje wykres punktowy do analizy korelacji między dwiema zmiennymi numerycznymi.

    Args:
        dane (pd.DataFrame): Źródłowa ramka danych.
        kolumna_1 (str): Zmienna numeryczna osi X.
        kolumna_2 (str): Zmienna numeryczna osi Y.
        grupa (Optional[str], opcjonalnie): Kolumna kategoryczna do kolorowania punktów.
        rozmiar_punktow_wg (Optional[str], opcjonalnie): Kolumna sterująca średnicą punktów.
        pokaz_trend (bool, opcjonalnie): Włącza wyświetlanie linii regresji liniowej.
        rozmiar (tuple, opcjonalnie): Wymiary figury wykresu.
        paleta (str, opcjonalnie): Zestaw kolorów punktów.
        tytul (Optional[str], opcjonalnie): Niestandardowy tytuł.
        ile_tickow_x (Optional[int], opcjonalnie): Liczba podziałek osi X.
        ile_tickow_y (Optional[int], opcjonalnie): Liczba podziałek osi Y.
    """
    fig, ax = plt.subplots(figsize=rozmiar, constrained_layout=True)
    fig.set_facecolor("white")
    ax.set_facecolor((0.95, 0.95, 0.97))

    sns.scatterplot(
        data=dane, x=kolumna_1, y=kolumna_2, hue=grupa,
        size=rozmiar_punktow_wg, sizes=(50, 400) if rozmiar_punktow_wg else None,
        palette=paleta, alpha=0.8, legend="auto", ax=ax
    )

    if pokaz_trend:
        sns.regplot(data=dane, x=kolumna_1, y=kolumna_2, scatter=False, ax=ax,
                    color='darkgray', line_kws={'linestyle': '--'})

    ax.set_title(tytul or f"Zależność między '{kolumna_2}' a '{kolumna_1}'", fontsize=20, weight='bold', pad=20)
    ax.set_xlabel(kolumna_1.replace('_', ' ').capitalize(), fontsize=14, weight='semibold')
    ax.set_ylabel(kolumna_2.replace('_', ' ').capitalize(), fontsize=14, weight='semibold')
    ax.tick_params(axis='both', labelsize=12)

    if grupa or rozmiar_punktow_wg:
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    if ile_tickow_x: ax.xaxis.set_major_locator(MaxNLocator(nbins=ile_tickow_x))
    if ile_tickow_y: ax.yaxis.set_major_locator(MaxNLocator(nbins=ile_tickow_y))

    sns.despine(ax=ax)
    plt.show()


def wykres_babelkowy(
        dane: pd.DataFrame,
        kolumna_x: str,
        kolumna_y: str,
        kolumna_rozmiar: str,
        grupa: Optional[str] = None,
        rozmiar: tuple = (16, 10),
        max_rozmiar_babelka: int = 1500,
        paleta: str = "viridis",
        tytul: Optional[str] = None,
        ile_tickow_x: Optional[int] = None,
        ile_tickow_y: Optional[int] = None
) -> None:
    """
    Przedstawia wykres bąbelkowy pozwalający na ewaluację trzech zmiennych numerycznych.

    Args:
        dane (pd.DataFrame): Źródłowa ramka danych.
        kolumna_x (str): Zmienna numeryczna osi X.
        kolumna_y (str): Zmienna numeryczna osi Y.
        kolumna_rozmiar (str): Zmienna numeryczna determinująca pole bąbelka.
        grupa (Optional[str], opcjonalnie): Zmienna kategoryczna na bazie której dobierany jest kolor.
        rozmiar (tuple, opcjonalnie): Wymiary wykresu.
        max_rozmiar_babelka (int, opcjonalnie): Limit wielkości markera wykresu.
        paleta (str, opcjonalnie): Paleta barw.
        tytul (Optional[str], opcjonalnie): Niestandardowy tytuł widoku.
        ile_tickow_x (Optional[int], opcjonalnie): Liczba podziałek osi X.
        ile_tickow_y (Optional[int], opcjonalnie): Liczba podziałek osi Y.
    """
    fig, ax = plt.subplots(figsize=rozmiar, constrained_layout=True)
    fig.set_facecolor("white")
    ax.set_facecolor((0.95, 0.95, 0.97))

    sns.scatterplot(
        data=dane, x=kolumna_x, y=kolumna_y,
        size=kolumna_rozmiar, hue=grupa, palette=paleta,
        sizes=(20, max_rozmiar_babelka), alpha=0.7, legend="auto", ax=ax
    )

    ax.set_title(tytul or f"Wykres bąbelkowy '{kolumna_y}' vs '{kolumna_x}'", fontsize=20, weight='bold', pad=20)
    ax.set_xlabel(kolumna_x.replace('_', ' ').capitalize(), fontsize=14, weight='semibold')
    ax.set_ylabel(kolumna_y.replace('_', ' ').capitalize(), fontsize=14, weight='semibold')
    ax.tick_params(axis='both', labelsize=12)

    if grupa or kolumna_rozmiar:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    if ile_tickow_x: ax.xaxis.set_major_locator(MaxNLocator(nbins=ile_tickow_x))
    if ile_tickow_y: ax.yaxis.set_major_locator(MaxNLocator(nbins=ile_tickow_y))

    sns.despine(ax=ax)
    plt.show()


def wykres_korelacji(
        dane: pd.DataFrame,
        rozmiar: tuple = (12, 10),
        paleta: str = "coolwarm",
        tytul: Optional[str] = None
) -> None:
    """
    Tworzy maskowaną mapę ciepła ilustrującą współczynniki korelacji Pearsona
    dla wszystkich numerycznych zmiennych w zbiorze.

    Args:
        dane (pd.DataFrame): Analizowany zestaw danych.
        rozmiar (tuple, opcjonalnie): Obszar rysowania macierzy.
        paleta (str, opcjonalnie): Paleta kolorów wskazująca wariancję zjawiska.
        tytul (Optional[str], opcjonalnie): Tytuł własny.
    """
    df_numeryczne = dane.select_dtypes(include=np.number)

    if df_numeryczne.shape[1] < 2:
        print("Brak minimum dwóch zmiennych numerycznych w zbiorze wejściowym.")
        return

    macierz_korelacji = df_numeryczne.corr(method='pearson')
    maska = np.zeros_like(macierz_korelacji, dtype=bool)
    maska[np.triu_indices_from(maska)] = True

    fig, ax = plt.subplots(figsize=rozmiar, constrained_layout=True)
    fig.set_facecolor("white")

    sns.heatmap(
        macierz_korelacji, mask=maska, cmap=paleta, annot=True,
        fmt=".2f", linewidths=.5, vmin=-1, vmax=1,
        cbar_kws={"shrink": .8}, ax=ax
    )

    ax.set_title(tytul or "Korelogram zmiennych numerycznych", fontsize=18, weight='bold', pad=20)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    plt.show()


def tabela_korelacji(
        dane: pd.DataFrame,
        kolumny: List[str],
        prog_korelacji: Optional[float] = None,
        rozmiar: tuple = (8, 12),
        paleta: str = "coolwarm",
        tytul: Optional[str] = None
) -> None:
    """
    Filtruje macierz korelacji do sprecyzowanych kolumn docelowych w zestawieniu
    ze wszystkimi pozostałymi zmiennymi numerycznymi.

    Args:
        dane (pd.DataFrame): Zestaw badawczy.
        kolumny (List[str]): Lista zmiennych do ujęcia na osi poziomej.
        prog_korelacji (Optional[float], opcjonalnie): Minimalna wartość bezwzględna
            korelacji, poniżej której komórki zostaną pozbawione danych barwnych.
        rozmiar (tuple, opcjonalnie): Wymiary figury okna wykresu.
        paleta (str, opcjonalnie): Wykorzystana kolorystyka mapy.
        tytul (Optional[str], opcjonalnie): Niestandardowy tytuł.

    Raises:
        ValueError: Jeśli zestaw podanych kolumn jest błędny.
    """
    df_numeryczne = dane.select_dtypes(include=np.number)
    kolumny_docelowe = [kol for kol in kolumny if kol in df_numeryczne.columns]

    if not kolumny_docelowe:
        raise ValueError("Brak zadeklarowanych kolumn numerycznych.")

    macierz_korelacji_pelna = df_numeryczne.corr(method='pearson')
    tabela_do_wizualizacji = macierz_korelacji_pelna[kolumny_docelowe].sort_index()

    if prog_korelacji is not None:
        tabela_z_nan = tabela_do_wizualizacji.copy()
        tabela_z_nan[np.abs(tabela_do_wizualizacji) < prog_korelacji] = np.nan
    else:
        tabela_z_nan = tabela_do_wizualizacji

    fig, ax = plt.subplots(figsize=rozmiar, constrained_layout=True)
    fig.set_facecolor("white")

    sns.heatmap(
        tabela_z_nan, cmap=paleta, annot=True, fmt=".2f",
        linewidths=.5, vmin=-1, vmax=1,
        cbar_kws={"shrink": .8, "label": "Korelacja Pearsona"}, ax=ax
    )

    tytul_koncowy = tytul or "Tabela korelacji ze zmiennymi docelowymi"
    if prog_korelacji: tytul_koncowy += f"\n(pokazano >= |{prog_korelacji}|)"
    ax.set_title(tytul_koncowy, fontsize=18, weight='bold', pad=20)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    plt.show()


def wykres_kolowy(
        df: pd.DataFrame,
        category_col: str,
        value_col: str,
        rozmiarx: int = 8,
        rozmiary: int = 10
) -> None:
    """
    Przedstawia wykres segmentowy udziału zdefiniowanych kategorii względem miary sumarycznej.

    Args:
        df (pd.DataFrame): Źródło danych (optymalnie pre-agregowane do limitu grup).
        category_col (str): Wskazanie kolumny kategorycznej.
        value_col (str): Wskazanie miary numerycznej.
        rozmiarx (int, opcjonalnie): Szerokość panelu.
        rozmiary (int, opcjonalnie): Wysokość panelu.
    """
    data = df.groupby(category_col)[value_col].sum()
    fig, ax = plt.subplots(figsize=(rozmiarx, rozmiary))

    ax.pie(data.values, labels=data.index, autopct='%1.1f%%', startangle=90)
    ax.set_title(f"Rozkład '{category_col}' z wykorzystaniem '{value_col}'", pad=20, weight='bold', fontsize=16)
    plt.axis('equal')
    plt.show()


def wykres_histogram(
        df: pd.DataFrame,
        col: str,
        bins: int = 10,
        rozmiarx: int = 8,
        rozmiary: int = 10
) -> None:
    """
    Tworzy wykres częstości występowania określonych wartości (histogram) dla cechy numerycznej.

    Args:
        df (pd.DataFrame): Repozytorium cech wejściowych.
        col (str): Badana metryka ciągła lub dyskretna.
        bins (int, opcjonalnie): Ilość interwałów (tzw. "koszyków"). Domyślnie 10.
        rozmiarx (int, opcjonalnie): Pozioma przestrzeń robocza.
        rozmiary (int, opcjonalnie): Pionowa przestrzeń robocza.
    """
    fig, ax = plt.subplots(figsize=(rozmiarx, rozmiary))
    ax.hist(df[col].dropna(), bins=bins, edgecolor='black', alpha=0.7)

    ax.set_title(f'Histogram rozkładu: {col}', pad=20, weight='bold', fontsize=16)
    ax.set_xlabel(col.replace('_', ' ').capitalize(), fontsize=12)
    ax.set_ylabel('Częstotliwość agregacji', fontsize=12)
    plt.show()

# ==============================================================================
# KONIEC PLIKU NARZĘDZIOWEGO
# ==============================================================================