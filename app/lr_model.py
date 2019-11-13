import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split


class LRModel(object):

    def __init__(self):
        df = pd.read_excel('app/data/ml.xlsx')
        self.x, self.y = df.iloc[:, df.columns != 'weather'], df.iloc[:, df.columns == 'weather']

    @property
    def model(self):
        # 数据归一化
        scaler = StandardScaler()
        X = scaler.fit_transform(self.x)

        # 初始化模型， 参数
        X_train, X_test, y_train, y_test = train_test_split(X, self.y['weather'], test_size=0.3, random_state=1)
        pca = PCA(n_components=7)
        logReg = LogisticRegression()
        pipe = Pipeline([('pca', pca), ('logistic', logReg)])
        pipe.fit(X_train, y_train)

        return pipe
