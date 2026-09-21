import csv, sys

path = sys.argv[1] if len(sys.argv) > 1 else "ratings.csv"

with open(path, "rb") as f:
    head = f.read(20)
print("Primeros bytes (crudo):", head)

with open(path, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    print("\nColumnas detectadas:", reader.fieldnames)
    row = next(reader, None)
    if row:
        print("\nPrimera fila:")
        for k, v in row.items():
            print(f"  {k!r} -> {v!r}")
