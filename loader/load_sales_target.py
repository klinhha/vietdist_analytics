import pandas as pd
from sqlalchemy import create_engine

sales_target = pd.read_excel(r"/Users/hakhanhlinh/Unigap Python/DAC K46/VietDist_SampleData/SRC02_sales_target_plan.xlsx")
print(sales_target)
connection_string = (
    "postgresql+psycopg2://postgres:Hkl%4022052001@localhost:5432/postgres"
)

engine = create_engine(connection_string)
print(engine) 

sales_target.to_sql(
    name = "Sales_Target",
    con = engine,
    if_exists = "replace",
    schema = "bronze"
)