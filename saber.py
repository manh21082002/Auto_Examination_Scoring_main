import cv2
import numpy as np
# from google.colab.patches import cv2_imshow

def getContours(img,cThread=[100,100],minArea=1000, filter=4):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv2.Canny(imgBlur,cThread[0],cThread[1])
    kernel = np.ones((5,5))
    imgDilation = cv2.dilate(imgCanny, kernel, iterations = 3)
    imgThre = cv2.erode(imgDilation, kernel, iterations = 2)

    contours, _ = cv2.findContours(imgThre, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    final_countours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > minArea:
            peri = cv2.arcLength(contour,True)
            approx = cv2.approxPolyDP(contour,0.02*peri,True)
            bbox = cv2.boundingRect(approx)
            if filter > 0:
                if len(approx) == filter:
                    final_countours.append([len(approx),area,approx,bbox,contour])
            else:
                final_countours.append([len(approx),area,approx,bbox,contour])
    final_countours = sorted(final_countours, key = lambda x:x[1], reverse=True)

    return img, final_countours

def reorder(myPoints):
	myPointsNew = np.zeros_like(myPoints)
	myPoints = myPoints.reshape((4,2))

	add = myPoints.sum()
	diff = np.diff(myPoints,axis =1)

	myPointsNew[0] = myPoints[np.argmin(add)]
	myPointsNew[3] = myPoints[np.argmax(add)]
	
	myPointsNew[1] = myPoints[np.argmin(diff)]
	myPointsNew[2] = myPoints[np.argmax(diff)]

	return myPointsNew

def wrapImage(img, points, widthImg, heightImg, pad = 0):
    points= get_4_contour(points)
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0],[widthImg, 0], [0, heightImg],[widthImg, heightImg]]) # PREPARE POINTS FOR WARP
    
    matrix = cv2.getPerspectiveTransform(pts1, pts2) 
    wrap = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
    wrap = wrap[pad:wrap.shape[0]-pad,pad:wrap.shape[1]-pad]
    return wrap

def get_4_contour(points):
    center = np.mean(points, axis=0).astype(int)

    points_above_center = np.array([point.squeeze() for point in points if point.squeeze()[1] < center[0][1]])
    points_below_center = np.array([point.squeeze() for point in points if point.squeeze()[1] >= center[0][1]])

    top_left = points_above_center[np.argmin(points_above_center[:, 0])]
    top_right = points_above_center[np.argmax(points_above_center[:, 0])]
    botton_left = points_below_center[np.argmin(points_below_center[:, 0])]
    botton_right = points_below_center[np.argmax(points_below_center[:, 0])]
    return np.array([[top_left], [top_right], [botton_left],[botton_right]])

#cắt vùng phiếu
def findFullAnswerSheet(pathImage, width =1830, height =2560):
    img = cv2.imread(pathImage)
    _, countours = getContours(img,minArea=300000)
    points_test_paper = get_4_contour(countours[0][2])
    return wrapImage(img, points_test_paper, width, height)

def get_test_code_image(image):
    height, width, channels = image.shape
    per_width = [0.876, 0.94]
    per_height = (0.0975, 0.298)
    return image[int(per_height[0]*height):int(per_height[1]*height),\
                 int(per_width[0]*width):int(per_width[1]*width)]

def get_student_code_image(image):
    height, width, channels = image.shape
    per_width = (0.727, 0.845)
    per_height = (0.0975, 0.298)
    return image[int(per_height[0]*height):int(per_height[1]*height),\
                 int(per_width[0]*width):int(per_width[1]*width)]

def get_sheet_ans_image(image):
    height, width, channels = image.shape
    per_height = (0.326, 0.945)
    per_width = (0.055, 0.925)
    full_sheet = image[int(per_height[0]*height):int(per_height[1]*height),\
                 int(per_width[0]*width):int(per_width[1]*width)]
    return full_sheet

def get_part_sheet_ans_image(image,dis=10):
    height, width, channels = image.shape
    dis = 0.03562 * width
    A, B = image[:,:int(round((width+dis)/2 - dis,0))], image[:,int(round((width+dis)/2,0)):]
    A1,A2 = A[:,:int(round((A.shape[1]+dis)/2 - dis,0))], A[:,int(round((A.shape[1]+dis)/2,0)):]
    B1,B2 = B[:,:int(round((B.shape[1]+dis)/2 - dis,0))], B[:,int(round((B.shape[1]+dis)/2,0)):]
    return [A1,A2,B1,B2]

