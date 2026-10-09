import os
import uuid
from pathlib import Path

from poznan_it_market.config import DATABASE_URL
from poznan_it_market.dbt_config import dbt_environment_from_url


def main():
    output_path = Path(os.environ["GITHUB_ENV"])
    settings = dbt_environment_from_url(DATABASE_URL)
    password = settings["POSTGRES_PASSWORD"]
    masked = password.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::add-mask::{masked}")

    with output_path.open("a", encoding="utf-8") as output:
        for name, value in settings.items():
            # Delimiters preserve special characters and multiline values.
            delimiter = uuid.uuid4().hex
            output.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")


if __name__ == "__main__":
    main()
