def handler(event, context):
    return {"ok": True, "records": len(event.get("Records", []))}
