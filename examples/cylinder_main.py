import cylinder  # pip install cylinder
import waitress  # pip install waitress


def main():
    app = cylinder.get_app(triage)
    waitress.serve(app, host="127.0.0.1", port=80)


def triage(request):
    # here you can examine the incoming request and decide to route to different webapps
    # depending on the hostname for example

    # you return a tuple of three items:
    # 1) site_dir: the root directory of the site that will handle the request
    # 2) site_name: a meaningful name for the website, perhaps the domain name
    # 3) appended_args: a dict of function arguments and their values that can be used later
    return "my_webapps", "webapp1", {}


if __name__ == "__main__":
    main()
