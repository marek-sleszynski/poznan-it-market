# Dziennik 03.08.2026 - dzień 1 (git)

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


# Dziennik 04.08.2026 - dzień 2 (terminal fundamenty)

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

# Dziennik 05.08.2026 - dzień 3 (środowisko pythona i pierwszy sktypt)

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


# Dziennik 06.08.2026 - dzień 4 (testy)

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


# Dziennik 07.08.2026 - dzień 5 (CI i domknięcie tygodnia)

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

# Dziennik 10.08.2026 - dzień 6 (Postgres w kontenerze i JOIN-y)

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

# Dziennik 11.08.2026 - dzień 7 (Agregacje i CTE)

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

# Dziennik 12.08.2026 - dzień 8 (funkcje okna)

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

# Dziennik dzień 1 (porządki i jsonb)

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

# Dziennik dzień 2 (upsert)

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


# Dziennik dzień 3 (indexy i plany zapytań)

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
