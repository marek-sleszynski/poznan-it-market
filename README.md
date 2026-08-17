# Poznań IT Market

![CI](https://github.com/marek-sleszynski/poznan-it-market/actions/workflows/ci.yml/badge.svg)

A data pipeline that collects IT job postings from justjoin.it and No Fluff Jobs
every day, tracks how they change over time, and shows how the Poznań IT job
market evolves.


## Why this exists

Public reports on the Polish IT market are quarterly and nationwide. As a cs student looking for my first job, I wanted daily,
local data and I wanted to build a system that deals with real data engineering. 
problems: incremental loads, cross-source deduplication and change tracking over time. Manually browsing job gives you not as good personalisation suited for me.

## Setup

git clone https://github.com/marek-sleszynski/poznan-it-market
cd poznan-it-market
uv sync
uv run ruff check .
