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
def read_file(file_name, buffer, sheet_name=0):
    if file_name.endswith(".csv"):  # ket thuc voi duoi gi, csv hay excel
        df = pd.read_csv(buffer)   # buffer la dia chi luu tru data trong RAM, pandas se doc du lieu tu buffer va tra ve dataframe

    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(
            buffer,
            sheet_name=sheet_name,
            engine = "openpyxl"
         ) #excel khac csv, phai truyen engine de doc du lieu tu excel, o day dung openpyxl de doc du lieu tu excel
            # engine nhu la 1 cầu nối
            # sheet name = none là đọc tất cả các sheets trong file
            # chỉ cần dùng sheet name = sheet name khi trong file có nhièu sheets và muốn chỉ đích danh trang sheet muốn đọc
            # còn với file chỉ có 1 trang sheet thì không cần để sheet name vì python sẽ tự mặc định đọc trang đầu tiên

    else:
        raise ValueError("File format not supported. Only CVS and Excel files are allowed")   
        
    return df