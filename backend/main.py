from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from book_detection import BookDetector
from pathlib import Path
import sqlite3
from datetime import datetime
import os
import uvicorn
import logging

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BookShelfAPI")

# Инициализация приложения
app = FastAPI(title="BookShelf Analyzer API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Конфигурация
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
DB_FILE = "bookshelf.db"
MODEL_PATH = "backend/models/yolov8n.pt"

# Инициализация компонентов
try:
    detector = BookDetector(model_path=MODEL_PATH)
    logger.info("Модель детектора успешно загружена")
except Exception as e:
    logger.error(f"Ошибка загрузки модели: {str(e)}")
    raise RuntimeError("Не удалось инициализировать детектор книг")

# Инициализация БД
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS bookshelf_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            book_count INTEGER,
            image_path TEXT
        )
        ''')
        conn.commit()

init_db()

@app.post("/detect", response_model=dict)
async def detect_books(file: UploadFile = File(...)):
    """Эндпоинт для детекции книг на изображении"""
    try:
        # Сохраняем загруженный файл
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Обрабатываем изображение
        result = detector.detect_books(file_path)
        
        # Сохраняем в БД
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "INSERT INTO bookshelf_stats (timestamp, book_count, image_path) VALUES (?, ?, ?)",
                (datetime.now(), result['count'], file_path)
            )
            conn.commit()
        
        return JSONResponse({
            "status": "success",
            "count": result["count"],
            "boxes": result["boxes"],
            "image_with_boxes": result["image_with_boxes"]
        })
        
    except Exception as e:
        logger.error(f"Ошибка детекции: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": str(e)
            }
        )

@app.get("/stats")
async def get_stats(days: int = 7):
    """Получение статистики за указанное количество дней"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT timestamp, book_count FROM bookshelf_stats "
                "WHERE timestamp >= datetime('now', ?) "
                "ORDER BY timestamp", (f'-{days} days',)
            )
            rows = cursor.fetchall()
            
        return {
            "status": "success",
            "timestamps": [row[0] for row in rows],
            "counts": [row[1] for row in rows]
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {"status": "ok", "message": "Service is running"}

# Монтирование статики фронтенда
frontend_path = Path(__file__).parent.parent / "frontend" / "build"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True))
    logger.info(f"Фронтенд монтирован из {frontend_path}")
else:
    logger.warning("Фронтенд не найден, API работает без интерфейса")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)