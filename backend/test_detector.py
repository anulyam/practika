import os
from pathlib import Path
from book_detection import BookDetector

def main():
    try:
        # Инициализация детектора
        detector = BookDetector()
        
        # Пути к тестовым данным
        current_dir = Path(__file__).parent
        test_img = current_dir / "test_bookshelf.jpg"
        
        # Проверка наличия тестового изображения
        if not test_img.exists():
            available_images = [f for f in os.listdir(current_dir) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if not available_images:
                raise FileNotFoundError("Нет изображений в формате JPG/PNG в папке backend")
            
            test_img = current_dir / available_images[0]
            print(f"Используется изображение: {test_img.name}")

        # Выполнение детекции
        print("\nЗапуск детекции...")
        result = detector.detect_books(str(test_img))
        
        # Вывод результатов
        print("\nРезультаты детекции:")
        print(f"Найдено книг: {result['count']}")
        
        if result['count'] > 0:
            print(f"Координаты первой книги: {result['boxes'][0]}")
            print(f"Размер изображения с рамками: {len(result['image_with_boxes'])} символов (base64)")
        else:
            print("Книги не обнаружены")

        # Сохранение результатов
        result_file = current_dir / "detection_result.txt"
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(f"Count: {result['count']}\n")
            if result['count'] > 0:
                f.write(f"First box coordinates: {result['boxes'][0]}\n")
            f.write(f"Image size: {len(result['image_with_boxes'])} chars\n")
        
        print(f"\nРезультаты сохранены в: {result_file}")
        return 0

    except Exception as e:
        print(f"\n❌ Ошибка: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code == 0:
        print("\nТест завершен успешно! ✅")
    else:
        print("\nТест завершен с ошибками ❗")