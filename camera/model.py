import tensorflow as tf
from tensorflow.keras.preprocessing import image_dataset_from_directory
import matplotlib.pyplot as plt
from tensorflow.keras import layers, models
from sklearn.metrics import classification_report
import numpy as np


# 데이터 경로
train_dir = "dataset/train"
val_dir = "dataset/validation"
test_dir = "dataset/test"

# 데이터 로드
batch_size = 32
img_size = (224, 224)  # 입력 이미지 크기

train_dataset = image_dataset_from_directory(
    train_dir,
    image_size=img_size,
    batch_size=batch_size
)

class_names = train_dataset.class_names

val_dataset = image_dataset_from_directory(
    val_dir,
    image_size=img_size,
    batch_size=batch_size
)


# 테스트 데이터 로드
test_dataset = image_dataset_from_directory(
    test_dir,
    image_size=img_size,
    batch_size=batch_size
)

# 데이터 증강
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomBrightness(0.2),  # 밝기를 20% 범위에서 무작위 변경
    tf.keras.layers.RandomContrast(0.2),    # 대비도를 20% 범위에서 무작위 변경
    tf.keras.layers.RandomFlip("horizontal")  # 수평 대칭
])

# 전처리 및 데이터 증강 적용
AUTOTUNE = tf.data.AUTOTUNE
train_dataset = (
    train_dataset
    .map(lambda x, y: (data_augmentation(x), y), num_parallel_calls=AUTOTUNE)
    .cache()
    .shuffle(1000)
    .prefetch(buffer_size=AUTOTUNE)
)
val_dataset = val_dataset.cache().prefetch(buffer_size=AUTOTUNE)
test_dataset = test_dataset.cache().prefetch(buffer_size=AUTOTUNE)

# MobileNetV2 기반 모델 구성
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)

base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(
        len(class_names),
        activation='softmax',
    )
])

# 학습률 설정 및 모델 컴파일
initial_learning_rate = 0.001  # 초기 학습률
optimizer = tf.keras.optimizers.Adam(learning_rate=initial_learning_rate)
model.compile(
    optimizer=optimizer,
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

lr_scheduler = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.2,
    patience=3,
    min_lr=1e-6
)

# 모델 학습
epochs = 35
history = model.fit(
    train_dataset,
    validation_data=val_dataset,
    epochs=epochs,
    callbacks=[early_stopping, lr_scheduler]
)


# 모델 평가
test_loss, test_accuracy = model.evaluate(test_dataset)
print(f"테스트 정확도: {test_accuracy:.2f}")

y_true = np.concatenate([y for _, y in test_dataset], axis=0)
y_pred_probs = model.predict(test_dataset)
y_pred = np.argmax(y_pred_probs, axis=1)

print("\n클래스별 성능 보고서:")
print(classification_report(y_true, y_pred, target_names=class_names))

# 모델 저장
model.save('saved_model/my_model')

# TFLite 변환
converter = tf.lite.TFLiteConverter.from_saved_model('saved_model/my_model')
tflite_model = converter.convert()

# TFLite 모델 저장
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)

# Accuracy와 Loss 시각화
plt.figure(figsize=(12, 6))

# Accuracy 그래프
plt.subplot(1, 2, 1)  # 1행 2열의 첫 번째 서브플롯
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

# Loss 그래프
plt.subplot(1, 2, 2)  # 1행 2열의 두 번째 서브플롯
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

# 그래프 저장
plt.tight_layout()
plt.savefig('./accloss.png')
print("저장되었습니다")
