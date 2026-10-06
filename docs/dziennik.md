# Dziennik dzień 1 (git)

**Co zrobiłem:**
- Dział main i remote na Learn Git Branching
- Repo poznan-it-market, przeszedłem przez branch, commit, PR i merge do main
- Przećwiczyłem konflikt merge na dwóch gałęziach i rozwiązałem go
- Dodałem plik .gitignore z regułami

**Komendy dnia:**
- branch, checkout -b, commit, merge, rebase, add, push, pull, fetch, reset, log, clone, status


**Co mnie wciągnęło:** 
- możliwość komunikowania się z githubem za pomocą cmd i satysfakcja z widzenia zmian

**Co mnie męczyło:**
- zbyt zaawansowane niektóre zadania na Learn Git  Branching, mieszanie się komend, dużo naraz

**Wnioski:**
- bardziej się skupiać na rzeczach istotnych, oswoić się bardziej z cmd

**Czas:** 8h | **Ocena dnia:**  2.5/5


# Dziennik dzień 2 (terminal fundamenty)

**Co zrobiłem:**
- wyklad MIT (shell,command-line environment,data wrangling)
- nauka z jq z jqlang.org
- pobranie strone z API i drobne zadania na niej

**Komendy dnia:**
- jq, grep, sed, sort, uniq, git config, cp, sed -i

**Co mnie wciągnęło:**
- możliwość komunikowania się z serwerem za pomocą Ubuntu, ekstracja i filtrowanie danych

**Co mnie męczyło:**
- problem z dwoma folderami na komputerze- pochłonęło mi to więcej czasu niż ćwiczenie jq, zbyt zaawansowane niektóre zadania, mieszanie się wyrażeń, dużo naraz

**Wnioski:**
- trzymać repo w jednym miejscu od początku, sprawdzać strukturę json częściej i testować ją

**Czas:** 7h | Ocena dnia: 4/5

# Dziennik dzień 3 (środowisko pythona i pierwszy sktypt)

**Co zrobiłem:**
- wyklad MIT (packaging and shipping code)
- napisalem fetch_sample
- żadanie httpx z własnym user-agentem oraz zapis do pliku danych uzyskanych
- trzy obserwacje o api
- import konfiguracji z poznan_it_market.config

**Komendy dnia:**
- export JJIT_API_URL="https://justjoin.it/api/candidate-api/offers", uv run python scripts/fetch_sample.py

**Co mnie wciągnęło:**
- zderzenie z API, stosowanie pythona

**Co mnie męczyło:**
- problem z endpointem,naprawda błędów w fetch_sample.py, zmienianie calych plikow na jezyk angielski, nadmiar materiału, dużo kroków

**Wnioski:**
- upewnianie się, że biorę dobry enpoint, pisanie wszystkiego poza dziennikiem po angielsku, sprawdzanie więcej dokumentacji

**Czas:** 8h | Ocena dnia: 3.5/5


# Dziennik dzień 4 (testy)

**Co zrobiłem:**
- wykład MIT (lec 9, code quality)
- testy fetch_sample 
- uruchomilem mypy src, zero blędów
- uruchomilem pytest --cov=src, 97% pokrycia

**Komendy dnia:**
- uv run pytest --cov=src, monkeypatch, mypy src

**Co mnie wciągnęło:**
- testy bez internetu, testowanie is_main_location

**Co mnie męczyło:**
- setup mockow, błędy ogólne

**Wnioski:**
- nie skupiac sie na 100% pokrycia 

**Czas:** 9h | **Ocena dnia:**  3.5/5


# Dziennik dzień 5 (CI i domknięcie tygodnia)

**Co zrobiłem:**
- pierwszy workflow github actions
- zaktualizowałem README
- naprawiałem błędy związa z github actions, aby uzyskać zielony przebieg
- dodałem licencję MIT
- włączyłem opcję, aby od teraz pracować przez branche i PR

**Komendy dnia:**
- git checkout -b, git push -u origin, uv run mypy src, ruff format --check

