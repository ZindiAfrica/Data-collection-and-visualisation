# This code creates a text classifying model
# Categories relate to gender based violence
# In addition creating a model used on our website, this code serves as a tutorial

# package used to store objects on your disk
# used to write text classifying model for later use
import pickle

# package for data manipulation and analysis
import pandas as pd

# fastai is the package we use to create a text classifier
# it's an easy to use package
# in particular, it comes with a model that has already been trained to understand english
# therefore, all we need to do is train the model to classify gbv tweets
# this is called transfer learning
from fastai.text.all import (
    TextDataLoaders,
    language_model_learner,
    AWD_LSTM,
    accuracy,
    text_classifier_learner,

)

# Read in text data - only a sample is required to train and validate the model
tweets = pd.read_csv('data/landing_zone/TwitterDataSets/Set3/Tweets.csv').sample(frac=0.75)


# prepare the data for fastai use
# we are going to train our model to predict 'semi type' classes (GBV type) using the text column
# 20% of the data is used for validation to verify our results
dls_lm = TextDataLoaders.from_df(
    tweets,
    text_col='tweet',
    label_col='semi_type',
    valid_pct=0.20,
    bs=64,
    is_lm=True
)

# Firstly, we teach our language model to understand the style of text in tweets
learn = language_model_learner(dls_lm, AWD_LSTM, drop_mult=0.3)
learn.fit_one_cycle(3, 1e-2)
learn.save_encoder('finetuned')


# Secondly, we teach our model to predict types of GBV in tweets
# like above, we first prepare data for fastai package use
dls_clas = TextDataLoaders.from_df(
    tweets,
    valid_pct=0.2,
    text_col='tweet',
    label_col='semi_type',
    bs=64,
    text_vocab=dls_lm.vocab
)

learn = text_classifier_learner(dls_clas, AWD_LSTM, drop_mult=0.5, metrics=accuracy).to_fp16()
learn = learn.load_encoder('finetuned')

# graph which helps us determine our models appropriate learning rate
# initially set to 2e-3 = 0.002
learn.lr_find()

# Accuracy =  0.814628 after first iteration of fitting model
learn.fit_one_cycle(1, 2e-3)


# Accuracy -  0.960643 after second iteration of fitting model
learn.freeze_to(-2)
learn.fit_one_cycle(1, 3e-3)

# Accuracy -  0.999 after second iteration of fitting model
learn.freeze_to(-4)
learn.fit_one_cycle(1, 5e-3)

with open('data/processed/tweets/tweet_classifier.pickle', 'wb') as handle:
    pickle.dump(
        learn,
        handle,
        protocol=pickle.HIGHEST_PROTOCOL
    )