def get_student_code(img_sbd, thresh_value = 150):
    # Xử lý ảnh
    gray = cv2.cvtColor(img_sbd, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Xoá viền
    kernel = np.ones((5,5))
    imgDilation = cv2.dilate(blur, kernel, iterations = 2)
    # Phóng to phần tô màu
    erosion = cv2.erode(imgDilation, kernel, iterations = 2)
    # Chuyển thành giá trị nhị phân, giá trị nào dưới 100 về 0, ngược lại 255 (đen và trắng)
    _, thresh = cv2.threshold(erosion, thresh_value, 255, cv2.THRESH_BINARY)

    # cv2_imshow(thresh)
    column_width = img_sbd.shape[1] // 6
    bubble_positions = [int(i*(img_sbd.shape[0]//10)) for i in range(11)]

    student_ID = ""
    for i in range(6): # Có 6 cột số báo danh
        column = thresh[:,i*column_width:(i+1)*column_width]
        selected_number = None
        min_mean = float('inf')

        for pos in range (10): # Có 10 dòng từ 0-9
            start, end = bubble_positions[pos], bubble_positions[pos+1]
            mean_value = np.mean(column[start:end, :])
            # Tìm giá trị trung bình nhỏ nhất
            # Nhỏ nhất là chứa nhiều phần tử màu đen nhất, tức chọn ô này
            if mean_value < min_mean:
                min_mean = mean_value
                selected_number = pos
        student_ID += str(selected_number)
    return student_ID

def get_test_code(img, thresh_value = 150):
    # Xử lý ảnh
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Xoá viền
    kernel = np.ones((5,5))
    imgDilation = cv2.dilate(blur, kernel, iterations = 2)
    # Phóng to phần tô màu
    erosion = cv2.erode(imgDilation, kernel, iterations = 2)
    # Chuyển thành giá trị nhị phân, giá trị nào dưới 100 về 0, ngược lại 255 (đen và trắng)
    _, thresh = cv2.threshold(erosion, thresh_value, 255, cv2.THRESH_BINARY)
    # cv2_imshow(thresh)
    column_width = img.shape[1] // 3
    bubble_positions = [int(i*(img.shape[0]//10)) for i in range(11)]

    test_ID = ""
    for i in range(3): # Có 6 cột số báo danh
        column = thresh[:,i*column_width:(i+1)*column_width]
        selected_number = None
        min_mean = float('inf')

        for pos in range (10): # Có 10 dòng từ 0-9
            start, end = bubble_positions[pos], bubble_positions[pos+1]
            mean_value = np.mean(column[start:end, :])
            # Tìm giá trị trung bình nhỏ nhất
            # Nhỏ nhất là chứa nhiều phần tử màu đen nhất, tức chọn ô này
            if mean_value < min_mean:
                min_mean = mean_value
                selected_number = pos
        test_ID += str(selected_number)
    return test_ID

def get_my_ans(image_ans, ANSWER_KEY, thresh_value = 150, limit_value = 240, start_ = 55):
    translate = {"A": 0, "B": 1, "C": 2, "D": 3}
    revert_translate = {0: "A", 1: "B", 2: "C", 3: "D", -1: "N"}
    img = image_ans[:,start_:]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Xoá viền
    kernel = np.ones((5,5))
    imgDilation = cv2.dilate(blur, kernel, iterations = 2)
    # Phóng to phần tô màu
    erosion = cv2.erode(imgDilation, kernel, iterations = 2)
    # Chuyển thành giá trị nhị phân, giá trị nào dưới 100 về 0, ngược lại 255 (đen và trắng)
    _, thresh = cv2.threshold(erosion, thresh_value, 255, cv2.THRESH_BINARY)

    # plt.imshow(img_cnts)

    ans_char = ['A','B','C','D']
    height_sub = img.shape[0] // 6
    n_part, n_questions = 6,5
    pad = 5
    my_answers = []

    for i_part in range(n_part):
        sub_img = thresh[height_sub*i_part+pad*3:height_sub*(i_part+1)-pad*2,pad:-pad]

        bubble_positions = [int(idx*(sub_img.shape[0]//n_questions)) for idx in range(n_questions+1)]
        for j in range(n_questions):
            start, end = bubble_positions[j], bubble_positions[j+1]
            row_1_question = sub_img[start:end,:]

            min_mean = float('inf')
            selected_ans = None
            width_sub = row_1_question.shape[1] // 4
            for i_ans in range(4):
                mean_value = np.mean(row_1_question[:,i_ans*width_sub:(i_ans+1)*width_sub])
                # print(mean_value)
                # Nếu không chọn đáp án, sẽ có limit_value chặn
                if mean_value < limit_value and mean_value < min_mean:
                    min_mean = mean_value
                    selected_ans = ans_char[i_ans]
            if selected_ans is not None:
                my_answers.append(selected_ans)
            else:
                my_answers.append("-")
    r = 15
    for part in range(n_part):
        start_h, start_w = height_sub * part + 45, 35 + start_
        try:
            for quest in range(n_questions):
                idx = part*n_questions+quest
                s_w = start_w + 74* translate[ANSWER_KEY[idx]]
                if my_answers[idx] == ANSWER_KEY[idx]:
                    cv2.circle(image_ans, (s_w, start_h), r, (0, 255, 0), 3)
                else: 
                    w_wrong_ans = start_w + 74 * translate[my_answers[idx]]
                    cv2.circle(image_ans, (w_wrong_ans, start_h), r, (0, 0, 255), 3)
                    cv2.circle(image_ans, (s_w, start_h), r, (255, 0, 0), 3)
                start_h += 45
        except:
            break
        
    return my_answers