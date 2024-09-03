import sys

intensity=str(sys.argv[1])
sec=int(sys.argv[2])

path = './EqData.txt'
with open(path, 'w') as f:
    f.write(f"{intensity} {sec}")
