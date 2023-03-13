# Swiggy-bills-analysis
The Swiggy Data Pipeline, help me analyse the cost behind my weekly foodbills along with my favourite food, cuisine and restaurants wherever I travel.


This repository includes designing an ETL pipeline for extraction of personal bills from GMAIL using API and processing it using AWS Services such as S3, Lambda, Glue, Redshift


The techstack used in this pipeline  
•	Language: Python
•	Gmail API(Data Extraction)
•	AWS : LAMBDA, S3, Glue, Redshift


Pipeline: Gmail API ---->Lambda------>S3------> AWS GLUE(transformation of Data)------>S3----->Redshift




Datawarehouse – Redshift
Lambda--> invoking of lambda function to extract pdf bills from source to destination
AWS Glue--> format the semi structured pdf data to csv 
Redshift--> Datawarehouse, which comprise of modelled data which can be used for visualization in future


