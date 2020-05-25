# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import tensorflow as tf
import tempfile
#!pip install seaborn==0.8.1
import seaborn as sns
import itertools
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.metrics import precision_recall_curve
from google.colab import widgets
# For facets
from IPython.core.display import display, HTML
import base64
#!pip install facets-overview==1.0.0
from facets_overview.feature_statistics_generator import FeatureStatisticsGenerator

print('Modules are imported.')

COLUMNS = ["age", "workclass", "fnlwgt", "education", "education_num",
           "marital_status", "occupation", "relationship", "race", "gender",
           "capital_gain", "capital_loss", "hours_per_week", "native_country",
           "income_bracket"]

train_df = pd.read_csv(
    "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data",
    names=COLUMNS,
    sep=r'\s*,\s*',
    engine='python',
    na_values="?")
test_df = pd.read_csv(
    "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.test",
    names=COLUMNS,
    sep=r'\s*,\s*',
    skiprows=[0],
    engine='python',
    na_values="?")

# Drop rows with missing values
train_df = train_df.dropna(how="any", axis=0)
test_df = test_df.dropna(how="any", axis=0)

print('UCI Adult Census Income dataset loaded.')

#@title Visualize the Data in Facets
fsg = FeatureStatisticsGenerator()
dataframes = [
    {'table': train_df, 'name': 'trainData'}]
censusProto = fsg.ProtoFromDataFrames(dataframes)
protostr = base64.b64encode(censusProto.SerializeToString()).decode("utf-8")


HTML_TEMPLATE = """<script src="https://cdnjs.cloudflare.com/ajax/libs/webcomponentsjs/1.3.3/webcomponents-lite.js"></script>
        <link rel="import" href="https://raw.githubusercontent.com/PAIR-code/facets/1.0.0/facets-dist/facets-jupyter.html">
        <facets-overview id="elem"></facets-overview>
        <script>
          document.querySelector("#elem").protoInput = "{protostr}";
        </script>"""
html = HTML_TEMPLATE.format(protostr=protostr)
display(HTML(html))

#@title Set the Number of Data Points to Visualize in Facets Dive

SAMPLE_SIZE = 2500 #@param
  
train_dive = train_df.sample(SAMPLE_SIZE).to_json(orient='records')

HTML_TEMPLATE = """<script src="https://cdnjs.cloudflare.com/ajax/libs/webcomponentsjs/1.3.3/webcomponents-lite.js"></script>
        <link rel="import" href="https://raw.githubusercontent.com/PAIR-code/facets/1.0.0/facets-dist/facets-jupyter.html">
        <facets-dive id="elem" height="600"></facets-dive>
        <script>
          var data = {jsonstr};
          document.querySelector("#elem").data = data;
        </script>"""
html = HTML_TEMPLATE.format(jsonstr=train_dive)
display(HTML(html))

feature = 'capital_gain / capital_loss' #@param ["", "hours_per_week", "fnlwgt", "gender", "capital_gain / capital_loss", "age"] {allow-input: false}


if feature == "hours_per_week":
  print(
'''It does seem a little strange to see 'hours_per_week' max out at 99 hours,
which could lead to data misrepresentation. One way to address this is by
representing 'hours_per_week' as a binary "working 40 hours/not working 40
hours" feature. Also keep in mind that data was extracted based on work hours
being greater than 0. In other words, this feature representation exclude a
subpopulation of the US that is not working. This could skew the outcomes of the
model.''')
if feature == "fnlwgt":
  print(
"""'fnlwgt' represents the weight of the observations. After fitting the model
to this data set, if certain group of individuals end up performing poorly 
compared to other groups, then we could explore ways of reweighting each data 
point using this feature.""")
if feature == "gender":
  print(
"""Looking at the ratio between men and women shows how disproportionate the data
is compared to the real world where the ratio (at least in the US) is closer to
1:1. This could pose a huge probem in performance across gender. Considerable
measures may need to be taken to upsample the underrepresented group (in this
case, women).""")
if feature == "capital_gain / capital_loss":
  print(
"""Both 'capital_gain' and 'capital_loss' have very low variance, which might
suggest they don't contribute a whole lot of information for predicting income. It
may be okay to omit these features rather than giving the model more noise.""")
if feature == "age":
  print(
'''"age" has a lot of variance, so it might benefit from bucketing to learn
fine-grained correlations between income and age, as well as to prevent
overfitting.''')

