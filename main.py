import os
import sys
from flask import Flask, redirect, render_template_string
from b2sdk.v2 import InMemoryAccountInfo
from b2sdk.v2 import B2Api

app = Flask(__name__)

application_key_id = os.getenv('READ_KEY_ID')
application_key = os.getenv('READ_KEY')

info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", application_key_id, application_key)

bucket = b2_api.get_bucket_by_name('nnue-data')

@app.route('/')
@app.route('/<path:path>')
def list_files(path=''):
    files_and_folders = bucket.ls(folder_to_list=path)
    result = '<div class="item"><span class="folder-open-icon"></span><a class="list-item" href="../">..</a><br/></div>'
    for (file_info, folder_name) in files_and_folders:
        if folder_name:  # Folder
            result += '<div class="item"><span class="folder-icon"></span><a class="list-item" href="' + folder_name + '">' + folder_name + '</a><br/></div>'
        else:  # File
            file_path = file_info.file_name
            file_name = os.path.basename(file_path)
            result += '<div class="item"><span class="file-icon"></span><a class="list-item" href="/download/' + file_path + '">' + file_name + '</a><br/></div>'
    return render_template_string(open("Template/BucketBrowser.html").read(), content=result)

@app.route('/download/<path:path>')
def download_file(path):
    url = "https://nova.shaheryarsohail.com/" + path
    return redirect(url)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python main.py <ip:port>")
        sys.exit(1)

    ip, port = sys.argv[1].split(':')
    app.run(host=ip, port=int(port))