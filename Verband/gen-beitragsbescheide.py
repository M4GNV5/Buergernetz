import os

YEAR = "2019"

with open("beitragsbescheid.tex.template") as fd:
    template = fd.read()

columns = [
    "Mandat",
    "BnName",
    "Strasse",
    "PLZ",
    "Ort",
    "Email",
    "Mitglieder",
    "BetragHalb",
]
with open("beitraege.csv") as fd:
    for line in fd.readlines():
        split = line.split('\t')
        curr = template.replace('|Jahr|', YEAR)
        for i, key in enumerate(columns):
            curr = curr.replace('|{}|'.format(key), split[i])

        with open("beitragsbescheid.tex", "w+") as fd2:
            fd2.write(curr)

        os.system("pdflatex -interaction=nonstopmode beitragsbescheid.tex")

        name = split[1].replace(".", "_").replace(" ", "_")
        os.system("mv beitragsbescheid.pdf bescheid/{}.pdf".format(name)) # mimimi insertion vuln
