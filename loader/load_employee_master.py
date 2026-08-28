#import pandas as pd
#from sqlalchemy import create_engine

#employee_master = pd.read_excel(r"/Users/hakhanhlinh/Unigap Python/DAC K46/VietDist_SampleData/SRC07_employee_master.xlsx")
#print(employee_master)

#tao connection den postgres
#connection_string = (
   # "postgresql+psycopg2://postgres:Hkl%4022052001@localhost:5432/postgres")

#tao engine de truyen bien connection string vao
#engine = create_engine(connection_string)
#print(engine) 

#day du lieu tu dataframe vao postgres
#employee_master.to_sql(
 #   name = "Employee_Master",
 #   con = engine,
  #  if_exists = "replace",
  #  schema = "bronze")
#if_exists = "replace" : neu bang da ton tai thi xoa bang cu va tao bang moi
#if_exists = "append" : neu bang da ton tai thi union du lieu vao bang cu
#if_exists = "fail" : neu bang da ton tai thi bao loi va khong lam gi ca


#semi-automation version
import pandas as pd

from drive_utils import (
    get_service_account,
    download_data,
    read_file
)

from db_utils import load_to_postgres

service = get_service_account()

buffer = download_data(service, file_id= '1w8m7d8Z7b0tE_xNLYv6KETypYf4un6Kj')

# Đọc tất cả các sheet
sheets = pd.read_excel(
    buffer,
    engine="openpyxl",
    sheet_name=None
)

print(sheets.keys())


# Lấy từng sheet
employee_v1 = sheets["Employee_v1_StartYear"]
employee_v2 = sheets["Employee_v2_Adjustment"]
change_log = sheets["Change_Log"]


# Thêm timestamp
recorded_at = pd.Timestamp.now()

employee_v1["recorded_at"] = recorded_at
employee_v2["recorded_at"] = recorded_at
change_log["recorded_at"] = recorded_at


# Load V1
load_to_postgres(
    employee_v1,
    table_name="Employee_Master_v1",
    schema="bronze",
    if_exists="replace"
)


# Load V2
load_to_postgres(
    employee_v2,
    table_name="Employee_Master_v2",
    schema="bronze",
    if_exists="replace"
)


# Load Change Log
load_to_postgres(
    change_log,
    table_name="Employee_Change_Log",
    schema="bronze",
    if_exists="replace")