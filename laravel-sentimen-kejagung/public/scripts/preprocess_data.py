import pandas as pd
from sklearn.model_selection import train_test_split

# 🔄 Load data
df = pd.read_csv('public/scripts/vader_labeled_data.csv')

# 🔄 Fitur dan Label
X = df[['vader_pos', 'vader_neu', 'vader_neg', 'compound_score']]
y = df['ground_truth_label']

# 🔄 Bagi data (80% Training, 20% Testing)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# ✅ Simpan hasil split
X_train.to_csv('public/scripts/X_train.csv', index=False)
X_test.to_csv('public/scripts/X_test.csv', index=False)
y_train.to_csv('public/scripts/y_train.csv', index=False)
y_test.to_csv('public/scripts/y_test.csv', index=False)

print("\n✅ Data berhasil di-preprocessing dan disimpan:")
print("- public/scripts/X_train.csv")
print("- public/scripts/X_test.csv")
print("- public/scripts/y_train.csv")
print("- public/scripts/y_test.csv")
