#import pandas as pd
#from sqlalchemy import create_engine

#product_master = pd.read_excel(r"/Users/hakhanhlinh/Unigap Python/DAC K46/VietDist_SampleData/SRC04_product_master.xlsx")
#print(product_master)

#tao connection den postgres
#connection_string = (
 #   "postgresql+psycopg2://postgres:Hkl%4022052001@localhost:5432/postgres")

#tao engine de truyen bien connection string vao
#engine = create_engine(connection_string)
#print(engine) 

#day du lieu tu dataframe vao postgres
#product_master.to_sql(
  #  name = "Product_Master",
   # con = engine,
   # if_exists = "replace",
   # schema = "bronze")
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

buffer = download_data(service, file_id= '181ujzupADQ-4mimFM_swTowWHTVxppqa')

# 1. Đọc file
data = read_file('product_master.xlsx', buffer)


# 2. Thêm timestamp
data["recorded_at"] = pd.Timestamp.now()


# 3. Load vào Bronze
load_to_postgres(
    data,
    table_name="Product_Master",
    schema="bronze",
    if_exists="replace"
)