import pandas as pd
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt

df = sns.load_dataset('titanic')

df['age'] = df['age'].fillna(df['age'].median())
df.dropna(subset=['embarked'], inplace=True)

df = pd.get_dummies(df, columns=['sex', 'embarked'], drop_first=True)

scaler = StandardScaler()
df[['age', 'fare']] = scaler.fit_transform(df[['age', 'fare']])

features = ['pclass', 'age', 'fare', 'sibsp', 'parch', 'sex_male', 'embarked_Q', 'embarked_S']

X = df[features]
y = df['survived']

kmeans = KMeans(n_clusters=2, random_state=42, n_init='auto')
clusters = kmeans.fit_predict(X)

df['cluster'] = clusters
sns.scatterplot(x='age', y='fare', hue='cluster', data=df)
plt.title('Кластеризация пассажиров')
plt.show()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
model = LogisticRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Оценка качества модели
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))