def pytest_collection_modifyitems(session, config, items):
    filtered = []
    deselected = []

    for item in items:
        if item.name.startswith("TestAll"):
            deselected.append(item)
        else:
            filtered.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = filtered
