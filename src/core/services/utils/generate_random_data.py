import random
import string


def generate_random_string(length: int = 4) -> str:
  """Generates a random string of specified length for filename uniqueness."""
  return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
