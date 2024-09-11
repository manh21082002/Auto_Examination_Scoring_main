from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import numpy as np
import sys
import os
import cv2
import matplotlib.pyplot as plt
sys.path.append('D:/Chấm điểm tự động THPTQG')
import saber as sb

# Lưu ảnh chấm điểm
def save_score_image(lst_sheet_ans,student_ID):
    plt.figure(figsize=(15, 15))
    for i in range(4):
        plt.subplot(1, 4, i + 1), plt.imshow(lst_sheet_ans[i])
    score_image_path = f'./uploads/{student_ID}_score_image.png'
    plt.savefig(score_image_path)
    plt.close()  # Đóng figure để giải phóng bộ nhớ
    return score_image_path

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Ensure the 'uploads' folder exists
if not os.path.exists('./uploads'):
    os.makedirs('./uploads')

# Lưu trữ đáp án đúng
ANS_KEY = ['A', 'B', 'C', 'D'] * 30  # Bạn có thể điều chỉnh đáp án này theo đề thi

# Function to process image using Saber
def findFullAnswerSheet(pathImage, width=1830, height=2560):
    img = cv2.imread(pathImage)
    _, contours = sb.getContours(img, minArea=300000)
    points_test_paper = sb.get_4_contour(contours[0][2])
    return sb.wrapImage(img, points_test_paper, width, height)

# Home route to render the HTML form
@app.route('/')
def index():
    return render_template('index.html')

# Route to serve images from uploads folder
@app.route('/uploads/<filename>')
def send_image(filename):
    return send_from_directory('./uploads', filename)

# Route to handle image upload and processing
@app.route('/process_image', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filepath = os.path.join('./uploads', file.filename)
        file.save(filepath)

        try:
            # Process the image using Saber functions
            image = findFullAnswerSheet(filepath)

            # Resize image to standard size
            width, height = 1830, 2560
            # width, height = 1830, 2560
            image = cv2.resize(image, (width, height))

            # Lưu ảnh đã qua xử lý
            processed_image_path = filepath.replace(".jpg", "_processed.jpg")
            cv2.imwrite(processed_image_path, image)

            # Vùng ảnh số báo danh
            anh_sbd = sb.get_student_code_image(image)

            # Vùng ảnh mã đề thi
            anh_mdt = sb.get_test_code_image(image)

            # Nhận diện số báo danh và mã đề
            student_ID = sb.get_student_code(anh_sbd)
            test_ID = sb.get_test_code(anh_mdt)

            # Nhận diện đáp án
            lst_sheet_ans = sb.get_part_sheet_ans_image(sb.get_sheet_ans_image(image))
            all_answer_key = []
            NUM_QUESTIONS = 120
            
            for i in range(4):
                my_ans = sb.get_my_ans(lst_sheet_ans[i], ANS_KEY[i * 30: i * 30 + 30])
                for ans in my_ans:
                    all_answer_key.append(ans)

            all_answer_key = np.array(all_answer_key)

            # Chấm điểm
            score = sum(all_answer_key[:NUM_QUESTIONS] == ANS_KEY[:NUM_QUESTIONS]) / NUM_QUESTIONS * 10

            # Lưu ảnh chấm điểm (sử dụng matplotlib để tạo hình)
            score_image_path = save_score_image(lst_sheet_ans,student_ID)

            # Trả về kết quả và đường dẫn ảnh
            return jsonify({
                "student_id": student_ID,
                "test_id": test_ID,
                "score": score,
                "original_image": file.filename,
                "processed_image": os.path.basename(processed_image_path),
                "score_image": os.path.basename(score_image_path)  # Trả về đường dẫn ảnh chấm điểm
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
