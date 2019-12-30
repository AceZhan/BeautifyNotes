from flask import Blueprint, request
from pylatex import Document, Section
import os

main = Blueprint('main', __name__)
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'

@main.route('/extract_text', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        doc = Document('basic')
        with doc.create(Section('A section')):
            doc.append('Some regular text and some ')

        doc.generate_tex(UPLOAD_FOLDER + 'newfile')
        return 'Found file', 201
    else:
        return 'No File', 404