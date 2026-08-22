import pandas as pd
from sqlalchemy import create_engine

distributor_master = pd.read_csv(r"/Users/hakhanhlinh/Unigap Python/DAC K46/VietDist_SampleData/SRC06_distributor_master.csv")
print(distributor_master)

#tao connection den postgres
connection_string = (
    "postgresql+psycopg2://postgres:Hkl%4022052001@localhost:5432/postgres"
)

#tao engine de truyen bien connection string vao
engine = create_engine(connection_string)
print(engine) 

#day du lieu tu dataframe vao postgres
distributor_master.to_sql(
    name = "Distributor_Master",
    con = engine,
    if_exists = "replace",
    schema = "bronze"
)
#if_exists = "replace" : neu bang da ton tai thi xoa bang cu va tao bang moi
#if_exists = "append" : neu bang da ton tai thi union du lieu vao bang cu
#if_exists = "fail" : neu bang da ton tai thi bao loi va khong lam gi ca