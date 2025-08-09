import os
import sys
from dotenv import load_dotenv
from daytona import Daytona, DaytonaConfig

load_dotenv()

def main() -> None:
    api_key = os.environ.get("DAYTONA_API_KEY")
    if not api_key:
        print(
            "DAYTONA_API_KEY is not set. Ensure it is present in the environment or in .env at the repo root.",
            file=sys.stderr,
        )
        sys.exit(1)

    config = DaytonaConfig(api_key=api_key)
    daytona_client = Daytona(config)

    sandbox = daytona_client.create()
    response = sandbox.process.code_run('print("Hello World from code!")')
    if getattr(response, "exit_code", 1) != 0:
        print(f"Error: {response.exit_code} {response.result}", file=sys.stderr)
        sys.exit(response.exit_code or 1)
    else:
        print(str(response.result))

if __name__ == "__main__":
    main()
