# -*- coding: utf-8 -*-
"""Yet another copy of projet_machine_learning.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1jv0AEwIXUQnEB70WE3R7tHYKIKrFkeSx

## import
"""

# Commented out IPython magic to ensure Python compatibility.

# Data manipulation libraries
import pandas as pd
import numpy as np

# Data visualization libraries
import matplotlib.pyplot as plt
# %matplotlib inline
import matplotlib
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Setting style and rcparams
sns.set_style('darkgrid')
matplotlib.rcParams['font.size'] = 14
matplotlib.rcParams['figure.figsize'] = (7, 4)
matplotlib.rcParams['figure.facecolor'] = '#00000000'
plt.rcParams["font.family"] = "sans-serif"

# For removing Multicollinearity
from statsmodels.stats.outliers_influence import variance_inflation_factor

# For handling class imbalance
from imblearn.over_sampling import SMOTE

# Preprocessing libraries
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, OrdinalEncoder, LabelEncoder, FunctionTransformer, PowerTransformer

# Model implementation libraries
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.naive_bayes import GaussianNB, BernoulliNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from xgboost import XGBClassifier, XGBRegressor
import lightgbm as lgb

# For building pipelines
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline, make_pipeline

# Model selection libraries
from sklearn.model_selection import cross_validate, train_test_split, GridSearchCV, cross_val_score, RandomizedSearchCV

# For performance metrics
from sklearn.metrics import mean_squared_error, r2_score, classification_report, confusion_matrix, accuracy_score, roc_auc_score, roc_curve, log_loss, precision_score, f1_score, recall_score, auc, fbeta_score

# Other libraries
from sklearn import metrics
from sklearn import tree
from joblib import Parallel, delayed
import time
import scipy.stats as stats
import seaborn as sns
import zipfile
import os

'''
#Google Colab
from google.colab import drive
# Mount Google Drive
drive.mount('/content/drive')
'''

"""##read data

"""

# Commented out IPython magic to ensure Python compatibility.
if not os.path.exists('projetml'):
  !git clone https://github.com/mathisehkirch/projetml.git

#   %cd projetml

  with zipfile.ZipFile('store-sales-time-series-forecasting.zip', 'r') as zip_ref:
    zip_ref.extractall()

#   %cd store-sales-time-series-forecasting
  files = os.listdir()
  csv_files = [file for file in files if file.endswith('.csv')]

  for file in csv_files:
    # Extract the name of the file (without extension) to use as variable name
    var_name = os.path.splitext(file)[0]
    # Read the CSV file and assign it to a variable with the filename as its name
    globals()[var_name] = pd.read_csv(file)

#   %cd /content

'''
stores= pd.read_csv('/content/drive/MyDrive/ML/Projet/stores.csv')
holidays_events= pd.read_csv('/content/drive/MyDrive/ML/Projet/holidays_events.csv')
oil= pd.read_csv('/content/drive/MyDrive/ML/Projet/oil.csv')
sample_submission= pd.read_csv('/content/drive/MyDrive/ML/Projet/sample_submission.csv')
test= pd.read_csv('/content/drive/MyDrive/ML/Projet/test.csv')
train= pd.read_csv('/content/drive/MyDrive/ML/Projet/train.csv')
transactions= pd.read_csv('/content/drive/MyDrive/ML/Projet/transactions.csv')


pd.set_option('display.max_rows', 100)  # Adjust 1000 to the desired number of rows to display
pd.set_option('display.max_columns', 100)  # Adjust 1000 to the desired number of columns to display
'''

print('stores df:')
stores.info()
print('holidays_events df:')
holidays_events.info()
print('oil df:')
oil.info()
print('test df:')
test.info()
print('train df:')
train.info()
print('transactions df:')
transactions.info()

"""#Data Prep

##Holiday Data Engineering

###Create Dummy
"""

holidays_events = pd.concat([holidays_events.drop('locale', axis=1),
                             pd.get_dummies(holidays_events['locale'],
                                            prefix='locale',
                                            prefix_sep='_',
                                            drop_first=False,
                                            dummy_na=False).astype(int)],
                             axis=1)

