import os
import sys

sys.path.insert(0, os.getcwd())
import src.cylinder as cylinder


def main():
    app = cylinder.get_app(dir_map, secret_key="df")
    app.run(host="127.0.0.42", port=80)


def dir_map(request):
    return "test_sites", "foo_site"


if __name__ == "__main__":
    main()
