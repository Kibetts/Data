from functools import wraps

from flask import current_app, jsonify, request


def require_admin_key(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        provided = request.headers.get("X-Admin-Key")
        if not provided or provided != current_app.config["ADMIN_API_KEY"]:
            return jsonify({"error": "Unauthorized"}), 401
        return fn(*args, **kwargs)

    return wrapper