holidays_events = holidays_events[['date', 'type', 'locale_name', 'description', 'transferred', 'locale_Local', 'locale_Regional', 'locale_National']]

holidays_events.describe(include='all')

"""###Unique attributes"""

print(holidays_events['type'].unique())
print(holidays_events['description'].unique())
print(holidays_events['locale_name'].unique())
print(holidays_events['transferred'].unique())

"""###Binning description"""

# Assuming holidays_events is your DataFrame and description is the column containing event descriptions

# Create a new column to store the category
holidays_events['category'] = 'Other'

# Historical Events
historical_keywords = ['Fundacion', 'Independencia', 'Batalla', 'Provincializacion', 'Cantonizacion', 'Traslado']
holidays_events.loc[holidays_events['description'].str.contains('|'.join(historical_keywords), case=False), 'category'] = 'Historical Events'

# Holiday and Celebration Events
holiday_keywords = ['Dia', 'Navidad', 'Carnaval', 'Viernes Santo', 'Black Friday', 'Cyber Monday', 'Puente', 'Recupero']
holidays_events.loc[holidays_events['description'].str.contains('|'.join(holiday_keywords), case=False), 'category'] = 'Holiday and Celebration Events'

# Natural Disaster Events
disaster_keywords = ['Terremoto']
holidays_events.loc[holidays_events['description'].str.contains('|'.join(disaster_keywords), case=False), 'category'] = 'Natural Disaster Events'

# Sports Events
sports_keywords = ['Mundial de futbol']
holidays_events.loc[holidays_events['description'].str.contains('|'.join(sports_keywords), case=False), 'category'] = 'Sports Events'

"""###Adressing Holiday Date Duplicates"""

duplicate_dates = holidays_events[holidays_events.duplicated(subset='date', keep=False)]
print("Duplicate Dates:")
#duplicate_dates

#drop description
#dummy locale_name

print("Duplicate Dates:")
duplicate_dates

df = holidays_events

# Step 1: Group by the duplicate column
grouped = df.groupby('date')

# Step 2: Sum up the three integer columns within each group
summed_values = grouped[['locale_Local', 'locale_Regional', 'locale_National']].sum()

# Step 3: Merge the summed values back into the original DataFrame
df = df.merge(summed_values, left_on='date', right_index=True, suffixes=('', '_sum'))

df_sorted = df.sort_values(by=['date', 'locale_Local', 'locale_Regional', 'locale_National'])
df_sorted

df_sorted.drop_duplicates(subset='date', keep='first', inplace=True)
df_sorted = df_sorted.drop(columns=['locale_Local', 'locale_Regional', 'locale_National'])

df_sorted

df_sorted.reset_index(drop=True, inplace=True)
holidays_events = df_sorted

holidays_events.head(10)

"""##Table Merge"""

train['test'] = 0
test['test'] = 1

data = pd.concat([train, test], axis=0)

data = data.merge(holidays_events, on='date', how='left')
data= data.merge(stores, on='store_nbr', how='left')
data= data.merge(oil, on='date', how='left')
data= data.merge(transactions, on=['date', 'store_nbr'], how='left')
data = data.set_index(['store_nbr', 'date', 'family'])
data = data.drop(index='2013-01-01', level=1)

"""## Data Engineering

###More Date
"""

data_ = data.copy().reset_index()


data_['date'] = pd.to_datetime(data_["date"])
data_['day_of_week'] = data_['date'].dt.day_of_week
data_['day_of_year'] = data_['date'].dt.dayofyear
data_['day_of_month'] = data_['date'].dt.day
data_['month'] = data_['date'].dt.month
data_['quarter'] = data_['date'].dt.quarter
data_['year'] = data_['date'].dt.year

train = data_[data_['test'] == 0]
test = data_[data_['test'] == 1]

data_

"""###Exponentially weighted moving average (sales)"""

grouped_data = data_.groupby(['store_nbr', 'family'])

