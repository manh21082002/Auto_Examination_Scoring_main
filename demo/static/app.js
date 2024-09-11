document.getElementById('uploadForm').addEventListener('submit', function (event) {
    event.preventDefault(); // Ngăn form tự động submit

    var formData = new FormData();
    formData.append('file', document.getElementById('fileInput').files[0]);

    // Gửi yêu cầu POST để upload ảnh
    fetch('/process_image', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        // Kiểm tra nếu có lỗi
        if (data.error) {
            document.getElementById('result').innerText = "Error: " + data.error;
        } else {
            // Hiển thị kết quả nếu thành công
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = `
                <h2>Kết quả chấm thi</h2>
                <p><strong>Mã sinh viên:</strong> ${data.student_id}</p>
                <p><strong>Mã đề thi:</strong> ${data.test_id}</p>
                <p><strong>Điểm:</strong> ${data.score}</p>
            `;

            // Hiển thị ảnh gốc và ảnh đã xử lý
            const originalImage = document.getElementById('originalImage');
            const processedImage = document.getElementById('processedImage');
            
            // Cập nhật đường dẫn của ảnh
            originalImage.src = `/uploads/${data.original_image}`;
            processedImage.src = `/uploads/${data.processed_image}`;

            // Hiển thị hình ảnh
            originalImage.style.display = 'block';
            processedImage.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').innerText = "An error occurred.";
    });
});
