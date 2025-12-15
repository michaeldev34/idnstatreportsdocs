import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller, kpss, grangercausalitytests
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.tsa.api import VAR
from scipy import stats
import matplotlib.pyplot as plt


#Set of classes that are common in both classes
# next implement eror handling everywhere possibl ebix bb 

class NonStatisticalReports:
    def __init__(self, label: str, data_type: str):
        self.label = label
        self.data_type = data_type.lower().strip()
        self.results = []

class StatisticalReports: 
    """distintions of algorithm are, its divided in wether a dataset 
    is either small or big data, with use of linear or non linear methods, based on premise that either we have more than 30 datapoints or nt
    so to instead use hypotesis tetsing or corrrealtions, disintinguising between linear or non linear methods 
    testing linearitybat first to decide which methods to use."""

    def __init__(self, label: str, data_type: str, panel_type: str):
        self.label = label
        self.data_type = data_type.lower().strip()
        self.results = []
        self.panel_type = panel_type.lower().strip()

        if self.data_type not in {"time_series", "cross_section", "panel"}:
            raise ValueError(
                f"Invalid dtype='{data_type}'. Must be one of: "
                "time_series, cross_section, panel"
            )
        
        if self.panel_type not in {"fixed", "unfixed"}:
            raise ValueError(
                f"Invalid panel_type='{panel_type}'. Must be one of: "
                "fixed, unfixed"
            )
        
    class KPIs:
        def __init__(self, label):
            self.label = label
            self.results = []

        def add(self, value):
            self.results.append(value)

        class marketing:
            def conversion_rate(self, data):
                pass

            def marketing_dataset(self):
                pass

        class administration:
            def administration_dataset(self):
                pass

        class operations:
            def oee(self, data):
                pass
            def units_produced_per_hour(self, data):
                pass
            def operations_dataset(self):
                pass

        class finance:
            def finance_dataset(self):
                pass
        
        class human_resources:
            def human_dataset(self):
                pass

        class legal_compliance:
            def legalandcompliance_dataset(self):
                pass

        class sales_commercial:
            def salesandcommercial_dataset(self):
                pass

        class technologhy:
            def technologhy_dataset(self):
                pass

        class product:
            def yield_rate(self, data):
                pass
            def defect_rate(self, data):
                pass
            def product_dataset(self):
                pass

        class customer_support:
            def customer_satisfaction(self, data):
                pass
            def customer_retention(self, data):
                pass
            def customer_dataset(self):
                pass

        class health_safety_environment:
            def health_safety_environment_dataset(self):
                pass

        def summary_table(self):
            pass

        
    class Preprocessing:
        def __init__(self, label):
            self.label = label
            self.results = []

        def add(self, value):
            self.results.append(value)

        def set_dataset(self, data):
            self.data = data
    
        class Tests:
            class mcoassumptions:
                def aleatorysample(self, data):
                    if self.data_type == "time_series":
                        print(False)
                        pass
                    elif self.data_type == "cross_section":
                        print(True)
                        pass
                    elif self.data_type == "panel":
                        print(False)
                        pass

                def independent_observations(self, data):
                    if self.data_type == "time_series":
                        print(False)
                        pass
                    elif self.data_type == "cross_section":
                        print(False)
                        pass
                    elif self.data_type == "panel":
                        print(True)
                        pass

                def condmedcero_strongexhogeneity(self, data):

                    if self.data_type == "time_series":
                        print(True)
                        pass
                    elif self.data_type == "cross_section":
                        print(False)
                        pass
                    elif self.data_type == "panel":
                        print(True)

                        if self.panel_type == "fixed":
                            print(True)

                        elif self.panel_type == "unfixed":
                            print(True)
                        

                def homocedasticity(self, data):
                    if self.data_type == "time_series":
                        print(True)
                        pass
                    elif self.data_type == "cross_section":
                        print(True)
                        pass
                    elif self.data_type == "panel":
                        print(True)
                        pass

                def noautocorrelation(self, data):
                    if self.data_type == "time_series":
                        print(True)
                        pass
                    elif self.data_type == "cross_section":
                        print(True)
                        pass
                    elif self.data_type == "panel":
                        print(True)
                        pass
                    

                def normalityresiduals(self, data):
                    if self.data_type == "time_series":
                        print(True)
                        pass
                    elif self.data_type == "cross_section":
                        print(True)
                        pass
                    elif self.data_type == "panel":
                        print(True)
                        if "n" in data.columns and "t" in data.columns: # if t and n are small enough 
                            print("Time series data")
                        
                    

            def trend(self, data):
                if self.data_type == "time_series":
                    print(True)
                    pass
                elif self.data_type == "cross_section":
                    print(False)
                    pass
                elif self.data_type == "panel":
                    print(True)
                    #decide here if detect it by observation or incommon 
                    pass
                

            def drift(self, data):
                if self.data_type == "time_series":
                    print(True)
                    pass
                elif self.data_type == "cross_section":
                    print(False)
                    pass
                elif self.data_type == "panel":
                    print(True)
                    #decide here if detect it by observation or incommon 
                    pass
                

            def order_integration(self, data):
                #for stationarity
                if self.data_type == "time_series":
                    print(True)
                    pass
                elif self.data_type == "panel":
                    print(True)
                    if "T" in data.columns: # if its BIG ONLY 
                        print(True)
                    pass
                else:
                    print("Is Cross Section Data, Order of integration not applicable")
                    
                    def unitroot(self, data):
                        pass

            def summary_table(self):
                    
                    df = pd.DataFrame(self.results, columns=["Test", "Result"])
                    return df

                    pass
            
    class Processing:
        #datasets >= 30 points
        class classic_statistics:
            def corr_matrix(self, data):
                pass

            def hypothesis_testing(self, data):
                pass

            def anova(self, data):
                pass

            def summary_table(self):
                pass


        class cross_validation:
            def split(self, data):
                pass
            def summary_table(self):
                pass
        
        class Models:
            class SmallData:
                #datasets <= 5000 points
                def multiple_linear_regression(self, data):
                    pass

                def ecm(self, data):
                    pass

                def vecm(self, data):
                    pass

                def granger_causality(self, data):
                    pass    

                def summary_table(self):
                    pass

            class BigData:
                #datasets > 5000 points
                def arima(self, data):
                    pass

                def garch(self, data):
                    pass

                def varima(self, data):
                    pass
                def random_forest(self, data):
                    pass

                def xgboost(self, data):
                    pass

                def neural_networks(self, data):
                    pass

                def summary_table(self):
                    pass

    class Explanation:
        def prediction(self, data):
            pass
        
        def thirtynext_period_forecast(self, data):
            pass

        def data_visualization(self, data):
            pass

        def summary_table(self):
            pass

        def interpretation(self, data):
            pass

    class report_generation:
        def pdf(self, data):
            pass

            
"""EXAMPLE USE:
statsreports = StatisticalReports("company_one", "time_series")
preprocessing statsreports.Preprocessing()
explanation = statsreports.Explanation()
reports = statsreports.report_generation()

df = preprocessing.set_dataset(data)
kpi_results = preprocessing.KPIs.summary_table(df)
tests_results = preprocessing.summary_table(df)
forecast30days = statsreports.Processing.summary_table()
pdf = reports.pdf(df.concat([kpi_results, tests_results, forecast30days]))

"""

            


class SmallData:
    self.experiments = DataProperties('Small Data experiments')
    self.experiments.Tests = DataProperties()

    summary_table = DataProperties.summary_table(data, datatype="timeseries", ..)

class BigData:
    self.experiments = DataProperties('Big Data experiments')
    
cross secitrona, panel data, time series data  

big data small data DONE

linear vs non linear models 

    


# --- IGNORE ---