alphas = [0.95, 0.8, 0.65, 0.5]
lags =[1,7,30]

for a in alphas:
    for i in lags:
        data_[f'sales_lag_{i}_alpha_{a}'] = np.log1p(grouped_data['sales'].transform(lambda x: x.shift(i).ewm(alpha=a, min_periods=1).mean()))

data_['sales_lag_7_alpha_0.5'].describe()

sales_lag_columns = list(data_.filter(like="lag").columns)

data_

"""##Dummies and test/train init"""

to_dummies = ['day_of_week', 'day_of_month', 'month', 'quarter', 'year', 'store_nbr', 'type_y', 'cluster', 'family', 'onpromotion', 'type_x',
              'locale_name', 'city', 'state', 'category', 'transferred']

X = data_.loc[:, [ 'day_of_week', 'day_of_month', 'month', 'quarter', 'year', 'store_nbr', 'type_y', 'cluster', 'family', 'onpromotion', 'type_x', 'category',
                  'transferred', 'locale_Local_sum',	'locale_Regional_sum',	'locale_National_sum', 'locale_name',  'city', 'state', 'test', 'sales', 'id']+ sales_lag_columns]

X[to_dummies] = X[to_dummies].astype('category')

data_train = X[X['test'] == 0]
data_test = X[X['test'] == 1]

dt_X_train = data_train.drop(['test', 'sales', 'id'],  axis=1)
dt_X_test = data_test.drop(['test', 'sales', 'id'],  axis=1)

dt_y_train = data_train['sales']

"""# ML

##Library
"""

# Commented out IPython magic to ensure Python compatibility.
'''
# Data manipulation libraries
import pandas as pd
import numpy as np

# Data visualization libraries
import matplotlib.pyplot as plt
# %matplotlib inline
import matplotlib
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


# setting style and rcparams
sns.set_style('darkgrid')
matplotlib.rcParams['font.size'] = 14
matplotlib.rcParams['figure.figsize'] = (7,4)
matplotlib.rcParams['figure.facecolor'] = '#00000000'
plt.rcParams["font.family"] = "sans-serif"

# for remove Multicollinearity
from statsmodels.stats.outliers_influence import variance_inflation_factor

# for handling class imbalance
from imblearn.over_sampling import SMOTE

# Preprocessing libraries
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import PowerTransformer

# for model implementation
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.decomposition import PCA
from sklearn import tree
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

# For build pipeline
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.pipeline import make_pipeline

# Model selection libraries
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RandomizedSearchCV

# for performance metrics
from sklearn import metrics
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score
from sklearn.metrics import accuracy_score, roc_auc_score, roc_curve, log_loss, precision_score, f1_score, recall_score, auc, fbeta_score

import time

from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBRegressor

from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import GradientBoostingRegressor
from sklearn import tree
from joblib import Parallel, delayed


import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import scipy.stats as stats

import lightgbm as lgb
'''

"""##X and y"""

TEST_SIZE = 0.2
RAND_STATE = 91

X_train, X_test, y_train, y_test = train_test_split(dt_X_train, dt_y_train, test_size = TEST_SIZE, random_state=RAND_STATE)

X_train_LGBM, X_val, y_train_LGBM, y_val = train_test_split(X_train, y_train, test_size = TEST_SIZE, random_state=RAND_STATE)

X_test_LGBM = dt_X_test.loc[:, ]


# X_test_final

"""## Performance Metrics Function"""

