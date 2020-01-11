import os, io, uuid
import zipfile
from flask import Flask, request, redirect, url_for, render_template, send_file, after_this_request
from pylatex import Document, Section

from google.cloud import vision
from google.cloud.vision import types

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'ServiceAccountToken.json'

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

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
IMAGE_NAME = 'blackboard.jpg'
FILE_PATH = os.path.join(UPLOAD_FOLDER, IMAGE_NAME)
ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg'}

app = Flask(__name__)
# DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 8mb
# app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not request.files.get('file', None):
            print('No file attached in request')
            return redirect(request.url)

        # list for file paths and extracted text
        extractedtext = []
        # extractedtext = [['- ?) Cate Reachability (CR)', 'Giveni Program P input I NEN, ', 'Question: Does Pon I reach code ', 'at line n?', 'Show C. R. is undecidable. ', '13) On=2i tb nosbel inod', 'if (b==0){ ', '- m=4*i*i; ', 'Selse', '(= 2*i;', 'm=(i+1)=(i ', 'Im=hand']]
        files = request.files.getlist("file")
        for file in files:
            if allowed_file(file.filename):
                # save as temporary files for processing
                unique_filename = uuid.uuid4().urn[9:] + '.' + file.filename.rsplit('.', 1)[1].lower()
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)

                # extract text from file
                extractedtext.append(extract_text(filepath))
                
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
        temppath = os.path.join(app.config['UPLOAD_FOLDER'], tempname)
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


if __name__ == '__main__':
    app.run(debug=True)