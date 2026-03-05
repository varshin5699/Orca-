import secrets
import uuid

def random_uid() -> str:
    return uuid.uuid4().hex
## Implement a better way. This ensures astronomically low repetiiton but then doesn't guarantee.