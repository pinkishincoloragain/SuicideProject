import re

for drug in ['calcium', 'calcium gluconate']:
    a=[m.start() for m in re.finditer(drug, 'Insulin and calcium gluconate were given.'.lower())]
    for _ in a:
        print(f"{drug} ({_}, {_+len(drug)})")