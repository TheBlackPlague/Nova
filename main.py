import os
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
    authorization = bucket.get_download_authorization(file_name_prefix=path, valid_duration_in_seconds=60 * 60)
    download_url = b2_api.get_download_url_for_file_name(bucket.name, path)
    authorized_url = f"{download_url}?Authorization={authorization}"
    return redirect(authorized_url)

if __name__ == '__main__':
    app.run(port=8000)
