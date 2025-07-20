import React, { useState } from 'react';
import { Chart } from 'react-chartjs-2';
import { Chart as ChartJS, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale } from 'chart.js';

ChartJS.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale);

function App() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      // Отправка изображения на сервер
      const response = await fetch('http://localhost:8000/detect', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      setResult(data);
      setImage(URL.createObjectURL(file));
      
      // Загрузка статистики
      loadStats();
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/stats?days=30');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  return (
    <div className="container">
      <h1>Анализатор книжного шкафа</h1>
      
      <div className="upload-section">
        <h2>Загрузите фото книжного шкафа</h2>
        <input type="file" accept="image/*" onChange={handleImageUpload} />
      </div>
      
      {loading && <p>Обработка изображения...</p>}
      
      {result && (
        <div className="results">
          <h2>Результаты анализа</h2>
          <p>Обнаружено книг: <strong>{result.count}</strong></p>
          
          <div className="image-container">
            <h3>Обнаруженные книги:</h3>
            <img 
              src={`data:image/jpeg;base64,${result.image_with_boxes}`} 
              alt="Обнаруженные книги" 
              style={{ maxWidth: '100%' }}
            />
          </div>
        </div>
      )}
      
      {stats && (
        <div className="stats">
          <h2>Статистика за последние 30 дней</h2>
          <div style={{ height: '400px' }}>
            <Chart
              type="line"
              data={{
                labels: stats.timestamps,
                datasets: [{
                  label: 'Количество книг',
                  data: stats.counts,
                  borderColor: 'rgb(75, 192, 192)',
                  tension: 0.1
                }]
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  x: {
                    title: { display: true, text: 'Дата' }
                  },
                  y: {
                    title: { display: true, text: 'Количество книг' }
                  }
                }
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;