from tokens.generator import generate_token
from tokens.validator import validate_token

DEFAULT_TTL = 3600  

def get_valid_token(scope: str, user_profile: dict, ttl: int = DEFAULT_TTL) -> str:
    tokens = user_profile.setdefault("tokens", {})
    token = tokens.get(scope)

    if token and validate_token(token, expected_scope=scope):
        return token  # still valid

    # generate new and store
    new_token = generate_token(user_profile["user_id"], ttl=ttl, scope=scope)
    tokens[scope] = new_token
    return new_token