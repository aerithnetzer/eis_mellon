import textnets as tn
import matplotlib.pyplot as plt

corpus = tn.Corpus(tn.examples.moon_landing)
t = tn.Textnet(corpus.tokenized(), min_docs=1)
fig, ax = plt.subplots(figsize=(8, 8))
t.plot(label_nodes=True, show_clusters=True, ax=ax)
plt.savefig("textnet.png")
