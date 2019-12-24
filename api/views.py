from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/process_image')
def process_image():

    return 'string'