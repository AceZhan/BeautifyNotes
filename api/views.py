import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from pylatex import Document, Section

main = Blueprint('main', __name__)
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'

@main.route('/', methods=['GET', 'POST'])
def process_image():

    return render_template("index.html", token="Hello guys")
    # if 'file' not in request.files:
    #     doc = Document('basic')
    #     with doc.create(Section('A section')):
    #         doc.append('Some regular text and some ')

    #     doc.generate_pdf(UPLOAD_FOLDER + 'newfile', clean_tex=False)
    #     return 'Found file', 201
    # else:
    #     return 'No File', 404


# @main.route('/download_file')
# def download_file():
#     return send_from_directory(UPLOAD_FOLDER, 'newfile.pdf', as_attachment=True)