def csv_to_pandas_input_fn(data, batch_size=100, num_epochs=1, shuffle=False):
  return tf.estimator.inputs.pandas_input_fn(
      x=data.drop('income_bracket', axis=1),
      y=data['income_bracket'].apply(lambda x: ">50K" in x).astype(int),
      batch_size=batch_size,
      num_epochs=num_epochs,
      shuffle=shuffle,
      num_threads=1)

print('csv_to_pandas_input_fn() defined.')

#@title Categorical Feature Columns

# Since we don't know the full range of possible values with occupation and
# native_country, we'll use categorical_column_with_hash_bucket() to help map
# each feature string into an integer ID.
occupation = tf.feature_column.categorical_column_with_hash_bucket(
    "occupation", hash_bucket_size=1000)
native_country = tf.feature_column.categorical_column_with_hash_bucket(
    "native_country", hash_bucket_size=1000)

# For the remaining categorical features, since we know what the possible values
# are, we can be more explicit and use categorical_column_with_vocabulary_list()
gender = tf.feature_column.categorical_column_with_vocabulary_list(
    "gender", ["Female", "Male"])
race = tf.feature_column.categorical_column_with_vocabulary_list(
    "race", [
        "White", "Asian-Pac-Islander", "Amer-Indian-Eskimo", "Other", "Black"
    ])
education = tf.feature_column.categorical_column_with_vocabulary_list(
    "education", [
        "Bachelors", "HS-grad", "11th", "Masters", "9th",
        "Some-college", "Assoc-acdm", "Assoc-voc", "7th-8th",
        "Doctorate", "Prof-school", "5th-6th", "10th", "1st-4th",
        "Preschool", "12th"
    ])
marital_status = tf.feature_column.categorical_column_with_vocabulary_list(
    "marital_status", [
        "Married-civ-spouse", "Divorced", "Married-spouse-absent",
        "Never-married", "Separated", "Married-AF-spouse", "Widowed"
    ])
relationship = tf.feature_column.categorical_column_with_vocabulary_list(
    "relationship", [
        "Husband", "Not-in-family", "Wife", "Own-child", "Unmarried",
        "Other-relative"
    ])
workclass = tf.feature_column.categorical_column_with_vocabulary_list(
    "workclass", [
        "Self-emp-not-inc", "Private", "State-gov", "Federal-gov",
        "Local-gov", "?", "Self-emp-inc", "Without-pay", "Never-worked"
    ])

print('Categorical feature columns defined.')

#@title Numeric Feature Columns
# For Numeric features, we can just call on feature_column.numeric_column()
# to use its raw value instead of having to create a map between value and ID.
age = tf.feature_column.numeric_column("age")
fnlwgt = tf.feature_column.numeric_column("fnlwgt")
education_num = tf.feature_column.numeric_column("education_num")
capital_gain = tf.feature_column.numeric_column("capital_gain")
capital_loss = tf.feature_column.numeric_column("capital_loss")
hours_per_week = tf.feature_column.numeric_column("hours_per_week")

print('Numeric feature columns defined.')

age_buckets = tf.feature_column.bucketized_column(
    age, boundaries=[18, 25, 30, 35, 40, 45, 50, 55, 60, 65])
    
    # List of variables, with special handling for gender subgroup.
variables = [native_country, education, occupation, workclass,
             relationship, age_buckets]
subgroup_variables = [gender]
feature_columns = variables + subgroup_variables

deep_columns = [
    tf.feature_column.indicator_column(workclass),
    tf.feature_column.indicator_column(education),
    tf.feature_column.indicator_column(age_buckets),
    tf.feature_column.indicator_column(gender),
    tf.feature_column.indicator_column(relationship),
    tf.feature_column.embedding_column(native_country, dimension=8),
    tf.feature_column.embedding_column(occupation, dimension=8),
]

print(deep_columns)
print('Deep columns created.')

#@title Define Deep Neural Net Model

HIDDEN_UNITS = [1024, 512] #@param
LEARNING_RATE = 0.1 #@param
L1_REGULARIZATION_STRENGTH = 0.0001 #@param
L2_REGULARIZATION_STRENGTH = 0.0001 #@param

model_dir = tempfile.mkdtemp()
single_task_deep_model = tf.estimator.DNNClassifier(
    feature_columns=deep_columns,
    hidden_units=HIDDEN_UNITS,
    optimizer=tf.train.ProximalAdagradOptimizer(
      learning_rate=LEARNING_RATE,
      l1_regularization_strength=L1_REGULARIZATION_STRENGTH,
      l2_regularization_strength=L2_REGULARIZATION_STRENGTH),
    model_dir=model_dir)

