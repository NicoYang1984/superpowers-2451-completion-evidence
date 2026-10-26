def handle_request(name):
    return (200, "accepted") if len(name) <= 100 else (422, "business validation")
