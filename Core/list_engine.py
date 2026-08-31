def get_list_data(data):

    if not isinstance(data, dict):
        return None

    if data.get("engine") != "list":
        return None

    return {
        "title": data.get("title", ""),
        "messages": data.get("messages", []),
        "items": data.get("items", [])
    }