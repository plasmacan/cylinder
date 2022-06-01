import cylinder  # pip install cylinder


def main():
    app = cylinder.get_app(triage)
    app.run(host="127.0.0.42", port=80)


def triage(request):  # pylint: disable=unused-argument
    # here you can examine the incoming request and decide to route to different webapps
    # depending on the hostname for example

    return "my_webapps", "webapp1"


if __name__ == "__main__":
    main()
