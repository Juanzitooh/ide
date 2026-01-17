import sys

from dotenv import load_dotenv

from app import create_app
from app.test_runner import run_tests

load_dotenv()

app = create_app()

if __name__ == "__main__":
    if "--test" in sys.argv:
        with app.app_context():
            report = run_tests()
        if report["errors"]:
            for error in report["errors"]:
                print(f"ERRO: {error}")
            sys.exit(1)
        print("Testes OK.")
        sys.exit(0)

    app.run(host="0.0.0.0", port=5000)
