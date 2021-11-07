## Predict scores for China football team via Naive Bayes

- 参考test_nb.ipynb

```{python}
from sklearn.naive_bayes import MultinomialNB, GaussianNB, CategoricalNB
import numpy as np
import pandas as pd 
from utils import chinawin, _label_trans

data = pd.read_csv('data.csv', encoding="gbk")
cw = chinawin()
cw.process_data(data)
# 获得特征
X, y = cw.get_feature()

clf = CategoricalNB()

ind = np.random.choice(len(y),int(len(y)*0.9))
X_train = X[ind]
y_train = y[ind]
X_test = X[~ind]
y_test = y[~ind]

clf.fit(X_train, y_train)
print("acc: ", sum(clf.predict(X_test) == y_test.reshape(-1)) / len(y))

```

