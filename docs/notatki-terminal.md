1. Podstawowe komendy i wieloznaczniki (globs)
ls — wypisuje zawartość katalogu

mkdir — tworzy folder

touch — tworzy plik

rm — usuwa plik

* — zastępuje dowolny ciąg znaków, np. rm *.py usuwa wszystkie pliki Pythona w folderze

{} — "rozmnaża" komendy, np. touch raport_{pon,wt,sr}.txt tworzy od razu trzy pliki

2. Strumienie danych i przekierowania
> (nadpisz) — kieruje wynik do pliku, niszcząc jego poprzednią zawartość, np. echo "Start" > plik.txt

>> (dopisz) — kieruje wynik na koniec pliku, bez niszczenia starych danych

2> (błędy) — przechwytuje wyłącznie ostrzeżenia i błędy z programu

/dev/null — systemowa "czarna dziura"; komenda > /dev/null 2>&1 całkowicie wycisza program

3. Zmienne środowiskowe i ścieżki
zmienna=wartosc — tworzenie zmiennej (nigdy spacji wokół =)

$zmienna — odczyt wartości

export PATH="$PATH:/nowy/folder/z/programami" — dodanie nowej ścieżki do $PATH

" " czyta zmienne wewnątrz tekstu, ' ' traktuje tekst w 100% dosłownie

4. Kody powrotu i logika zdarzeń
$? — kod wyjścia ostatniej komendy: 0 = sukces, inna wartość = błąd

&& (AND) — uruchamia drugą komendę tylko, gdy pierwsza się powiodła

|| (OR) — uruchamia drugą komendę tylko, gdy pierwsza zakończyła się błędem

5. Zarządzanie procesami (praca w tle)
Ctrl+C — zabija bieżący program

Ctrl+Z — zamraża bieżący program

jobs — pokazuje zamrożone/działające w tle zadania

bg 1 / fg 1 — wznawia zadanie nr 1 w tle / przywraca na pierwszy plan

nohup komenda & — uruchamia program w tle, odporny na zamknięcie terminala

pgrep nazwa + kill 1234 (lub kill -9 1234) — znajdowanie i zabijanie procesu

6. Praca na zdalnych serwerach (SSH)
ssh uzytkownik@adres_serwera — logowanie

ssh-keygen -t ed25519 — generowanie klucza

ssh-copy-id uzytkownik@adres_serwera — logowanie bez hasła od tej pory

scp plik.txt uzytkownik@adres:/folder/ — kopiowanie plików przez sieć

7. Multiplekser terminala (tmux)
tmux new -s nazwa — nowa sesja

tmux a — przywrócenie odłączonej sesji

Ctrl+B, % / Ctrl+B, " — podział ekranu w pionie / poziomie

Ctrl+B, d — odłączenie sesji

8. Aliasy
alias wylicz="Rscript dlugi_skrypt.R --flagi"

alias rm="rm -i" — wymusza pytanie o zgodę przy usuwaniu

Część II: obróbka danych (data wrangling)
1. Rury / potoki (|)
Łączą programy — wynik jednego wpada jako surowy tekst na wejście drugiego.

2. Podstawowe filtrowanie
grep "slowo" — przepuszcza tylko linie zawierające szukane słowo

less — pager na końcu rury (... | less)

3. Cięcie i podmiana tekstu (sed)
sed 's/STARY/NOWY/' — znajdź i zamień

sed 's/BŁĄD: //' — usunięcie prefiksu z tekstu

4. Wyrażenia regularne (regex)
. — dowolny pojedynczy znak

* — poprzedni znak powtórzony 0+ razy

+ — poprzedni znak powtórzony 1+ razy

[0-9] — jedna dowolna cyfra

.* — łapie wszystko między dwoma punktami

5. Wycinanie kolumn (awk)
awk '{print $2}' — wypisuje drugie słowo/kolumnę

awk '$1 == "TEMP" {print $3}' — warunkowe wycinanie kolumny

6. Sortowanie i zliczanie powtórzeń
text
... | sort | uniq -c | sort -rn | head -n 10
7. Kalkulacje w terminalu
paste -sd+ — łączy liczby w pionie w jedną linię matematyczną

bc -l — kalkulator z potoku

8. Przekazywanie argumentów (xargs)
... | xargs kill — buduje i odpala komendę z argumentami z rury

9. jq — praca z JSON
jq '.data | length' — liczba elementów w tablicy

jq -r '.data[].pole' — wypisuje wartość pola z każdego elementu, bez cudzysłowów

jq -r '.data[].tablica[]?' — spłaszcza zagnieżdżoną tablicę, ? zabezpiecza przed null

jq '[.data[] | select(warunek)] | length' — liczy elementy przechodzące filtr

jq '.data[0] | keys' — lista kluczy pierwszego elementu
