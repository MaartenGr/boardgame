## Table of Contents
<a name="toc"/></a>

1. [Introduction](#introduction)

    a. [Goal of Project](#introduction-goal)

    b. [Deliverable](#introduction-deliverable)
    
2. [Document Structure](#documentstructure)
3. [Data](#data)
4. [Feature Engineering](#featureengineering)

    a. [Preprocessing Steps](#featureengineering-preprocessing)

    b. [New Variables](#featureengineering-newvariables)
    
    c. [Outlier Removal](#featureengineering-outlier)
    
    d. [Feature Selection](#featureengineering-featureselection)
    
    e. [One-hot Encoding](#featureengineering-onehotencoding)
    
    f. [Things that did not work](#featureengineering-things)
        
5. [Sampling](#sampling)
6. [Modeling](#modeling)

    a. [Hyperparameter Optimization](#modeling-hyperparameter)

    b. [Validation](#modeling-validation)
    
7. [Results](#results)

    a. [5-fold CV](#results-cv)

    b. [Holdout](#results-holdout)
    
    c. [Calibrating probabilities](#results-calibrating)
    
    d. [Impact Train Size](#results-trainsize)
    
    e. [Job Titles](#results-jobtitles)
    
8. [MlFlow](#mlflow)
9. [SHAP](#shap)

    a. [SHapley Additive exPlanations](#shap-shapley)

    b. [Usage](#shap-usage)

10. [Server](#server)

    a. [Server Speed](#server-speed)
    
    b. [Server Speed](#server-dash)



## 1. Introduction
[Back to ToC](#toc)
<a name="introduction"/></a>

#### 1.a. Goal of Project
<a name="introduction-goal"/></a>
[Back to ToC](#toc)

The goal of this project is to predict, the moment an individual is hired, if that person will 
leave its job one year later.

Additionally, we believe that employers would like to know what makes a person leave or stay. 
In order to give that information, an algorithm called `SHAP` was used to estimate how 
important certain variables (such as Age, Traveltime, and Salary) are in making the prediction. 

This will allow employers to optimize what they are going to give potential employees in order
to stay as long as possible. 

#### 1.b. Deliverable  
<a name="introduction-deliverable"/></a>
[Back to ToC](#toc)

The product will be an API (microservice) which can be accessed to get the prediction and
its probability. Most likely, this will be displayed as being a gauge meter. 

The `SHAP` values will also be returned and are indicative of each feature's importance.  
In other words, which variables makes a person leave their job within a year? 
   
## 2. Document structure
<a name="documentstructure"/></a>
[Back to ToC](#toc)

Below you can find an overview of the document structure. 

```bash
.
├── api
|   └── Dictionaries
|   |    └── branche.pickle
|   |    └── cao.pickle
|   |    └── dienstverband.pickle
|   |    └── full_parttime.pickle
|   |    └── geslacht.pickle
|   |    └── index.pickle           # May contain different versions 
|   └── Model
|   |    └── model.pickle           # May contain different versions
|   |    └── parameters.pickle      # May contain different versions
|   └── app.py
|   └── app_dev.py
|   └── Dockerfile
|   └── requirements.txt
|   
├── create_model
|   └── data
|   |    └── data.csv               # Local version of SQL script, not used in production 
|   └── html_output
|   |    └── facets_profile.html
|   |    └── pandas_profile.html
|   └── mlruns                      # Contains experiment info; See MlFlow
|   └── exploration.py
|   └── extract.py
|   └── helpers.py                  # Backup; currently not used
|   └── load_data.py
|   └── modelling.py
|   └── Overview.ipynb
|   └── pipeline.py
|   └── preprocessing.py
|   └── requirements.txt
|   └── requirements_pipeline.txt
|   └── validation.py
| 
├── images                          # Images for the readme; too many to show
|
├── test_server
|   └── Dash                        # Used as an interface for the API
|   |    └── main.py           
|   |    └── branche.pickle           
|   |    └── cao.pickle           
|   |    └── dienstverband.pickle           
|   └── Test Connection.ipynb
|
└── .dockerignore
└── .gitignore
└── .gitlab-ci.yml
└── docker-compose.yml
└── docker-compose_dev.yml
└── README.md
```

Next, I will go through the structure of the project in order to explain what 
each folder/file is used for.  


| Folder              | Description |
| ------------------- |:-----------:|
| `api` | Contains the main application served on either http://10.0.0.45:8084/docs (dev) or http://10.0.0.45:8085/docs (master)|
| `api/Dictionaries` | Contains several python dictionaries which are needed to translate key:value pairs. For example, gender 0 is converted to "female" |
| `api/Model` | Contains the model itself and the parameters that were used. |
| `create_model` | Several .py files associated with a different process in creating the model: extract.py :arrow_right: preprocessing.py :arrow_right: modelling.py :arrow_right: validation.py |
| `create_model/data` | Local variant of the data. This is not used in production and only for testing/debugging purposes. |
| `create_model/html_output` | HTML output of automatic dashboarding tools. Simply open the file to explore the data. |
| `create_model/mlruns` | Folder that contains all results of the experiments. See MlFlow below for instructions.  |
| `images` | Images for README + Results |
| `test_server` | Notebook which can be used to test the API in python.  |
| `test_server/Dash` | Dashboard for visualizing how the API could be used. See Dash below for more instructions.  |

## 3. Data
<a name="data"/></a>
[Back to ToC](#toc)

Data was retrieved (in Python) using the following SQL-statement:
```shell
Select * from 
    (
    SELECT h.*
    FROM DS.dbo.r_stg_riskofturnover h
    JOIN
        (
        SELECT MIN(VerloningPeriode_PK) VerloningPeriode_PK, Identificatie_PK, Werkgever_PK
        FROM DS.dbo.r_stg_riskofturnover turnover
        GROUP BY Identificatie_PK, Werkgever_PK
        ) m 
    ON h.VerloningPeriode_PK = m.VerloningPeriode_PK
    AND h.Identificatie_PK = m.Identificatie_PK
    AND h.Werkgever_PK = m.Werkgever_PK
    ) a
INNER JOIN
    (
    SELECT h.VerloningPeriode_PK Max_VerloningPeriode_PK, h.Identificatie_PK, h.Werkgever_PK
    FROM DS.dbo.r_stg_riskofturnover h
    JOIN
        (
            SELECT MAX(VerloningPeriode_PK) VerloningPeriode_PK, Identificatie_PK, Werkgever_PK
            FROM DS.dbo.r_stg_riskofturnover turnover
            GROUP BY Identificatie_PK, Werkgever_PK
        ) m 
    ON h.VerloningPeriode_PK = m.VerloningPeriode_PK
    AND h.Identificatie_PK = m.Identificatie_PK
    AND h.Werkgever_PK = m.Werkgever_PK
    ) b
ON a.Identificatie_PK = b.Identificatie_PK    
AND a.Werkgever_PK = b.Werkgever_PK       
```

**r_stg_riskofturnover** is a table which contains information with 
respect to the duration of contracts for individuals.


## 4. Feature Engineering
<a name="featureengineering"/></a>
[Back to ToC](#toc)

Since end-users will manually fill in most variables it is important that the number
of variables in the model is kept to a minimum. 

#### 4.a. Preprocessing steps  
<a name="featureengineering-preprocessing"/></a>
[Back to ToC](#toc)

The following preprocessing steps were partially based
on preprocessing steps performed in the Cox-variant:
* *SoortDienstverband_PK* 
    * 2 is replaced by 0 as it reduces noise and improves predictive power of model
* *RedenEindeDienstverband* 
    * Is either 0, 4, 5, 8 or 10
    * Others include being fired, death and pension
* *Leeftijd* (Age) 
    * Between 18 and 66 (inclusive)
* *Netto* (Salary) 
    * Should be higher than 100
* *EigenaarDirecteur* (Owner) 
    * Is not relevant and therefore excluded
* *Werkgevergrootte* 
    * Is at least 2
    * Binning this may result in improved scores as it would reduce noise captured
    in the extreme values 
* *RijstijdOverDeWegInMinuten* (TravelTimeInMinutes) 
    * Is lower or equal to 120 minutes
* *StartDateJob*
    * Should be at least begin of 2012
    * Although the year of contract is not included in the feature space I did want to 
    have jobs starting in at least 2012 such that we have the most recent data. 
    All data of events that happened quite some years ago could introduce noise 
    as they are less representative of the current situation. 
* *StartDateContract*
    * Before 2018-04 in order to remove EndDateContracts that have not appeared yet
    * Although this could be extended a bit more it is important to note that the target is based on having
    Verloningen at least 14 months after having received their first Verloning. Therefore, if it is currently May 2019, then the StartDateContract should be at most January 2018 to account for the 14 months as well as any delays in Verloning.
     
Additionally, I make sure that the target is actually correct by selecting, 
for each Dienstverband_PK, those that have either a difference 
in VerloningPeriode_PK of < 11 or > 13 if they match the target. 
Thus, those that have a difference of > 13 cannot have a target of 1 since they 
seem to stay after a year. 

The StartDateJob/StartDateContract and EndDateJob/EndDateContract do not match
with the actual amount of verloningen (payslips) a person actually got. Therefore, 
I choose to base the target on the amount of verloningen instead of the difference
between start- and end date. This highly improved the prediction quality.  

Moreover, I excluded 11, 12, and 13 since that introduces noise in the target
as these values are within a grey zone. It improved prediction quality. 

#### 4.b. New Variables  
<a name="featureengineering-newvariables"/></a>
[Back to ToC](#toc)

A set of new variables were created:
* *Hours* 
    * DeeltijdFactor * FtUren / 100
    * Or (if AfwijkendAantalUrenPerWeek != 0)
    * AfwijkendAantalUrenPerWeek * FtUren / 100
* *Target*
    * Whether somebody still has a contract after one year (0:yes / 1:no)

#### 4.c. Outlier removal  
<a name="featureengineering-outlier"/></a>
[Back to ToC](#toc)

Outliers were removed (> 3 std.) for the following variables:
* Basisloon
* BasisFulltimeMaandloon 
* BasisUurloon 
* Bruto 
* Netto
* FulltimePeriodeloon
* DeeltijdFactor 

Moreover, additional outliers were detected using an `IsolationForest`. 
The results show a small improvement in score which is why this algorithm was
additionally included. Outliers based on Std is mostly used to exclude extreme values 
whereas an IsolationForest also checks whether a sample is an outlier based on all its 
values. 

#### 4.d. Feature Selection  
<a name="featureengineering-featureselection"/></a>
[Back to ToC](#toc)

The following features were selected:
* Target
* ReistijdOverDeWegInMinuten 
* Full_Parttime_PK 
* Leeftijd
* Hours 
* Bruto
* FulltimePeriodeloon
* WerknemerAuto 
* Geslacht_PK
* Werkgevergrootte
* Branche_PK 
* Cao_PK
* SoortDienstverband_PK
* Maand 
* Provincie_Werkgever
* Provincie_Werknemer

NOTE: ISCO cannot be used due to the limited data. The target is imbalanced and 
limiting employees by using ISCO leads to insufficient data for training. 

#### 4.e. One-hot encoding  
<a name="featureengineering-onehotencoding"/></a>
[Back to ToC](#toc)

Due to the nature of categorical variables, several dummies were
created. For example, if you would have 4 categories labeled 
0, 1, 2 and 3, then the model would think that the value 2.5
makes sense. In reality this is not the case, therefore, we create
dummies for each category which gets the value 0 or 1 (boolean).
For the following variables dummies were created:
* Provincie_Werkgever 
* Provincie_Werknemer

NOTE: I did not apply one-hot encoding to Cao_PK (or other categorical features) since it had very little effect on the resulting
prediction. Moreover, although it is best practice, it is more difficult to bring into production.

#### 4.f. Things that did not work 
<a name="featureengineering-things"/></a>
[Back to ToC](#toc)

The following feature engineering steps were tried and were not effective in 
improving the quality of predictions:
* MinMax scaling
* Log transformation of Skewed columns
    * 'ReistijdOverDeWegInMinuten', 'Leeftijd', 'Basisloon', 'Bruto', 'MinimumPeriodeloon', 'Werkgevergrootte',
           'Heffingsplichtig', 'Average_Bruto_per_Cao',
           'Abs_Diff_Avg_Bruto_per_Cao'
* Interaction between set of two features:
    * Multiplication 
        * Not used due to collinearity 
    * Division
        * Not used due to collinearity 
* Interaction between features using DFS (Deep Feature Synthesis)      
* Using ISCO labels
    * It resulted in significantly less data and was therefore not useable  
* SMOTE
    * Higher score on CV, but lower on hold-out (also higher std based on cv folds)


## 5. Sampling
<a name="sampling"/></a>
[Back to ToC](#toc)

Due to the nature of the target its distribution is somewhat unbalanced (57:43). 
I choose to randomly sample rows with equal distribution of the target as 
sufficient data is available. Moreover, oversampling with `SMOTE` did note improve the results.  

A train data set of 150,000 rows was created for validating the model and optimizing
the hyperparameters. 
 
A hold-out data set of 10,000 rows was created, also with equal 
distribution of the target. This data set is used to test performance
after having found the right model(s) and set of parameters. It helps
to detect overfitting.   

## 6. Modeling
<a name="modeling"/></a>
[Back to ToC](#toc)

For the modeling I compared several models on their out-of-the-box
classification accuracy:

![alt text](images/models_new.png "Title Text") 

Aside from performing best, LightGBM was chosen due to its options prevent overfitting
through regularization and early stopping. Moreover, it is a fast model which can be
used to quickly iterate through different hyperparameters and preprocessing steps. 

**Reference to LightGBM**  
Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., ... & Liu, T. Y. 
(2017). Lightgbm: A highly efficient gradient boosting decision tree. 
In Advances in Neural Information Processing Systems (pp. 3146-3154).

#### 6.a. Hyperparameter optimization
<a name="modeling-hyperparameter"/></a>
[Back to ToC](#toc)

Using Random Grid Search (similar performance compared to 
to Bayesian optimization) the following hyperparameters were selected:
* objective: binary
* num_leaves: 59
* n_jobs: -1
* n_estimators: 200
* min_split_gain: 0.05
* min_child_weight: 0.56
* max_depth: -1
* learning_rate: 0.06999999999999999
* lambda_l2: 0
* lambda_l1: 1.5
* boosting: dart
* min_data_in_leaf: 100
* feature_fraction: 0.8
* bagging_freq: 10
* bagging_fraction: 0.8

#### 6.b. Validation
<a name="modeling-validation"/></a>
[Back to ToC](#toc)

Validation of performance was done using the following objective measures:
* Accuracy
* F1 score
* ROC-curves
* Precision
* Recall
* Brier Loss

Although accuracy gives information of its performance, it is wise to also
check its performance across other measures since it takes different situations 
into account. ROC-curves, for example, take into account how the model performs across
different threshold (probability thresholds). 

## 7. Results
<a name="results"/></a>
[Back to ToC](#toc)

The results are shown below and are split between a 5-fold CV on the train data and an 
additional holdout set for which to validate on. 
  
#### 7.a. 5-fold CV  
<a name="results-cv"/></a>
[Back to ToC](#toc)

* *Accuracy*
    * 0.7249 
* *F1*
    * 0.7226 
* *ROC_AUC*	
    * 0.7806  
* *Precision*
    * 0.7286  
* *Recall*
    * 0.7167  
* *Brier Loss*
    * 0.1902
        
#### 7.b. Holdout
<a name="results-holdout"/></a> 
[Back to ToC](#toc)

* *Accuracy*
    * 0.7304  
* *F1*
    * 0.7292 
* *ROC_AUC*	
    * 0.7304  
* *Precision*
    * 0.7324  
* *Recall*
    * 0.7260  
* *Brier Loss*
    * 0.1889

I specified AUC as the metric to optimize in the model which can
be seen in the results above since there was a little overfitting
on that metric in the CV. Moreover, the folds are stable which similarly demonstrates
a stable model in its predictions. 

![alt text](images/roc_model_new.png "Title Text")

#### 7.c. Calibrating probabilities
<a name="results-calibrating"/></a>
[Back to ToC](#toc)

All metrics above, except for Brier Loss, are based on whether the prediction itself is 
correct. In order to validate the probabilities Brier Loss was used to validate the 
quality of the probabilities.

However, these qualities can be further optimized in order to better represent the real 
fraction of positives we see in the data. 

The image below shows what happens when you calibrate the model, LightGBM, with 
`isotonic regression` and `Platt’s sigmoid model`. 

![alt text](images/calibration.png "Title Text")

You would like to optimize for the black dotted line as it shows a good distribution of
the fraction of positives versus the mean predicted value. The graphs show that LightGBM
already has a line very similar to the optimum. Thus, no additional calibration was needed. 

#### 7.d. Impact Train Size
<a name="results-trainsize"/></a>
[Back to ToC](#toc)

In order to check whether we actually have sufficient data for prediction I limited the amount 
of data for training. Next, the evaluation metrics were used for different training sizes. 

![alt text](images/effect_of_train_size_on_accuracy_new.png "Title Text")

The image above shows that after roughly 60,000 training samples the increase in most
evaluation metrics levels. This means that 90,000 training samples is sufficient in 
creating a strong model. More data will always help but the increase at this stage
is too low for it to affect the predictions significantly. 

#### 7.e. Job Titles
<a name="results-jobtitles"/></a>
[Back to ToC](#toc)

Here I check whether there are large differences in job titles between correct and 
incorrect predictions. The results below indicate that no major differences can be found
in the distribution of job titles. 
Thus, we can conclude that the model works equally well for all job titles.

**The most frequent job titles of the correct predictions**
![alt text](images/correct_prediction_title.png "Title Text")

**The most frequent job titles of the incorrect predictions**
![alt text](images/incorrect_prediction_title.png "Title Text")

## 8. MlFlow
<a name="mlflow"/></a>
[Back to ToC](#toc)

I used MlFlow to track the performance of models. If you would like to see the 
results, then make sure you are on a linux server. Then, simply ```cd``` to the
create_model folder and type in ```mlflow ui```. This will give open up a server at
http://127.0.0.1:5000 which you can use to access MlFlow.

![alt text](images/mlflow.png "Title Text")

## 9. SHAP
<a name="shap"/></a>
[Back to ToC](#toc)

#### 9.a. SHapley Additive exPlanations
<a name="shap-shapley"/></a>
[Back to ToC](#toc)

A (fairly) recent development has been the implementation of Shapley values into machine 
learning applications. In its essence, SHAP uses game theory to track the marginal 
contributions of each variable. For each variable, it randomly samples other values from 
the data set and calculates the change in your model score. These changes are then averaged 
for each variable to create a summary score, but also gives information on how important 
certain variables are for a specific data point.

#### 9.b. Usage
<a name="shap-usage"/></a>
[Back to ToC](#toc)

I use SHAP values to explain individual predictions to the user. This would help users 
understand why certain predictions were made and what they can do to change the prediction. 
The great thing about using such a method is that it creates more engagement with the user. 
They can simply try different values and quickly see the effect is has on the prediction. 
For example, let's say that the model predicts that a candidate will leave after a year. 
SHAP could then be used to explain why this is. If the main reason is salary and the 
employer is willing to raise it then the prediction might change.

More info: https://towardsdatascience.com/opening-black-boxes-how-to-leverage-explainable-machine-learning-dd4ab439998e

## 10. Server
<a name="server"/></a>
[Back to ToC](#toc)

The server will update automatically after a commit to the master.  
You can access the server and test predictions by simply going to:
  
**Master**
* 10.0.0.45:8080/docs
* 10.0.0.45:8080/redoc

**Dev**
* 10.0.0.45:8081/docs
* 10.0.0.45:8081/redoc

To access the server and test the prediction via python:
```python
import requests
to_predict_dict = {'reistijdoverdeweginminuten': 15.0,
                   'full_parttime_pk': 'Parttime',
                   'leeftijd': 30.0,
                   'bruto': 2200.0,
                   'werknemerauto': 2.0,
                   'geslacht_pk': 'Man',
                   'branche_pk': 'Onbekend',
                   'fulltimeperiodeloon': 1.0,
                   'maand': 1.0,
                   'werkgevergrootte': 29.0,
                   'hours': 20,
                   'cao_pk': 'Kinderopvang',
                   'premiegroep_pk': 13.0,
                   'heffingsplichtig': 2167.82,
                   'soortdienstverband_pk': 'Bepaalde tijd',
                   'werknemer': 'Limburg',
                   'werkgever': 'Limburg'}

url = 'http://10.0.0.45:8084/predict'
r = requests.get(url,params=to_predict_dict); r.json()
```

#### 10.a. Server Speed
<a name="server-speed"/></a>
[Back to ToC](#toc)

A 1000 requests results in the following time:
* Flask, Gunicon + NGINX (old tests)
    * 19.388221502304077
* FastAPI, Uvicorn, Gunicorn + NGINX (old tests)
    * 16.11115574836731

Note that more extensive tests are needed to be sure of the speed difference. 
However, FastApi has integrated OpenApi/ReDoc which helps with automatic documentation
of parameters. 

#### 10.b. Dash
<a name="server-dash"/></a>
[Back to ToC](#toc)

To create a PoC/MVP, I developed an interface using Dash in which the API can accessed. To access the interface, simply ```cd``` into the
test_server/Dash folder and type in ```python main.py```. This will give open up a server at
http://127.0.0.1:8050 which you can use to access the interface (see below).

![alt text](images/dash.png "Title Text")
