# High-School-Examination-Scoring
- Xin chào rất vui khi nhận được sự quan tâm của bạn!!

Đây là Mô hình tự động chấm điểm thi THPTQG của chung tôi

- **Kiến trúc dữ liệu**
```bash
High-School-Examination-Scoring/
│
├── demo/                       # Demo folder for running the application
│   ├── static/                 # Static files such as JS and CSS
│   │   ├── app.js              # JavaScript file for handling image upload and result display
│   │   └── style.css           # CSS file for styling the front-end interface
│   │
│   ├── templates/              # Template files for rendering HTML pages
│   │   └── index.html          # Main HTML file for the web interface
│   │
│   ├── uploads/                # Folder for storing uploaded and processed images
│   │   └── (uploaded files)    # This folder will contain uploaded and processed images dynamically
│   │
│   └── app.py                  # Flask application to process images and display results
│
├── image/                      # Folder for storing reference images used for testing
│   └── (image files)           # Sample images used in the scoring process
│
├── saber.py                    # Python file containing the core functions for image processing and scoring
│
├── README.md                   # Readme file that explains how to set up and use the project
│
├── requirements.txt            # Python dependencies required for the project
```

- **Cách chạy chương trình**
```bash
git clone https://github.com/manh21082002/High-School-Examination-Scoring.git
cd High-School-Examination-Scoring
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd demo
python app.py
```

- Giao diện người dùng

  ![image](https://github.com/user-attachments/assets/ef6d9f5a-11c6-4fec-a349-2ef12420c937)