**Co mnie wciągnęło:**
- gdy pierwszy przebieg zrobił się zielony po czterech rundach poprawek, poprawianie struktury mojego projektu

**Co mnie męczyło:**
- cztery rundy poprawek i commitów pod rząd związane z github actions

**Wnioski:**
- branch protection rzeczywiście blokuje merge, uv run jest konieczny, poniewaz (np ruff, mypy) nie są zainstalowane globalnie

**Czas:** 4h | **Ocena dnia:** 4/5

# Dziennik dzień 6 (Postgres w kontenerze i JOIN-y)

**Co zrobiłem:**
- utworzyłem sql/exercises i zrobilem zadania z sql
- skonfigurowalem i uruchomilem docker compose
- zaladowalem pagille i przeanalizowalem tam ralacje

**Komendy dnia:**
- make db-up, make db-shell, make db-reset, docker compose down, cross join

**Co mnie wciągnęło:**
- uczenie się sql i odkrywanie nowych metod rozwiązania
- tzw self join

**Co mnie męczyło:**
- niektóre zadania z sql były zbyt zaawansowane, poruszanie się w pegilii i przenoszenie danych bez wcześniejszego doświadczenia

**Wnioski:**
- makefile przyśpiesza pracę, przyłożyć się do sql

**Czas:** 7h | **Ocena dnia:** 4/5

# Dziennik dzień 7 (Agregacje i CTE)

**Co zrobiłem:**
- zrobiłem zadania z agregates i recursive
- zrozumiałem jak ważne jest CTE 
- zrozumialem wiele funkcji w sql
- zrobiłem kalendarz wykorzystując recursive

**Komendy dnia:**
- with recursive, leteral, having, rollup, cube

**Co mnie wciągnęło:**
- niektóre zadania, zrozumienie tego jak ważne jest with z CTE, generowanie danych z dim_date

**Co mnie męczyło:**
-niektóre zadania zbyt zaawansowane, zrozumienie rekurancji, zrozumienie struktury sql (nie po kolei czyta on linijki), zrozumienie kolejności logiki przetważania danych tzw. FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY

**Wnioski:**
- jeśli zadanie jest zbyt cieżkie nalezy przede wszystkim je zrozumieć, uzywac CTE

**Czas:** 9h | **Ocena dnia:** 3/5

# Dziennik dzień 8 (funkcje okna)

**Co zrobiłem:**
- pytania do pagilii (sumy, obroty itp.)
- nauczylem sie wiele funkcji (np. FIRST_VALUE, LAST_VALUE, NTH_VALUE, NTILE)

**Komendy dnia:**
- with, group by, \dt, round, to_char

**Co mnie wciągnęło:**
- nauka nowych funkcji, satysfakcja z działającego kodu

**Co mnie męczyło:**
- błędy składniowe, zaawansowaność niektórych pytań

**Wnioski:**
- CTE jest ważne, funkcja okna potrafi rozwiązać łatwiej problem

**Czas:** 8h | **Ocena dnia:** 2.5/5

# Dziennik dzień 9 (porządki i jsonb)

**Co zrobiłem:**
- test api- błąd 503
- aktualizacja readme.md
- napisałem 3 pytania sql na jsonb
- dodałem ADR-1

**Komendy dnia:**
- `payload->>'companyName', `jsonb_array_elements(payload->'requiredSkills')`, `(payload->>'publishedAt')::timestamptz AT TIME ZONE 'Europe/Warsaw'

**Co mnie wciągnęło:**
- Korzystanie z sql na prawdziwych ofertach pracy i uzyskiwanie wyników odnośnie np top 10 firm.

**Co mnie męczyło:**
- rozróżnianie ->, a ->>, wgranie próbki.

**Wnioski:**
-  `->` zwraca `jsonb`, a `->>` zwraca `text`, zawsze trzeba jak najbardziej rozpakować dane, daty przechowywać w timestamptz.


**Czas:** 4h | **Ocena dnia:** 4/5

# Dziennik dzień 10 (upsert)

