## 1. Basic commands and wildcards (globs)
* `ls` — lists folder contents
* `mkdir` — creates a folder
* `touch` — creates a file
* `rm` — deletes a file
* `*` — replaces any string of characters, e.g. `rm *.py` deletes all Python files in the folder
* `{}` — "multiplies" commands, e.g. `touch report_{mon,tue,wed}.txt` creates three files at once

## 2. Data streams and redirections
* `>` (overwrite) — directs output to a file, destroying its previous content, e.g. `echo "Start" > file.txt`
* `>>` (append) — directs output to the end of a file, without destroying old data
* `2>` (errors) — captures only warnings and errors from a program
* `/dev/null` — system "black hole"; the command `> /dev/null 2>&1` completely silences a program

## 3. Environment variables and paths
* `variable=value` — creating a variable (never spaces around `=`)
* `$variable` — reading a value
* `export PATH="$PATH:/new/folder/with/programs"` — adding a new path to `$PATH`
* `" "` reads variables inside text, `' '` treats text 100% literally

## 4. Exit codes and event logic
* `$?` — exit code of the last command: `0` = success, other value = error
* `&&` (AND) — runs the second command only if the first one succeeded
* `||` (OR) — runs the second command only if the first one ended with an error

## 5. Process management (background work)
* `Ctrl+C` — kills the current program
* `Ctrl+Z` — freezes the current program
* `jobs` — shows frozen/background tasks
* `bg 1` / `fg 1` — resumes task no. 1 in the background / brings to the foreground
* `nohup command &` — runs a program in the background, resistant to terminal closing
* `pgrep name` + `kill 1234` (or `kill -9 1234`) — finding and killing a process

## 6. Working on remote servers (SSH)
* `ssh user@server_address` — logging in
* `ssh-keygen -t ed25519` — generating a key
* `ssh-copy-id user@server_address` — logging in without a password from now on
* `scp file.txt user@address:/folder/` — copying files over the network

## 7. Terminal multiplexer (tmux)
* `tmux new -s name` — new session
* `tmux a` — restoring a detached session
* `Ctrl+B, %` / `Ctrl+B, "` — vertical / horizontal screen split
* `Ctrl+B, d` — detaching a session

## 8. Aliases
* `alias calculate="Rscript long_script.R --flags"`
* `alias rm="rm -i"` — forces asking for permission when deleting

# Part II: Data Wrangling

## 1. Pipes (|)
They connect programs — the result of one falls as raw text into the input of the other.

## 2. Basic filtering
* `grep "word"` — lets through only lines containing the searched word
* `less` — pager at the end of a pipe (`... | less`)

## 3. Cutting and replacing text (sed)
* `sed 's/OLD/NEW/'` — find and replace
* `sed 's/ERROR: //'` — removing a prefix from text

## 4. Regular expressions (regex)
* `.` — any single character
* `*` — previous character repeated 0+ times
* `+` — previous character repeated 1+ times
* `[0-9]` — one random digit
* `.*` — catches everything between two points

## 5. Cutting columns (awk)
* `awk '{print $2}'` — prints the second word/column
* `awk '$1 == "TEMP" {print $3}'` — conditional column cutting

## 6. Sorting and counting repetitions
```text
... | sort | uniq -c | sort -rn | head -n 10
