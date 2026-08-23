import nflreadpy as nfl
import inspect

print("AVAILABLE NFLREADPY FUNCTIONS")
print("=" * 60)

names = [
    name
    for name in dir(nfl)
    if "proj" in name.lower()
    or "fantasy" in name.lower()
]

for name in names:
    obj = getattr(nfl, name)

    print()
    print(name)

    try:
        print(inspect.signature(obj))
    except Exception:
        pass