**Co zrobiłem:**
- przetestowalem dzialanie insert, on conflict, do nothing, do update set
- zrobiłem docelowy schemat sql/ddl/001_raw_schema.sql
- przetestowalem obslugę duplikatow przy ponownym uruchomieniu pipeline 

**Komendy dnia:**
- insert into, on conflict, do update set

**Co mnie wciągnęło:**
- odkrycie pułapki null (WAŻNE NOT NULL), zrozumienie co to idempotencja i zastosowanie tego (przy uruchamianiu pipelinów stan systemu bedzie taki sam zawsze) 

**Co mnie męczyło:**
- złożoność schematu docelowego, błędy składniowe

**Wnioski:**
- do update uzywamy, gdy chcemy podmienic wartosc o tym samym np id, do nothing służy, do zachowania pierwszego zarejestowania po danym id

**Czas:** 4h | **Ocena dnia:** 3.5/5


# Dziennik dzień 11 (indexy i plany zapytań)

**Co zrobiłem:**
- powiększyłem testy do +/- 100tyś używając generate_series 
- poznałem strukturę b-tree i regułę lewego prefixu
- zoptymalizowalem zapytania uzywając indexa o x20

**Komendy dnia:**
- ANALYZE, EXPLAIN (ANALYZE, BUFFERS), CREATE INDEX, generate_series(1, 200) g

**Co mnie wciągnęło:**
- satysfakcja z optymalizacji, użycie ANALYZE

**Co mnie męczyło:**
- składnia, pojęcie niektórej teorii (b-tree,lewy prefix)

**Wnioski:**
- ANALYZE jest ważne, dla dużych wyników baza automatycznie bierze bitmap scan, konieczne są podwójne nawiasy przy wyciąganiu pól w indexie

**Czas:** 4h | **Ocena dnia:** 4/5

# Dziennik dzień 12 (Rozpoznanie API)

**Co zrobiłem:**
- w devtools zbadałem maksymalny rozmiar strony, zachowanie api przy przekroczeniu zakresu.
- przeanalizowałem strukturę lokalizacji ofert i podjąłem decyzję które oferty odrzucam
- sprawdziłem nagłówki pod kątem rate limitów

**Komendy dnia:**
- SELECT count(*) FROM scratch.offers_sample WHERE payload->'locations'->0->>'city' = 'Poznań';

**Co mnie wciągnęło:**
- odkrycie kiedy serwer zwraca błąd, zdanie sobie sprawy ile odrzuciłem ofert

**Co mnie męczyło:**
- opisywanie w dokumentacji, rozpozanie api

**Wnioski:**
- pętlę pobierania musimy zatrzymać na podstawie meta.next.cursor is null, trzeba ograniczenia pilnować samemu (brak rate limit)

**Czas:** 4h | **Ocena dnia:** 3/5

# Dziennik dzień 13 (klient http)

**Co zrobiłem:**
- Konfiguracja httpx.Client z user-agent
- fetch_justjoinit_pages jako yield z max_pages i odstępem time.sleep
- funkcja save_raw_pages zapisująca odpowiedzi do data/raw/YYYY-MM-DD/page_NNN.json (odporność na wywalenia)
- testy pytest z httpx.MockTransport (ponowienie przy 500, przerwanie przy 404)

**Komendy dnia:**
- pytest tests/test_client.py

**Co mnie wciągnęło:**
- testy bez łączenia z siecią

**Co mnie męczyło:**
- Zaawansowaność funkcji, ilość nowych rzeczy, funkcji. Przesyt nowej wiedzy

**Wnioski:**
- Skupić się na powtórce, upraszczać jak najbardziej, błędy 4xx bez ponawiania (marnowanie zasobów), yield zapobiega zapychaniu ram przy duzym pobieraniu

**Czas:** 5.5h | **Ocena dnia:** 2/5

# Dziennik dzień 14 (walidacja i odrzuty)

**Co zrobiłem:**
- implementacja model RawOffer w Pydantic v2.
- tabela raw.rejected_records do zapisu błędnych payloadow
- 3 iteracje walidacji na danych
- testy i zestaw testow jednostykowych 

