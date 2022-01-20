import numpy as np
import datetime

distances = r"/Users/Arveiler/Documents/compta_cc/2020_03_26/distances.csv"
merged = r"/Users/Arveiler/Documents/compta_cc/2020_03_26/merged.csv"
beau = merged[:-4] + "_beau.csv"

raw = np.genfromtxt(merged,delimiter=';',dtype=None,names=['dist','date','title','loc'],skip_header=1,encoding='utf-8')

#raw = np.genfromtxt(merged,delimiter=';',dtype=None,names=['dist','date','title','loc'],skip_header=1,encoding='utf-8')
# cal = sorted(raw,key=lambda x: x['date'])
# np.savetxt("/Users/Arveiler/Desktop/cal.csv",cal,fmt=('%.1f','%s','%s','%s'),delimiter=';',encoding='utf-8')