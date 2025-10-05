import sys
from pathlib import Path

# ensure project root is on sys.path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
	sys.path.insert(0, str(project_root))

from services.parseMedications import parseMedications

s = open('med_examp.txt','r',encoding='utf-8').read()
split_blocks = {'Medikamentengaben': {'Medikamentengaben': s}}

df = parseMedications(split_blocks)
print('ROWS', len(df))
print(df.head(200).to_string())