def performance_metrics(actual, prediction, train_actual, train_predicted, model=''):
    print('\033[1m' + '-----------------------------------------' + '\033[0m')
    print(f'{model} Test data R-squared Score:', r2_score(actual, prediction))
    print(f'{model} Train data R-squared Score:', r2_score(train_actual, train_predicted))
    print('\033[1m' + '-----------------------------------------' + '\033[0m')

    mse_test = mean_squared_error(actual, prediction)
    mse_train = mean_squared_error(train_actual, train_predicted)

    print(f'{model} Test data Mean Squared Error:', mse_test)
    print(f'{model} Train data Mean Squared Error:', mse_train)
    print('\033[1m' + '-----------------------------------------' + '\033[0m')

    # Plot the scatter plot of actual vs predicted values for test set
    plt.figure(figsize=(8, 6))
    plt.scatter(actual, prediction, color='blue', label='Test Data', s=1, alpha=0.8)
    #plt.scatter(train_actual, train_predicted, color='red', label='Train Data', s=5, alpha=0.01)
    plt.title(f'{model} - Actual vs Predicted')
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    plt.legend(loc="upper right")
    plt.show()


    actual_combined = np.concatenate([actual, prediction])

    plt.figure(figsize=(16, 12))

    # Density plot
    plt.subplot(2, 2, 1)
    sns.kdeplot(actual_combined, cmap='Blues', fill=True, bw_method=0.5)
    plt.title(f'{model} - Density Plot of Actual vs Predicted (Test Data)')
    plt.xlabel('Actual')
    plt.ylabel('Predicted')

    # Residual plot
    residuals = prediction - actual
    plt.subplot(2, 2, 2)
    plt.scatter(prediction, residuals, color='blue')
    plt.axhline(y=0, color='red', linestyle='--')
    plt.title(f'{model} - Residual Plot (Test Data)')
    plt.xlabel('Predicted')
    plt.ylabel('Residuals')

    # Q-Q plot
    plt.subplot(2, 2, 3)
    stats.probplot(actual - prediction, dist="norm", plot=plt)
    plt.title(f'{model} - Q-Q Plot (Test Data)')
    plt.xlabel('Theoretical Quantiles')
    plt.ylabel('Ordered Values')

    df = pd.DataFrame({'Actual': actual, 'Predicted': prediction})

    # Downsample the DataFrame
    df_sampled = df.sample(n=50000, random_state=42)

    # Create the violin plot with sampled data
    plt.subplot(2, 2, 4)
    sns.violinplot(data= df_sampled, cmap='Blues')
    plt.title(f'{model} - Violin Plot of Actual vs Predicted (Test Data)')
    plt.xlabel('Actual')
    plt.ylabel('Predicted')

    plt.tight_layout()
    plt.show()

"""##Old Algorithms

###Dict Regressors + Hyperparameters Basic Algorithm
"""

