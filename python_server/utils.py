import json
import hashlib


def get_class_hash(obj):
    serialized_obj = json.dumps(
        obj,
        default=lambda o: o.__dict__,
        sort_keys=True,
    )
    return hashlib.sha256(serialized_obj.encode("utf-8")).hexdigest()
