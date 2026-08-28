import os ## lấy tất cả thông tin từ hệ điều hành (operational system)

from urllib.parse import quote_plus  #biến ký tự đặc biệt trong password của postgres thành dạng an toàn để đưa vào URL

from io import BytesIO # cho phep tuong tac voi RAM bang python. tuc la luu du lieu vao RAM thay vi o dia.

import pandas as pd # pandas la thu vien xu ly du lieu tren python, pandas co kha nang doc du lieu tu bang, file excel, csv, json, sql, html, xml, parquet, feather, hdf5, msgpack, stata, sas7bdat, pickle va nhieu dinh dang khac.
from google.oauth2 import service_account # cho phep tuong tac vowi google  qua tai khoan service_account

# cho phep download meta data thong qua api
from googleapiclient.discovery import build  # build duong dan de download cac file tu gg storage/gg drive
from googleapiclient.http import MediaIoBaseDownload # cho phep download file ve va luu tru vao RAM

from sqlalchemy import create_engine # cho phep ket noi den database postgres

from dotenv import load_dotenv # thu vien cho phep doc file bien moi truong (env)

load_dotenv() 

# dinh nghia bien de python duoc phep vao bien moi truong env de lay duong dan den file json va ID ma khong lam lo thong tin (thay vi copy paste duong dan vao truc tiep thi de lam lo gia tri da luu tru)
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") # lay duong dan den file json service account tu file .env
FOLDER_DRIVE_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID") # lay ID cua folder tren Google Drive tu file .env

# Dinh nghia pham vi cong viec cua service account, tuc la cai quyen cua service acc xem no duoc phep lam gi tren gg
# Neu can service acc lam nhieu thi them nhieu scopes vao dsach, nhung o day chi can doc du lieu tren ggdrive nen chi lam 1 scope
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"] # service account chi co quyen doc du lieu tu gg drive

# CACH LAM MANUAL:
#B1: tai data tu gg drive
#B2: day cac file len VSCODE
#B3: Doc data tu file csv/xlsx bang pandas
#B4: Tao connection string den postgres
#B5: tao engine de truyen bien connection string vao
#B6: tosql de day du lieu vao postgres

# ham download dat ve tu gg drive vaf luu vao RAM, tra ve buffer = B1 + B2

# dinh nghia ham de dung service acc tu file json va lam nhiem vu trong scope, credentials = connection_string trong cac file load_ khac
# dinh nghia ham voi muc dich tai su dung cho cac file load khac, chi can goi lai ham ma khong can copy paste va sua lai 1 cach maual nua
def get_service_account(): 
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes = SCOPES
    )
# tao engine de ket noi voi gg drive
    service = build(     # truyen thong tin la chung ta dang can ket noi den dich vu nao cua gg, o day ta dung gg drive
        "drive",   # ket noi den gg drive
        "v3",     #version 3 cua gg drive
        credentials = credentials
    )

    return service


# dinh nghia ham de download data tu gg drive 
def download_data(service, file_id):
    request = service.files().get_media(
        fileId = file_id,
        supportsAllDrives = True
    )

    buffer = BytesIO() # tao 1 buffer (khoang trong) de luu tru du lieu tai RAM

    downloader = MediaIoBaseDownload(        # download data tu gg drive ve buffer
        buffer,
        request
    )

    done = False 

    while not done:
        status, done = downloader.next_chunk() # download data theo tung chunk (1 phan nho) de tranh loi do du lieu qua lon

    buffer.seek(0) # dua con tro ve dau buffer de doc du lieu tu dau

    return buffer

# ham doc file csv tu RAM bang pandas, tra ve datafram = B3, can su dung if de check xem file la csv hay excel de dung ham doc tuong ung
def read_file(file_name, buffer):
    if file_name.endswith(".csv"):  # ket thuc voi duoi gi, csv hay excel
        df = pd.read_csv(buffer)   # buffer la dia chi luu tru data trong RAM, pandas se doc du lieu tu buffer va tra ve dataframe

    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(
            buffer,
            engine = "openpyxl"
         ) #excel khac csv, phai truyen engine de doc du lieu tu excel, o day dung openpyxl de doc du lieu tu excel
            # engine nhu la 1 cầu nối

    else:
        raise ValueError("File format not supported. Only CVS and Excel files are allowed")   
        
    return df