**Komendy dnia:**
- uv run python scripts/validate_sample.py, uv run pytest tests/test_models.py

**Co mnie wciągnęło:**
- Kontrolowanie odrzucanych błędów, przez co nic nie ginie. 

**Co mnie męczyło:**
- Składnia niektórych funkcji, nowe rzeczy

**Wnioski:**
- słowa kluczowe dla pythona wymagają validation_alias, nie mozna odrzucac i usuwac błędów, bo mogą się do czegoś przydać
**Czas:** 4h | **Ocena dnia:** 4/5

# Dziennik dzień 15 (ładowanie i historia przebiegów)

**Co zrobiłem:**
- loader w psycopg 3
- tabela metadanych rejestrująca stan, czas trwania i liczba ofert
- spiełem pobieranie, audyt i ładowanie w jedną funkcję 

**Komendy dnia:**
- uv run python -m poznan_it_market.ingest.loader, docker compose exec -T db psql -U postgres -d poznan_it_market < sql/ddl/001_raw_schema.sql

**Co mnie wciągnęło:**
- satysfakcja z skrypt rejestruje stan rzeczywisty i dane

**Co mnie męczyło:**
- zaawansowaność kodu, funkcji, błędy z postgresql

**Wnioski:**
- Skupić się na nauce, tabela metadanych jest ważna do rejestrowania statusu i odróżnić trendy rynkowe

**Czas:** 4.5h | **Ocena dnia:** 3.5/5

# Dziennik dzień 16 (Idempotentoność)

**Co zrobiłem:**
- dezycja dotycząca zapisów duplikatów
- 3 testy idempotentności (brak duplikatów (i aktualizowanie), status failed przy przerwaniu, poprawne ponowne zczytywanie)

**Komendy dnia:**
- make ingest, uv run pytest tests/test_loader_idempotency.py -v

**Co mnie wciągnęło:**
- prosty temat i zrozumiały, stabilność pipeline 

**Co mnie męczyło:**
- błędy przy obaleniu testów

**Wnioski:**
- Idempotentność jest ważna, pipeline musi być bezpieczny przy ponownych uruchomienach.

**Czas:** 3h | **Ocena dnia:** 4/5

# Dziennik dzień 17 (Model danych i dbt)

**Co zrobiłem:**
- 5 pytań biznesowych
- ziarno tabeli faktów, diagram encji
- czytanie teorii Kiballa, zasady dbt style
- konfiguracja profiles.yml

**Komendy dnia:**
- uv add dbt-core dbt-postgres, dbt init, dbt debug

**Co mnie wciągnęło:**
- dobór najciekawszych pytań biznesowych 

**Co mnie męczyło:**
- teoria, nowa struktura, konieczność powtarzania

**Wnioski:**
- przykładać więcej uwagi, standardy nazewnictwa są ważne, pytania biznesowe i definicja ziarna są ważne.

**Czas:** 4h | **Ocena dnia:** 3.5/5

# Dziennik dzień 18 (Warstwa staging)

**Co zrobiłem:**
- model stagingowy i rozpakowałem dane, znormalizowałem widełki, dodałem flagę, przeniosłem logikę filtrowania lokalizacji z pythona do sql
- weryfikacja wierszy (widok poprawnie odrzucił dane)

**Komendy dnia:**
- uv run dbt compile, uv run dbt run

**Co mnie wciągnęło:**
- zrozumienie prostoty widoku za pomocą sql

**Co mnie męczyło:**
- błędy, składnia sql, struktura danych

**Wnioski:**
- patrzec uwazniej na strukture danych, dbt compile sprawdza linia po linie, a dbt run wysyla kod do postgresql, gdzie baza weryfikuje poprawnosc (bardziej zaawansowane)
**Czas:** 4h | **Ocena dnia:** 4/5

# Dziennik dzień 19 (Warstwa marts)

**Co zrobiłem:**
- model wymiaru z md5
- imprementacja głownej tabeli faktów
- przygotowałem 3 pytania analityczne w sql 