print('Deep neural net model defined.')

#@title Fit Deep Neural Net Model to the Adult Training Dataset

STEPS = 1000 #@param

single_task_deep_model.train(
    input_fn=csv_to_pandas_input_fn(train_df, num_epochs=None, shuffle=True),
    steps=STEPS);

print('Deep neural net model is done fitting.')

#@title Evaluate Deep Neural Net Performance

results = single_task_deep_model.evaluate(
    input_fn=csv_to_pandas_input_fn(test_df, num_epochs=1, shuffle=False),
    steps=None)
print("model directory = %s" % model_dir)
print("---- Results ----")
for key in sorted(results):
  print("%s: %s" % (key, results[key]))
  
  #@test {"output": "ignore"}
#@title Define Function to Compute Binary Confusion Matrix Evaluation Metrics
def compute_eval_metrics(references, predictions):
  tn, fp, fn, tp = confusion_matrix(references, predictions).ravel()
  precision = tp / float(tp + fp)
  recall = tp / float(tp + fn)
  false_positive_rate = fp / float(fp + tn)
  return precision, recall, false_positive_rate

print('Binary confusion matrix and evaluation metrics defined.')

#@title Define Function to Visualize Binary Confusion Matrix
def plot_confusion_matrix(confusion_matrix, class_names, figsize = (8,6)):
    # We're taking our calculated binary confusion matrix that's already in form 
    # of an array and turning it into a Pandas DataFrame because it's a lot 
    # easier to work with when visualizing a heat map in Seaborn.
    df_cm = pd.DataFrame(
        confusion_matrix, index=class_names, columns=class_names, 
    )
    fig = plt.figure(figsize=figsize)
    
    # Combine the instance (numercial value) with its description
    strings = np.asarray([['True Positives', 'False Negatives'],
                          ['False Positives', 'True Negatives']])
    labels = (np.asarray(
        ["{0:d}\n{1}".format(value, string) for string, value in zip(
            strings.flatten(), confusion_matrix.flatten())])).reshape(2, 2)

    heatmap = sns.heatmap(df_cm, annot=labels, fmt="");
    heatmap.yaxis.set_ticklabels(
        heatmap.yaxis.get_ticklabels(), rotation=0, ha='right')
    heatmap.xaxis.set_ticklabels(
        heatmap.xaxis.get_ticklabels(), rotation=45, ha='right')
    plt.ylabel('References')
    plt.xlabel('Predictions')
    return fig

print('Binary confusion matrix visualization defined.')

#@title Visualize Binary Confusion Matrix and Compute Evaluation Metrics Per Subgroup
CATEGORY  =  "gender" #@param {type:"string"}
SUBGROUP =  "Male" #@param {type:"string"}

# Given define subgroup, generate predictions and obtain its corresponding 
# ground truth.
predictions_dict = single_task_deep_model.predict(input_fn=csv_to_pandas_input_fn(
    test_df.loc[test_df[CATEGORY] == SUBGROUP], num_epochs=1, shuffle=False))
predictions = []
for prediction_item, in zip(predictions_dict):
    predictions.append(prediction_item['class_ids'][0])
actuals = list(
    test_df.loc[test_df[CATEGORY] == SUBGROUP]['income_bracket'].apply(
        lambda x: '>50K' in x).astype(int))
classes = ['Over $50K', 'Less than $50K']

# To stay consistent, we have to flip the confusion 
# matrix around on both axes because sklearn's confusion matrix module by
# default is rotated.
rotated_confusion_matrix = np.fliplr(confusion_matrix(actuals, predictions))
rotated_confusion_matrix = np.flipud(rotated_confusion_matrix)

tb = widgets.TabBar(['Confusion Matrix', 'Evaluation Metrics'], location='top')

with tb.output_to('Confusion Matrix'):
  plot_confusion_matrix(rotated_confusion_matrix, classes);

with tb.output_to('Evaluation Metrics'):
  grid = widgets.Grid(2,3)

  p, r, fpr = compute_eval_metrics(actuals, predictions)

  with grid.output_to(0, 0):
    print('Precision ')
  with grid.output_to(1, 0):
    print(' %.4f ' % p)

  with grid.output_to(0, 1):
    print(' Recall ')
  with grid.output_to(1, 1):
    print(' %.4f ' % r)

  with grid.output_to(0, 2):
    print(' False Positive Rate ')
  with grid.output_to(1, 2):
    print(' %.4f ' % fpr)
    