'''
GB_hyper = {
    'n_estimators': 100,           # default is 100 trees
    'learning_rate': 0.1,          # Moderate learning rate (default 0.1)
    'subsample': 0.5,              # Use % of samples for each tree (default 1)
    'max_depth': 3,                # Shallow trees (default 3)
    'max_features': 'sqrt',        # Use square root of features for splitting (default none: all)
    'min_samples_split': 10,       # Require 10 samples for a split (default 2)
    'min_samples_leaf': 5,         # Require 10 samples for a leaf (default 1)
    'loss': 'squared_error',       # Default least squares loss (default squared_error)
    'alpha': 0.9,                  # Regularization parameter (default is 0.9)
    'init': None,                  # Initial estimator for predictions (default is None)
    'warm_start': False,           # Reuse solution of the previous call to fit as initialization (default is False)
    'random_state': 9009           # Random seed for random number generation (default is None)
}

DT_hyper = {
    'criterion': 'squared_error',   # The function to measure the quality of a split (default is squared error)
    'splitter': 'best',             # The strategy used to choose the split at each node (default is 'best')
    'max_depth': 10,                # The maximum depth of the tree (default is None)
    'min_samples_split': 10,         # The minimum number of samples required to split an internal node (default is 2)
    'min_samples_leaf': 5,          # The minimum number of samples required to be at a leaf node (default is 1)
    'min_weight_fraction_leaf': 0.0,# The minimum weighted fraction of the sum total of weights (default is 0.0)
    'max_features': None,           # The number of features to consider when looking for the best split (default is None)
    'random_state': 9119,           # The random seed for random number generation (default is None)
    'max_leaf_nodes': None,         # The maximum number of leaf nodes (default is None)
    'min_impurity_decrease': 0.0,   # The minimum impurity decrease required for a split to happen (default is 0.0)
    'ccp_alpha': 0.0                # The complexity parameter used for Minimal Cost-Complexity Pruning (default is 0.0)
}

RF_hyper = {
    'n_estimators': 5,         # Number of trees in the forest (default is 100)
    'criterion': 'squared_error',# Function to measure the quality of a split (default is squared error)
    'max_depth': 10,             # Maximum depth of the tree (default is None)
    'min_samples_split': 10,     # Minimum number of samples required to split an internal node (default is 2)
    'min_samples_leaf': 5,      # Minimum number of samples required to be at a leaf node (default is 1)
    'min_weight_fraction_leaf': 0.0,  # Minimum weighted fraction of the sum total of weights (default is 0.0)
    'max_features': 'auto',      # Number of features to consider when looking for the best split (default is 'auto')
    'max_leaf_nodes': None,      # Maximum number of leaf nodes (default is None)
    'min_impurity_decrease': 0.0,  # Minimum impurity decrease required for a split to happen (default is 0.0)
    'bootstrap': True,           # Whether bootstrap samples are used when building trees (default is True)
    'oob_score': False,          # Whether to use out-of-bag samples to estimate the R^2 on unseen data (default is False)
    'random_state': 9229,        # Random seed for random number generation (default is None)
    'verbose': 0,                # Controls the verbosity of the tree building process (default is 0)
    'warm_start': False,         # When set to True, reuse the solution of the previous call to fit and add more estimators to the ensemble (default is False)
    'ccp_alpha': 0.0,            # Complexity parameter used for Minimal Cost-Complexity Pruning (default is 0.0)
    'max_samples': None          # If bootstrap is True, the number of samples to draw from X to train each base estimator (default is None)
}

Linear_hyper = {
    'fit_intercept': True,            # Calculate intercept (default is True)
    'copy_X': False,                   # Copy X or overwrite it (default is True)
}

Ridge_hyper = {
    'alpha': 1.0,                     # Regularization strength (default is 1.0)
    'fit_intercept': True,            # Calculate intercept (default is True)
    'copy_X': False,                  # Copy X or overwrite it (default is True)
    'max_iter': 10000,                # Maximum number of iterations for optimization (default is None)
    'tol': 0.001,                     # Tolerance for stopping criterion (default is 1e-3)
    'solver': 'auto',                 # Solver to use for optimization (default is 'auto')
    'random_state': 9999,             # Random seed for random number generation (default is None)
}

Lasso_hyper = {
    'alpha': 1.0,                     # Regularization strength (default is 1.0)
    'fit_intercept': True,            # Calculate intercept (default is True)
    'precompute': True,               # Precompute Gram matrix for faster computation (default is False)
    'copy_X': False,                  # Copy X or overwrite it (default is True)
    'max_iter': 10000,                # Maximum number of iterations for optimization (default is 1000)
    'tol': 0.0001,                    # Tolerance for stopping criterion (default is 1e-4)
    'warm_start': True,               # Reuse solution of the previous call to fit as initialization (default is False)
    'positive': False,                # Force coefficients to be positive (default is False)
    'random_state': 9889              # Random seed for random number generation (default is None)
}

dict_regressors = {
    #"Nearest Neighbors": KNeighborsRegressor(),
    #"Random Forest Regressor": RandomForestRegressor(),
    #"Neural Network Regressor": MLPRegressor(),
    #"XGBoost Regressor": XGBRegressor(),
    #"Gradient Boosting Regressor": GradientBoostingRegressor(**GB_hyper),
    "Decision Tree Regressor": tree.DecisionTreeRegressor(**DT_hyper),
    "Random Tree Regressor": RandomForestRegressor(**RF_hyper),
    "Linear Regression": LinearRegression(**Linear_hyper),
    "Ridge Regression": Ridge(**Ridge_hyper),
    "Lasso Regression": Lasso(**Lasso_hyper),
}

no_regressors = len(dict_regressors.keys())
'''

"""###Batch Regress Method"""