**Komendy dnia:**
- uv run dbt run --select stg_offers

**Co mnie wciągnęło:**
- proste pytania w sql

**Co mnie męczyło:**
- ciężkie pytania w sql

**Wnioski:**
- stałe dane trzymamy jako table, nie view
- W tabeli faktów technologie musza byc w osobnej tabeli 

**Czas:** 4h | **Ocena dnia:** 4/5

# Dziennik dzień 20 (Model przyrostowy)

**Co zrobiłem:**
- przekształciłem model na `incremental` z kluczem na `unique_key=['date_id', 'raw_offer_id']` i filtrem `fetched_at`.
- sumylacja drugiego dnia danych w warstwie surowej i potwierdzilem braku duplikatów.
- wpis w adr.

**Komendy dnia:**
- `uv run dbt run --select fct_offer_snapshot`, `uv run dbt run --select +fct_offer_snapshot --full-refresh`

**Co mnie wciągnęło:**
- Spadek wykonywania czasu zapytania i satysfakcja z kolejnych kroków.

**Co mnie męczyło:**
- błędy z pustą tabelą, logiką sql, błąd postsql

**Wnioski:**
- model `incremental` jest efektywny, ale wrażliwy na zmiany, trzeba pamiętac o używaniu raz w tygodniu `--full-refresh` dla poprawy logiki danych.

**Czas:** 4h | **Ocena dnia:** 3.5/5

# Dziennik dzień 21 (SCD type 2)

**Co zrobiłem:**
- scd type 2 do śledzenia zmian w ofertach
- konfiguracja snap_offers.sql z check w płacach 
- zapytanie sql ze zmianą płac

**Komendy dnia:**
- `uv run dbt snapshot`.  `LAG(salary_from) OVER (PARTITION BY source_offer_id ORDER BY dbt_valid_from)`

**Co mnie wciągnęło:**
- satysfaskcja z poprawnych wyników komend

**Co mnie męczyło:**
- zapomnienie o `make ingest`, składnia sql i błędy, poprawne odwołania do kolumn

**Wnioski:**
- skupiać się bardziej, snapshot musi zostac uruchomiony przed nadpisaniem nowymi danymi

**Wyniki dzisiejszego zapytania**
| source_offer_id | company_name | old_salary_from | old_salary_to | new_salary_from | new_salary_to | changed_at |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `upvanta-sp-z-o-o--operator-monitoringu-systemow-i-sieci-specjalista-noc-network-operations-center---poznan-poznan-admin` | Upvanta sp. z o.o. | 5275.0 | 5275.0 | 25000 | 35000 | 2026-09-27 18:00:45.696034 |

**Czas:** 3.5h | **Ocena dnia:** 3.5/5

# Dziennik dzień 22 (Testy dbt i dokumentacja)

**Co zrobiłem:**
- testy dbt unique, not_null, relationships w yaml
- test sql weryfikujący logikę biznesową płac
- dbt build do github actions
- zdjęcie grafu lini danych 

**Komendy dnia:**
- `uv run dbt test --select stg_offers`, `uv run dbt test --select marts`

**Co mnie wciągnęło:**
- wizualizacja architektury w lineage graph

**Co mnie męczyło:**
- złożoność struktury, natłok wiedzy, zapisywanie obrazu do wsl

**Wnioski:**
- dbt zwraca efekty testów poprzez zwracanie tylko odrzuconych ofert, pozwala to szybko namierzyć błąd i ewentualnie manualnie wpiąć ofertę do bazy

**Czas:** 4.5h | **Ocena dnia:** 3/5

# Dziennik dzień 23 (Baza w chmurze)

**Co zrobiłem:**
- konfiguracja chmury i założenie bazy
- aplikacja sktyptów warstwy surowej do chmury przez `psql`
- test chmury z ładowaniem danych i testami
- analiza limitu darmowego, obliczenie, że dziennie będzie zabierać do 1.2mb i dostosowanie modelu do limitu za pomocą polecenia sql

