# Poznań IT Market

![CI](https://github.com/marek-sleszynski/poznan-it-market/actions/workflows/ci.yml/badge.svg)

A data pipeline that collects IT job postings from justjoin.it. With plans to add No Fluff Jobs
every day,	 track how they change over time and show, how the Poznań IT job
market evolves.


## Why this exists

Public reports on the Polish IT market are quarterly and nationwide. As a cs student looking for my first job, I wanted daily,
local data and I wanted to build a system that deals with real data engineering. 
problems: incremental loads, cross-source deduplication and change tracking over time. Manually browsing jobs gives you not as good personalisation suited for me.


## What it does

- pulls sample postings from justjoin.it API
- stores raw API as .json files
- normalizes company names, salary ranges and filters by primary location
- runs automated tests and type checks if pushed by CI


## Stack

Python 3.12, httpx, pytest, ruff, mypy, GitHub Actions


## Getting started

- uv sync
- make sample
- make test 


## Status

Project developed since August 2026. Still not finished.