'''
def batch_regress(X_train, y_train, X_test, y_test, dict_regressors, n_jobs=-1, verbose=True):
    def fit_regressor(key, regressor):
        t_start = time.perf_counter()
        regressor.fit(X_train, y_train)
        t_end = time.perf_counter()
        t_diff = t_end - t_start

        y_train_pred = regressor.predict(X_train)
        y_test_pred = regressor.predict(X_test)

        train_score = r2_score(y_train, y_train_pred)
        test_score = r2_score(y_test, y_test_pred)

        mse_train = mean_squared_error(y_train, y_train_pred)
        mse_test = mean_squared_error(y_test, y_test_pred)

        return {
            'regressor': key,
            'train_score': train_score,
            'test_score': test_score,
            'mse_train': mse_train,
            'mse_test': mse_test,
            'training_time': t_diff,
            'y_train_pred': y_train_pred,
            'y_test_pred': y_test_pred,
            'y_train_pred_rescaled': pd.Series(scaler_Y.inverse_transform(y_train_pred.reshape(-1, 1)).flatten(), index=y_train.index),
            'y_test_pred_rescaled': pd.Series(scaler_Y.inverse_transform(y_test_pred.reshape(-1, 1)).flatten(), index=y_test.index)


#y = pd.Series(y_sca.flatten(), index=y.index)
        }

    results = Parallel(n_jobs=n_jobs)(delayed(fit_regressor)(key, regressor) for key, regressor in dict_regressors.items())

    df_results = pd.DataFrame(results)

    if verbose:
        for result in results:
            print("Trained {c} in {f:.2f} s".format(c=result['regressor'], f=result['training_time']))

    return df_results
'''

"""###Batch Regress OLD"""

'''
from sklearn.metrics import mean_squared_error, r2_score

def batch_regress(X_train, y_train, X_test, y_test, verbose=True):
    df_results = pd.DataFrame(data=np.zeros(shape=(no_regressors, 1)), columns=['regressor'])
    count = 0
    for key, regressor in dict_regressors.items():
        t_start = time.perf_counter()
        regressor.fit(X_train, y_train)
        t_end = time.perf_counter()
        t_diff = t_end - t_start

        y_train_pred = regressor.predict(X_train)
        y_test_pred = regressor.predict(X_test)

        train_score = r2_score(y_train, y_train_pred)
        test_score = r2_score(y_test, y_test_pred)

        mse_train = mean_squared_error(y_train, y_train_pred)
        mse_test = mean_squared_error(y_test, y_test_pred)

        df_results.loc[count, 'regressor'] = str(key)
        df_results.loc[count, 'train_score'] = train_score
        df_results.loc[count, 'test_score'] = test_score
        df_results.loc[count, 'mse_train'] = mse_train
        df_results.loc[count, 'mse_test'] = mse_test
        df_results.loc[count, 'training_time'] = t_diff

        if verbose:
            print("Trained {c} in {f:.2f} s".format(c=key, f=t_diff))
        count += 1
    return df_results
'''

"""### Training"""

#df_results = batch_regress(X_train, y_train, X_test, y_test, dict_regressors)

"""### Top 3 Graphs"""

'''
print(df_results.sort_values(by='test_score', ascending=False))

top_regressors = df_results.sort_values(by='test_score', ascending=False).head(3)

# Loop through top regressors
for _, row in top_regressors.iterrows():
    regressor_name = row['regressor']
    y_train_pred = row['y_train_pred']
    y_test_pred = row['y_test_pred']

    # Check the performance metrics using the predictions from df_results
    performance_metrics(y_test, y_test_pred, y_train, y_train_pred, regressor_name)

    print(y_test)
    print(y_test_pred)

'''

"""###RandomSearchCV"""

