import os, io, uuid
import zipfile
from flask import Blueprint, request, redirect, url_for, render_template, send_file, after_this_request
from werkzeug.utils import secure_filename
from pylatex import Document, Section

from google.cloud import vision
from google.cloud.vision import types

main = Blueprint('main', __name__)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.dirname(__file__) + '/VisionServiceAccountToken.json'
os.environ['UPLOAD_FOLDER'] = os.path.dirname(__file__) + '/uploads/'
ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg'}


def extract_text(file_path):
    client = vision.ImageAnnotatorClient()

    # open file
    with io.open(file_path, 'rb') as image_file:
        content = image_file.read()


    image = vision.types.Image(content=content)
    response = client.document_text_detection(image=image)
    annotation = response.full_text_annotation
    
    breaks = vision.enums.TextAnnotation.DetectedBreak.BreakType
    # text found in documents
    lines = []

    for page in annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                line = ""
                for word in paragraph.words:
                    for symbol in word.symbols:
                        line += symbol.text
                        if symbol.property.detected_break.type == breaks.SPACE:
                            line += ' '
                        if symbol.property.detected_break.type == breaks.EOL_SURE_SPACE:
                            line += ' '
                            lines.append(line)
                            line = ''
                        if symbol.property.detected_break.type == breaks.LINE_BREAK:
                            lines.append(line)
                            line = ''

    return lines

# limit upload size upto 8mb
# app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not request.files.get('file', None):
            print('No file attached in request')
            return redirect(request.url)

        # list for file paths and extracted text
        extractedtext = []
        files = request.files.getlist("file")
        for file in files:
            if allowed_file(file.filename):
                # save as temporary files for processing
                unique_filename = secure_filename(uuid.uuid4().urn[9:] + '.' + file.filename.rsplit('.', 1)[1].lower())
                filepath = os.path.join(os.environ['UPLOAD_FOLDER'], unique_filename)
                
                print('savedfilepath:' + filepath)
                file.save(filepath)

                # extract text from file
                # extractedtext.append(extract_text(filepath))

                print('gottext')
                
                # remove temporary file
                os.remove(filepath)

        # create latex document
        doc = Document('basic')
        with doc.create(Section('Extracted text')):
            for page in extractedtext:
                for index in range(0, len(page), 1):
                    doc.append(page[index] + '\n')
                doc.append('\n')

        # save temporary latex and pdf documents
        tempname = uuid.uuid4().urn[9:]
        temppath = os.path.join(os.environ['UPLOAD_FOLDER'], tempname)
        doc.generate_pdf(temppath, clean_tex=False)

        # create zip file
        with zipfile.ZipFile(temppath + '.zip','w', compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(temppath + '.pdf', "extracted_text.pdf")
            zipf.write(temppath + '.tex', "extracted_text.tex")

        # remove temporary files
        os.remove(temppath + '.pdf')
        os.remove(temppath + '.tex')

        @after_this_request
        def remove_file(response):
            os.remove(temppath + '.zip')
            return response

        return send_file(temppath + '.zip',
                mimetype = 'zip',
                attachment_filename= 'Extracted_Text.zip',
                as_attachment = True)

    return render_template('index.html')

