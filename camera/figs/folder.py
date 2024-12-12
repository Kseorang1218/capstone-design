import os
import shutil
from sklearn.model_selection import train_test_split

# 원본 데이터 디렉토리
original_dir = "./cropped/augmented"  # 파일이 저장된 폴더 이름
output_dir = "./dataset"  # 정리된 데이터셋 폴더 이름

# 정리할 클래스 이름
classes = ["boots", "shoes", "slipper", "sneakers"]

# 데이터셋 비율 설정
train_ratio = 0.7
val_ratio = 0.2
test_ratio = 0.1

# 출력 디렉토리 생성
for split in ["train", "validation", "test"]:
    for cls in classes:
        os.makedirs(os.path.join(output_dir, split, cls), exist_ok=True)

# 클래스별로 파일 분리
for cls in classes:
    class_files = [f for f in os.listdir(original_dir) if f.startswith(cls)]
    train_files, temp_files = train_test_split(class_files, test_size=(val_ratio + test_ratio), random_state=42)
    val_files, test_files = train_test_split(temp_files, test_size=test_ratio / (val_ratio + test_ratio), random_state=42)

    # 파일 이동
    for split, files in zip(["train", "validation", "test"], [train_files, val_files, test_files]):
        for file in files:
            src_path = os.path.join(original_dir, file)
            dest_path = os.path.join(output_dir, split, cls, file)
            shutil.move(src_path, dest_path)

print("데이터 정리가 완료되었습니다!")