'''
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint

# Step 1: Define the hyperparameters
DT_hyperpara = {
 #   'criterion': ['squared_error', 'friedman_mse', 'absolute_error'],   # Measure the quality of a split (default is squared error)
 #   'splitter': ['best', 'random'],                                    # Strategy used to choose the split at each node (default is 'best')
    'max_depth': [5],                      # Maximum depth of the tree (default is None)
 #   'min_samples_split': [2, 5, 10],                               # Minimum number of samples required to split an internal node (default is 2)
 #   'min_samples_leaf': [1, 4, 6, 9],                                 # Minimum number of samples required to be at a leaf node (default is 1)
 #   'min_weight_fraction_leaf': [i / 10 for i in range(1, 10, 2)],                 # The minimum weighted fraction of the sum total of weights (default is 0.0)
 #   'max_features': ['sqrt', 'log2', None], #[i / 10 for i in range(1, 10, 2)]],   # Number of features to consider when looking for the best split
 #   'random_state': [9119],                                                         # Random seed for random number generation
 #   'min_impurity_decrease': [0.0, 0,5],#[i / 10 for i in range(1, 10, 2)],        # The minimum impurity decrease required for a split to happen (default is 0.0)
 #   'ccp_alpha': [0.0, 0,5],#[i / 10 for i in range(1, 10, 2)]                     # The complexity parameter used for Minimal Cost-Complexity Pruning (default is 0.0)
}

#Best hyperparameters: {'random_state': 9119, 'min_samples_split': 6, 'min_samples_leaf': 1, 'max_depth': 5, 'criterion': 'friedman_mse'}


# Step 2: Create a decision tree regressor instance
dt_regressor = DecisionTreeRegressor()

# Step 3: Perform random grid search using RandomizedSearchCV
random_search = RandomizedSearchCV(
    estimator=dt_regressor,
    param_distributions=DT_hyperpara,
    scoring = 'neg_mean_absolute_error',
    n_iter=2,  # Number of parameter settings that are sampled
    cv=2,        # Number of folds for cross-validation
    verbose=2,
    random_state=42,
    n_jobs=-1
)

# Step 4: Fit the RandomizedSearchCV object to your training data
#random_search.fit(X_train, y_train)
random_search.fit(X_train, y_train)


# Step 5: Extract the best estimator and its corresponding hyperparameters
best_estimator = random_search.best_estimator_
best_params = random_search.best_params_
print("Best hyperparameters:", best_params)
'''

'''
# Initialiser le meilleur modèle avec les hyperparamètres optimaux
best_rf_regressor = DecisionTreeRegressor(**random_search.best_params_)

# Entraîner le meilleur modèle sur les données d'entraînement
best_rf_regressor.fit(X_train, y_train)

'''

'''
# Faire des prédictions sur les données de test
y_train_pred = best_rf_regressor.predict(X_train)
y_test_pred = best_rf_regressor.predict(X_test)

y_final_test_pred = best_rf_regressor.predict(X_test_final)
'''

'''
performance_metrics(y_test, y_test_pred, y_train, y_train_pred, 'DecisionTreeRegressor')
'''

"""###Submission CSV"""

'''
y_final_test_pred_inverse = scaler_Y.inverse_transform(y_final_test_pred.reshape(-1, 1))

# Convert it back to a pandas Series with the original index
y_Sub = pd.Series(y_final_test_pred_inverse.flatten(), index=X_test_final.index)

# Créer un DataFrame avec les ID et les prédictions
submission_df = pd.DataFrame({
    'id': test['id'],
    'sales': y_Sub
})

# Enregistrer le DataFrame au format CSV
submission_df.to_csv('submission.csv', index=False)
'''

"""##LightGBM"""

X_train_LGBM

"""### Initialize"""

#X_test_LGBM = X_test_final.loc[:, ]