# tao ham de ket noi den postgres , tra ve connection_string = B4 + B5
def create_connection_postgres():
    PG_USER = os.getenv("PG_USER")    # truy cap bien moi truong .env de lay du lieu da chon
    PG_PWD = os.getenv("PG_PWD")
    PG_DATABASE_NAME =  os.getenv("PG_DATABASE_NAME")
    PG_HOST = os.getenv("PG_HOST")
    PG_PORT = os.getenv("PG_PORT")

    PG_PWD = quote_plus(PG_PWD) # Do passửod trong postgres có chứa ký tự đặc biển là '@' nên cần dùng quote_plus để biến ký tự đó thành dạng an toàn để đưa vào URL

    connection_string = (
        f"postgresql+psycopg2://{PG_USER}:{PG_PWD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE_NAME}"
    ) #truyen cac bien o tren vao connection string de ket noi den postgre, phai dung f"..." de truyen bien vao chuoi
    # Vi f la ky tu dac bie de truyen bien vao chuoi, tuc la thay the gia tri goc cua bien vao chuoi de tao connection string va tranh lo thong tin
    # neu ko co f thi se bi loi vi python se hieu la chuoi binh thuong va ko thay the gia tri cua bien vao chuoi, ma se in ra gia tri goc cua bien
    
    engine = create_engine(connection_string) # tao engine de truyen bien connection string vao
    return engine


# day data vao postgres = B6
def load_to_postgres(df, table_name, schema = "bronze", if_exists = 'replace'):  #du lieu nao duoc dua vao postgres, ten gi, thuoc schema nao, ...
    engine = create_connection_postgres()       # engine là cầu nối giữa python và postgres
    df.to_sql(
        name = table_name,
        con = engine,
        schema = schema,
        if_exists = if_exists,
        index = False
    )

# Truoc khi load vao bronze, dam bao lap timestamp bieu dien du lieu upload vao luc nao
# data['recorded_at'] = pd.Timestamp.now()


service = get_service_account() # goi ham de lay service account
buffer = download_data(service, file_id = '1-BLii_-P0NQ4jlcG9ckbyfkZk54vo19s') # goi ham de download data tu gg drive ve buffer

# Dối với các file khác thì có thể viết như dưới dây:
# data = read_file('sales_target.xlsx', buffer) # goi ham de doc data tu buffer va truyen ra dataframe(df) de xu ly tiep, luc nay data = df
# sau do khi goi ham load_to_postgres thi python se hieu la lay dataframe da duoc truyen vao bang co ten "..." roi dua vao postgres

#Tạo Timestamp để record xem thông tin được tạo khi nào
# data['recorded_at'] = pd.Timestamp.now()

# print(data) 

# Nhưng riêng với file load_sales_target_plan thì phải làm cách khác vì file này có 2 version:

buffer.seek(0) # dua con tro ve dau buffer de doc du lieu tu dau

# Nếu viết read_file như trên thì python sẽ chỉ đọc 1 file sheet và trả về 1 Dataframe duy nhất, nhưng sales_target có 2 sheets nên cần trả về 2 data frame
sheets = pd.read_excel(
    buffer,
    sheet_name=None,
    engine="openpyxl"
)

# print(sheets.keys())       # bỏ vào # để python không chạy lần 2

# đọc xem định dạng file được viết như thế nào để sau đó chuyển sang dạng long
# print(sheets["Plan_v1_Original"].head())
# print("===== V1 =====")
# print(sheets["Plan_v1_Original"].columns.tolist())

#print("\n===== V2 =====")
#print(sheets["Plan_v2_Adjustment_H2"].head())
#print(sheets["Plan_v2_Adjustment_H2"].columns.tolist())

# Lấy 2 version
v1 = sheets["Plan_v1_Original"].copy()
v2 = sheets["Plan_v2_Adjustment_H2"].copy()

# Tạo bảng Metadata của các version
sales_target_files = pd.DataFrame([
    {
        "version_label": "v1",
        "sheet_name": "Plan_v1_Original"
    },
    {
        "version_label": "v2",
        "sheet_name": "Plan_v2_Adjustment_H2"
    }
])

# Tạo bảng để lưu toàn bộ thông tin của cả v1 và v2 và ghép chúng thành 1 dataframe mới
sales_targets_raw = pd.concat(
    [v1, v2],
    ignore_index=True
)

# Tạo month_col
sales_targets_raw["month_col"] = (
    "T" + sales_targets_raw["month"].astype(str)
)

# Timestamp
sales_targets_raw["recorded_at"] = pd.Timestamp.now()

sales_target_files["recorded_at"] = pd.Timestamp.now()

# Kiểm tra
#print("===== VERSION =====")
#print(sales_targets_raw["plan_version"].unique())

#print("\n===== MONTH =====")
#print(sorted(sales_targets_raw["month_col"].unique()))

#print("\n===== FILE METADATA =====")
#print(sales_target_files)

#print("\n===== RAW DATA =====")
#print(sales_targets_raw.head())

#print(sales_targets_raw["plan_version"].value_counts())
#print(sales_targets_raw["month_col"].unique())

#load bảng saes_target_files và raw vào postgres
load_to_postgres(
    sales_target_files,
    "sales_target_files",
    schema="bronze",
    if_exists="replace"
)

load_to_postgres(
    sales_targets_raw,
    "sales_targets_raw",
    schema="bronze",
    if_exists="replace"
)