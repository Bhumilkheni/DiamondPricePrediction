import os
import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer  # Handeling Missing value

#pipeline
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder  # ordinal encoding
from sklearn.preprocessing import StandardScaler  # handeling feature scaling

from src.exception import customException
from src.logger import logging
from src.utils import save_object


## Data Transformation config
@dataclass
class DataTransformationconfig:
    preprocessor_ob_file_path=os.path.join('artifacts','preprocessor.pkl')


## Data Ingestionconfig class

class DataTransformation:
    def __init__(self):
        self.data_transformation_config=DataTransformationconfig()

    def get_data_transformation_object(self):
        try:
            logging.info("Data Transformation initiated")
            #Define which column should be ordinal encoded and which should be scaled value
            numerical_cols=['carat', 'depth', 'table', 'x', 'y', 'z']
            categorical_cols=['cut', 'color', 'clarity']
            # Define the custom ranking for each ordinal variable
            cut_categories = ['Fair', 'Good', 'Very Good','Premium','Ideal']
            color_categories = ['D', 'E', 'F', 'G', 'H', 'I', 'J']
            clarity_categories = ['I1','SI2','SI1','VS2','VS1','VVS2','VVS1','IF']
            logging.info('Pipeline initiated')
            ## Numerical Pipeline
            num_pipeline=Pipeline(
                steps=[
                    ('imputer',SimpleImputer(strategy='median')),
                    ('scaler',StandardScaler())   
                ]
            )

            ## Categorical Pipeline
            cat_pipeline=Pipeline(
                steps=[
                    ('imputer',SimpleImputer(strategy='most_frequent')),
                    ('ordinalencoder',OrdinalEncoder(categories=[cut_categories,color_categories,clarity_categories])),
                    ('sclaer',StandardScaler())
                ]
            )

            preprocessor=ColumnTransformer([
                ('num_pipeline',num_pipeline,numerical_cols),
                ('cat_pipeline',cat_pipeline,categorical_cols)
            ])
            return preprocessor
            
            logging.info("Pipeline Completed")
        except Exception as e:
            logging.info("Error in Data Transformation")
            raise customException(e,sys)

    def initiate_data_transformation_object(self,train_path,test_path):
        try:
            #reading train and test data
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)

            logging.info('Read train and test data completed')
            logging.info(f'Train DataFrame Head: \n{train_df.head().to_string()}')
            logging.info(f'Test DataFrame Head: \n{test_df.head().to_string()}')

            logging.info('Obtaining preprocessing object')

            preprocessing_obj=self.get_data_transformation_object()

            target_column_value='price'
            drop_columns=[target_column_value,'id']

            # feature into independent and dependent feature
            input_feature_train_df=train_df.drop(columns=drop_columns,axis=1)
            target_feature_train_df=train_df[target_column_value]

            input_feature_test_df=train_df.drop(columns=drop_columns,axis=1)
            target_feature_test_df=train_df[target_column_value]

            ## apply the transformation
            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr=preprocessing_obj.transform(input_feature_test_df)

            logging.info('Applying preprocessing object on training and testing dataset')

            train_arr=np.c_[input_feature_train_arr,np.array(target_feature_train_df)]
            test_arr=np.c_[input_feature_test_arr,np.array(target_feature_test_df)]

            save_object(
                file_path=self.data_transformation_config.preprocessor_ob_file_path,
                obj=preprocessing_obj
            )

            logging.info('preprocessor pickle is created and saved')
            return(
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_ob_file_path
            )

        except Exception as e:
            raise customException(e,sys)