'''

https://lightgbm.readthedocs.io/en/latest/Parameters.html

For Better Accuracy --

Use large max_bin (may be slower)
max_bin, default = 255, type = int, constraints: max_bin > 1
    max number of bins that feature values will be bucketed in
    small number of bins may reduce training accuracy but may
       increase general power (deal with over-fitting)
    LightGBM will auto compress memory according to max_bin.
       For example, LightGBM will use uint8_t for feature value if max_bin=255

Use small learning_rate with large num_iterations
learning_rate, default = 0.1, type = double, constraints: learning_rate > 0.0 ;
    in dart, it also affects on normalization weights of dropped trees
num_iterations, default = 100, type = int, constraints: num_iterations >= 0

Use large num_leaves (may cause over-fitting)
num_leaves, default = 31, type = int, constraints: 1 < num_leaves <= 131072
    max number of leaves in one tree

Try dart

boosting, default = gbdt, type = enum, options: gbdt, rf, dart,
    dart, Dropouts meet Multiple Additive Regression Trees



Deal with Over-fitting --

Use small max_bin
Use small num_leaves
Use min_data_in_leaf and min_sum_hessian_in_leaf

Use bagging by set bagging_fraction and bagging_freq
Use feature sub-sampling by set feature_fraction

Try lambda_l1, lambda_l2 and min_gain_to_split for regularization
lambda_l1 , default = 0.0, type = double,  constraints: lambda_l1 >= 0.0
lambda_l2 , default = 0.0, type = double,  constraints: lambda_l2 >= 0.0
min_gain_to_split, default = 0.0, type = double, constraints: min_gain_to_split >= 0.0
    the minimal gain to perform split
    can be used to speed up training

Try max_depth to avoid growing deep tree
max_depth, default = -1, type = int
limit the max depth for tree model. This is used to deal with over-fitting
     when #data is small. Tree still grows leaf-wise, <= 0 means no limit

Try extra_trees
extra_trees, default = false, type = bool,
    use extremely randomized trees
    if set to true, when evaluating node splits LightGBM will check only
        one randomly-chosen threshold for each feature
    can be used to speed up training
    can be used to deal with over-fitting

Try increasing path_smooth

path_smooth , default = 0, type = double, constraints: path_smooth >=  0.0
    controls smoothing applied to tree nodes, helps prevent overfitting on leaves with few samples
    if set to zero, no smoothing is applied, if path_smooth > 0 then min_data_in_leaf must be at least 2
    larger values give stronger regularization

the weight of each node is w * (n / path_smooth) / (n / path_smooth + 1) +w_p / (n / path_smooth + 1),
 where n is the number of samples in the node,w is the optimal node weight to minimise the loss
 (approximately -sum_gradients / sum_hessians), and w_p is the weight of the parent node

note that the parent output w_p itself has smoothing applied, unless it is the root node,
 so that the smoothing effect accumulates with the tree depth
'''

#['l1', 'l2']

hyper_params = {'task': 'train',
                'boosting': 'gbdt',
                'objective': 'regression',
                'metric': ['l1', 'huber', 'r2'],
                'learning_rate': 0.05,
                'num_iterations': 800,
                'feature_fraction': 0.8,
                'bagging_fraction': 0.7,'bagging_freq': 10,
                'verbose': 0,
                'extra_trees': True,
                "max_depth": 50,
                "num_leaves": 128,
                "max_bin": 512}

gbm = lgb.LGBMRegressor(**hyper_params)

gbm.fit(X_train_LGBM, y_train_LGBM,
        eval_set=[(X_val, y_val)],
        eval_metric=['l1', 'huber', 'r2'])

"""###Fit"""

gbm = lgb.LGBMRegressor(**hyper_params)

gbm.fit(X_train_LGBM, y_train_LGBM,
        eval_set=[(X_val, y_val)],
        eval_metric=['l1', 'huber', 'r2'])

"""### Prediction/ Graphs"""

y_Sub = gbm.predict(X_test_LGBM)
y_pred_LGBM = gbm.predict(X_test)
y_train_pred_LGBM = gbm.predict(X_train_LGBM)


performance_metrics(y_test, y_pred_LGBM, y_train_LGBM, y_train_pred_LGBM, 'LGBMRegressor')

"""### Submission"""

# Créer un DataFrame avec les ID et les prédictions
submission_df = pd.DataFrame({
    'id': test['id'],
    'sales': y_Sub
})

# Enregistrer le DataFrame au format CSV
submission_df.to_csv('submission.csv', index=False)

"""#Other"""

