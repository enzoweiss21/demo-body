from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_multiple_images():
    image_files = [file for key, file in request.files.items() if key.startswith('image')]
    if not image_files:
        return jsonify({'error': 'No images received'}), 400

    saved_paths = []
    for i, file in enumerate(image_files):
        filename = secure_filename(f"frame{i}.jpg")
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        saved_paths.append(path)

    # Run SPIN on the first image only for now
    try:
        subprocess.run([
            'python', 'SPIN/demo.py',
            '--img_path', saved_paths[0],
            '--output_folder', OUTPUT_FOLDER
        ], check=True)
    except subprocess.CalledProcessError:
        return jsonify({'error': 'SPIN failed'}), 500

    return jsonify({
        'status': 'success',
        'frames_saved': len(saved_paths),
        'mesh_path': f"output/{os.path.basename(saved_paths[0])}.obj"
    }), 200

@app.route('/output/<filename>')
def serve_mesh(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
