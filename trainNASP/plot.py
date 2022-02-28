import os
import matplotlib.pyplot as plt

dir = "eval/"

accs = {}
cells = {}
for filename in os.listdir(dir):
    if "train" in filename:
        file = os.path.join(dir, filename)

        acc = []
        cell = []
        with open(file, "r") as f:
            lines = f.readlines()

            i = 4
            while i < len(lines):
                line = lines[i]
                line_c = lines[i+1]
                acc.append(float(line[38:-2]))
                cell.append(float(line_c[38:-2]))
                i += 7
        accs[filename[5:-4]] = acc
        cells[filename[5:-4]] = cell

for key, y in accs.items():
    y = y[:100]
    x = list(range(0, len(y)))
    i = 1
    while 1:
        if i == len(y):
            break
        if i>0:
            if (y[i] < y[i-1]*0.8):
                y.pop(i)
                x.pop(i)
                i-=1
        i+=1
    print("Max acc board value of", key+":", max(y))
    print("Max acc cell value of", key+":", max(cells[key]))
    print()
    plt.plot(x,y, label=key)
    plt.xlabel('Round')
    plt.ylabel('Accuracy on whole board [%]')
plt.legend()
plt.savefig("eval/NASP_plot.png")