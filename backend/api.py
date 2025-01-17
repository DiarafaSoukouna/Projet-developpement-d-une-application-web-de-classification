from utilities import predict_file_label

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def welcome():
    return 'Welcome to our API,'


@app.route('/uploadFiles', methods=['POST'])
def uploadFiles():
    if 'files' not in request.files:
        return jsonify({'message': 'Not a file'})
    
    files = request.files.getlist('files')

    
    results = []
    for file in files:
        file_content = []

        for line in file.stream.readlines():
            file_content.append(line.decode("utf-8"))

        results.append({'filename': file.filename, 'label': predict_file_label(file_content)})
        
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)