**Komendy dnia:**
- `psql "$DATABASE_URL" -f sql/ddl/001_raw_schema.sql`, `set -a && source .env && set +a`

**Co mnie wciągnęło:**
- Satysfakcja z optymalizacji danych w chmurze, zobaczenie jak wszystko przechodzi na zdalnym silniku. 

**Co mnie męczyło:**
- Problem ze zmiennymi, problem z konfiguracją chmury.

**Wnioski:**
- dawać adresy z parametrami w .env w cudzysłowach. Trzymanie w chmurze w nieskończoność danych to strata zasobów (tym bardziej, że wszystko się zapisuje w warstwie marts).

**Czas:** 4h | **Ocena dnia:** 4/5

# Dziennik dzień 24 (Automatyzacja w Github Actions)

**Co zrobiłem:**
- automatyzacja w Github Actions wykonujący się codziennie o 6:00 CET
- implementacja zabiezpieczeń przed awarią 
- zapisanie decyzji artefaktów
- naprawa makefile i błędów

**Komendy dnia:**
- cd dbt && uv run dbt build --full-refresh --profiles-dir .

**Co mnie wciągnęło:**
- satysfakcja z zielonego przebiegu w github actions 

**Co mnie męczyło:**
- naprawa zmiennych, naprawa błędów, natłok błędów

**Wnioski:**
- Github Actions jest prosty, optymalny kosztowo i czasowo. Dla mojego projektu najlepiej się on nada, gdzie pipeline działa ~3 min dziennie.

**Czas:** 3.5h | **Ocena dnia:** 3.5/5

# Dziennik dzień 25 (Testy jakości danych)

**Co zrobiłem:**
- Test świeżości źródła dbt z progiem ostrzeżenia na 26h.
- test sql na anomalie ilościowe (np spadek dziennej liczby ofert poniezej 60%)
- dokumentacja z tlumaczeniem progów i zatrzymania pipelinów
- Tabela w neonie do logów ofert i monitorowania jakości danych
- kontrolowana awaria

**Komendy dnia:**
- `uv run dbt test --select assert_daily_offers_completeness`

**Co mnie wciągnęło:**
- satysfakcja z działających testów implementowanie i łatwa modyfikacja ich

**Co mnie męczyło:**
- Błędy, próba łączenia z chmurą przez konsolę

**Wnioski:**
- Najlepiej jest przetestować najpierw test np za pomocą sztucznych danych. 26 godziny czekania to próg limitu, aby nie dostawać sztucznych alertów o awariach.

**Czas:** 3.5h | **Ocena dnia:** 4/5

# Dziennik dzień 26 (Wykresy i README)

**Co zrobiłem:**
- implementacja `scripts/make_charts.py` w matplotlib
- 4 wykresy do `docs/img/`
- aktualizacja README.md
- wpięcie automatycznego odświerzania wykresów

**Komendy dnia:**
- `make charts`, `uv run python scripts/make_charts.py`

**Co mnie wciągnęło:**
- Zobaczenie wykresów w dokumentacji

**Co mnie męczyło:**
- Skomplikowaność poleceń i natłok wiedzy, matplotlib

**Wnioski:**
- Dokumentacja techniczna jest ważna. Jest wizytówką projektu.

**Czas:** 5h | **Ocena dnia:** 3/5

# Dziennik dzień 27 (ADR,klon projektu, v1.0)

**Co zrobiłem:**
- uporządkowanie 8 decyzji architektonicznych
- test świerzego klona i uzupełniłem README i poprawiłem błędy
- test pipeline od zera
- wydanie v1.0

**Komendy dnia:**
- `git clone . /tmp/poznan-it-market-fresh`, `git tag -a v1.0`

**Co mnie wciągnęło:**
- test świerzego klona

**Co mnie męczyło:**
- awaria github actions, błędy w klonie

**Wnioski:**
- ważne są testy na klonach, projekt jest domnięty i cały plan jest ukończony. Zostały lekkie modyfikacje i usprawnienia lekkie.

**Czas:** 4h | **Ocena dnia:** 3/5
