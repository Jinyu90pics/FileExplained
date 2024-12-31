import os
import markitdown
from flask import Flask, request, render_template, jsonify
from googleapiclient.discovery import build
from google.auth.oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth import exceptions
import pickle

app = Flask(__name__)

# Google Sheets API设置
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = os.getenv('SHEET_ID', 'your-google-sheet-id')  # Google Sheet ID
CREDENTIALS_PATH = 'credentials.json'

# OAuth2认证
def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Google Sheets API 交互
def append_to_sheet(markdown_text):
    try:
        creds = get_credentials()
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        request = sheet.values().append(spreadsheetId=SHEET_ID, range="Sheet1!A1", 
                                        valueInputOption="RAW", body={"values": [[markdown_text]]})
        request.execute()
    except exceptions.GoogleAuthError as e:
        print(f"Error with Google Sheets API: {e}")

# 首页和文件上传页面
@app.route('/')
def index():
    return render_template('index.html')

# 处理文件上传
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        # 将文件内容读取为字符串
        file_content = file.read().decode('utf-8')
        
        # 使用 markitdown 库将 HTML 转换为 Markdown
        try:
            markdown_content = markitdown.markup(file_content)
        except Exception as e:
            return jsonify({"error": f"Conversion failed: {str(e)}"}), 500
        
        # 将转换后的内容写入 Google Sheets
        append_to_sheet(markdown_content)
        
        # 返回转换后的 Markdown 内容
        return jsonify({"markdown": markdown_content})

if __name__ == '__main__':
    app.run(debug=True)
