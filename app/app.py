# AUTOGENERATED! DO NOT EDIT! File to edit: ../store_sales_2.ipynb.

# %% auto 0
__all__ = ['iskaggle', 'creds', 'cred_path', 'path', 'train_df', 'test_df', 'sub_df', 'stores_df', 'oil_df', 'hol_events_df',
           'transactions_df', 'combined_df', 'test_idxs', 'train_idxs', 'valid_idxs', 'eq_start_date', 'eq_end_date',
           'earthquake_cond', 'earthquake_indexes', 'procs', 'cont', 'cat', 'train_val_splits', 'to']

# %% ../store_sales_2.ipynb 1
from fastai.tabular.all import *
from fastbook import *

from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_log_error

import seaborn as sns

from dtreeviz.trees import *
import dtreeviz

from treeinterpreter import treeinterpreter as ti
import waterfall_chart

from fastprogress import master_bar, progress_bar
from fastprogress.fastprogress import force_console_behavior


# %% ../store_sales_2.ipynb 3
iskaggle = os.environ.get('KAGGLE_KERNEL_RUN_TYPE', '')
creds = ''

# %% ../store_sales_2.ipynb 4
cred_path = Path('~/.kaggle/kaggle.json').expanduser()
if not cred_path.exists():
    cred_path.parent.mkdir(exist_ok=True)
    cred_path.write_text(creds)
    cred_path.chmod(0o600)

# %% ../store_sales_2.ipynb 5
path = Path('store-sales-time-series-forecasting')

# %% ../store_sales_2.ipynb 6
if not iskaggle and not path.exists():
    import zipfile, kaggle
    kaggle.api.competition_download_cli(str(path))    
    zipfile.ZipFile(f'{path}.zip').extractall(path)


# %% ../store_sales_2.ipynb 7
if iskaggle:
    path = Path('../input/store-sales-time-series-forecasting')
    ! pip install -q dataset

# %% ../store_sales_2.ipynb 9
train_df = pd.read_csv(path/'train.csv', low_memory=False)
test_df = pd.read_csv(path/'test.csv', low_memory=False)
sub_df = pd.read_csv(path/'sample_submission.csv', low_memory=False)
stores_df = pd.read_csv(path/'stores.csv', low_memory=False)
oil_df = pd.read_csv(path/'oil.csv', low_memory=False)
hol_events_df = pd.read_csv(path/'holidays_events.csv', low_memory=False)
transactions_df = pd.read_csv(path/'transactions.csv', low_memory=False)

# %% ../store_sales_2.ipynb 11
combined_df = pd.concat([train_df, test_df]).reset_index()

# %% ../store_sales_2.ipynb 14
test_idxs = combined_df.index[(combined_df.index > train_df.index.max())] 

# %% ../store_sales_2.ipynb 16
train_idxs = combined_df.index[(combined_df.index < round(len(train_df) * 0.8))]

# %% ../store_sales_2.ipynb 17
valid_idxs = combined_df.index[(combined_df.index > len(train_idxs)) & (combined_df.index < test_idxs.min())]

# %% ../store_sales_2.ipynb 20
combined_df = combined_df.merge(oil_df, on='date', how='left')

# %% ../store_sales_2.ipynb 22
combined_df = combined_df.merge(stores_df, on='store_nbr', how='left')

# %% ../store_sales_2.ipynb 24
hol_events_df.rename(columns={'type': 'hol_type'}, inplace=True)

# %% ../store_sales_2.ipynb 25
# combined_df = combined_df.merge(hol_events_df, on='date', how='left')

# %% ../store_sales_2.ipynb 27
combined_df['date'] = pd.to_datetime(combined_df['date'])

# %% ../store_sales_2.ipynb 29
eq_start_date = pd.to_datetime("2016-04-16")
eq_end_date = pd.to_datetime("2016-05-16")

# %% ../store_sales_2.ipynb 30
earthquake_cond = (combined_df.date >= eq_start_date) & (combined_df.date < eq_end_date)

# %% ../store_sales_2.ipynb 32
earthquake_indexes = combined_df.index[earthquake_cond]

# %% ../store_sales_2.ipynb 34
combined_df = add_datepart(combined_df, 'date')

# %% ../store_sales_2.ipynb 38
combined_df[dep_var] = np.log(combined_df[dep_var] + 1e-5)

# %% ../store_sales_2.ipynb 39
procs = [Categorify, FillMissing, Normalize]

# %% ../store_sales_2.ipynb 40
cont, cat = cont_cat_split(combined_df, 1, dep_var=dep_var)

# %% ../store_sales_2.ipynb 41
train_val_splits = (list(train_idxs), list(valid_idxs))

# %% ../store_sales_2.ipynb 42
to = TabularPandas(combined_df, procs, cat, cont, y_names=dep_var, splits=train_val_splits)
