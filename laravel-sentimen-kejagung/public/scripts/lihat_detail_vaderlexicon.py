# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# analyzer = SentimentIntensityAnalyzer()
# print(analyzer.lexicon)


import vaderSentiment
import os

# Dapatkan path folder modul vaderSentiment
module_path = os.path.dirname(vaderSentiment.__file__)

# Gabungkan dengan nama file lexicon
lexicon_path = os.path.join(module_path, "vader_lexicon.txt")

print("Lokasi file lexicon:", lexicon_path)
