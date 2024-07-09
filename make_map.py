import os
import shutil   # Thao tác với tệp và thư mục

import numpy as np
import cv2
from PIL import Image

from skimage.draw import ellipse

# Định nghĩa biến
data_path = "dataset"

# Tạo map cho các ảnh sản phẩm không bị lỗi
def make_map_normal(data_path):
    # Lặp qua các folder ảnh không bị lỗi
    for folder in os.listdir(data_path):
        if (not folder.endswith("def")) and (not folder.startswith(".")) and (not folder.endswith("mask")):
            print("*" * 10, folder)

            # Tạo thư mục mask
            mask_folder = folder + "_mask"
            mask_folder = os.path.join(data_path, mask_folder)

            # Kiểm tra nếu có file mask_folder rồi thì xóa, còn nếu không thì bỏ qua và tiếp tục thực thi code tiếp theo
            try:
                shutil.rmtree(mask_folder)
            except:
                pass

            os.mkdir(mask_folder)

            # Lặp qua các file trong thư mục Class4
            current_folder = os.path.join(data_path, folder)
            for file in os.listdir(current_folder):
                if file.endswith("png"):
                    print(file)
                    # Đọc file và lấy ra chiều cao, chiều rộng của ảnh
                    current_file = os.path.join(current_folder, file)
                    image = cv2.imread(current_file)
                    w, h = image.shape[0], image.shape[1]

                    # Tạo ra mask image cho ảnh sản phẩm không bị lỗi
                    mask_image = np.zeros((w, h), dtype=np.uint8)
                    mask_image = Image.fromarray(mask_image)

                    # Lưu lại
                    mask_image.save(os.path.join(mask_folder, file))

make_map_normal(data_path)

# Vẽ vùng lỗi lên trên ảnh map màu đen
def draw_defect(file, labels, w, h):
    # Lấy file id
    file_id = int(file.replace(".png", ""))

    # Lấy nhãn của file
    label = labels[file_id - 1]

    # Tách các thành phần trong nhãn
    label = label.replace("\t", "").replace("  ", " ").replace("  ", " ").replace("\n", "")
    label_array = label.split(" ")

    # Vẽ hình ellipse
    major, minor, angle, x_pos, y_pos = float(label_array[1]), float(label_array[2]), float(label_array[3]), float(
        label_array[4]), float(label_array[5])
    rr, cc = ellipse(y_pos, x_pos, r_radius=minor, c_radius=major, rotation=-angle)

    # Tạo ảnh màu đen
    mask_image = np.zeros((w, h), dtype=np.uint8)

    try:
        # Gán các điểm thuộc hình ellipse thành 1
        mask_image[rr, cc] = 1 # 255
    except:
        # Nếu lỗi chỉ gán các điểm trong ảnh
        rr_n = [min(511, rr[i]) for i in rr]
        cc_n = [min(511, cc[i]) for i in cc]
        mask_image[rr_n, cc_n] = 1 # 255
        # mask_image = Image.fromarray(mask_image)

    # Chuyển thành ảnh
    mask_image = np.array(mask_image, dtype=np.uint8)
    mask_image = Image.fromarray(mask_image)

    return mask_image

# Tạo map cho các ảnh sản phẩm bị lỗi
def make_map_defect(data_path):
    # Lặp qua từng folder trong thư mục Class4_def
    for folder in os.listdir(data_path):
        if (folder.endswith("def")) and (not folder.startswith(".")):
            print("*" * 10, folder)

            # Tạo folder mask
            mask_folder = folder + "_mask"
            mask_folder = os.path.join(data_path, mask_folder)
            try:
                shutil.rmtree(mask_folder)
            except:
                pass

            os.mkdir(mask_folder)

            # Lặp qua các file trong folder
            current_folder = os.path.join(data_path, folder)

            # Load file txt
            f = open(os.path.join(current_folder, 'labels.txt'))
            labels = f.readlines()
            f.close()

            for file in os.listdir(current_folder):
                if file.find("(") > -1:
                    # Xoá file nếu bị trùng (do đặc thù dữ liệu)
                    os.remove(os.path.join(current_folder, file))
                    continue

                if file.endswith("png"):
                    print(file)
                    # Read image file
                    current_file = os.path.join(current_folder, file)
                    image = cv2.imread(current_file)
                    w, h = image.shape[0], image.shape[1]

                    # Tạo ảnh mask cho ảnh sản phẩm bị lỗi (ảnh đen, bên trên là ảnh phần bị lỗi)
                    mask_image = draw_defect(file, labels, w, h)

                    # Save file
                    mask_image.save(os.path.join(mask_folder, file))

make_map_defect(data_path)