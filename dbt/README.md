# dbt models

Run commands from the project root:

```bash
make dbt-demo
make dbt
```

`dbt-demo` uses the local demo database and the sample date. `dbt` uses the live database.
Both build models and run data tests. The shared build script prepares the connection settings.

Staging filters the selected data mode and city. Marts contain daily observations,
skills and salary variants.

The daily workflow runs live source freshness separately before the build.
See [the data model](../docs/data-model.md) and [quality checks](../docs/data-quality.md).
