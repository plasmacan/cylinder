def main(response, log, session, request):
    visits = session.get("visits", 0)
    session["visits"] += 1
    response.data = f"visits: {visits}"
    return response
