import cv2
import numpy as np
from ultralytics import YOLO
from typing import Dict, Any, List
import base64
import os
from pathlib import Path

class BookDetector:
    def __init__(self, model_path: str = 'backend/models/yolov8n.pt'):
        """
        Инициализация детектора книг с проверкой модели
        Args:
            model_path: Путь к файлу модели YOLO
        """
        # Проверка существования модели
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Файл модели не найден: {model_path}")
        
        try:
            self.model = YOLO(model_path)
            self.class_name = "book"  # Используем фиксированное имя класса
            print(f"Модель успешно загружена из {model_path}")
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки модели: {str(e)}")

    def detect_books(self, image_path: str) -> Dict[str, Any]:
        """
        Детектирует книги на изображении с обработкой ошибок
        Args:
            image_path: Путь к изображению для анализа
        Returns:
            Словарь с результатами: {
                "count": количество книг,
                "boxes": [[x1,y1,x2,y2], ...],
                "image_with_boxes": base64 изображения с рамками
            }
        """
        # Проверка существования изображения
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Изображение не найдено: {image_path}")

        try:
            # Чтение изображения
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Не удалось загрузить изображение (возможно повреждение файла)")

            # Детекция объектов
            results = self.model(img)
            boxes = []

            # Обработка результатов детекции
            for result in results:
                for box in result.boxes:
                    # Получаем координаты рамки
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    boxes.append([x1, y1, x2, y2])
                    
                    # Рисуем рамку и подпись
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        img, 
                        self.class_name, 
                        (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.9, 
                        (0, 255, 0), 
                        2
                    )

            # Конвертация в base64
            success, buffer = cv2.imencode('.jpg', img)
            if not success:
                raise RuntimeError("Ошибка конвертации изображения в JPG")
            
            return {
                "count": len(boxes),
                "boxes": boxes,
                "image_with_boxes": base64.b64encode(buffer).decode('utf-8')
            }

        except Exception as e:
            raise RuntimeError(f"Ошибка детекции: {str(e)}")


if __name__ == "__main__":
    try:
        # Тестирование детектора
        detector = BookDetector()
        
        # Путь к тестовому изображению (можно заменить на свое)
        test_img = "test_bookshelf.jpg"
        if not os.path.exists(test_img):
            test_img = input("Введите путь к тестовому изображению: ")
        
        # Выполнение детекции
        result = detector.detect_books(test_img)
        
        # Вывод результатов
        print("\nРезультаты детекции:")
        print(f"Найдено книг: {result['count']}")
        if result['count'] > 0:
            print(f"Координаты первой книги: {result['boxes'][0]}")
            print(f"Размер изображения с рамками: {len(result['image_with_boxes'])} символов (base64)")
        
        # Сохранение результатов в файл
        with open("detection_result.txt", "w") as f:
            f.write(f"Count: {result['count']}\n")
            if result['count'] > 0:
                f.write(f"First box coordinates: {result['boxes'][0]}\n")
            f.write(f"Image size: {len(result['image_with_boxes'])} chars\n")
        
        print("Результаты сохранены в detection_result.txt")

    except Exception as e:
        print(f"\nОшибка: {str(e)}")
        if 'test_bookshelf.jpg' not in os.listdir():
            print("Для теста поместите изображение 'test_bookshelf.jpg' в папку с скриптом")