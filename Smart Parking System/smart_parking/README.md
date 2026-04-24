# Smart Parking System 🚗

A real-time parking detection system built with Python, OpenCV, and Flask. This system detects empty vs occupied parking slots from video footage and displays results on a modern web dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-orange.svg)

## ✨ Features

- **Real-time Detection**: Process video frames and detect parking slot occupancy
- **Visual Feedback**: Green (empty) and Red (occupied) rectangles on video
- **Live Dashboard**: Modern web interface with live statistics
- **Alert System**: Shows "Parking Available" or "Parking Full" status
- **CSV Logging**: Records parking data with timestamps
- **Webcam/Video Support**: Works with webcam or video file input

## 📁 Project Structure

```
smart_parking/
├── app.py                 # Flask web server
├── parking_detector.py    # Core detection logic
├── utils.py               # Utility functions
├── slots.pkl              # Parking slot coordinates
├── requirements.txt       # Python dependencies
├── create_slots.py        # Script to generate slots.pkl
│
├── static/
│   ├── styles.css         # Modern UI styles
│   └── script.js          # Frontend JavaScript
│
└── templates/
    └── index.html         # Dashboard HTML
```

## 🛠️ Installation

### 1. Prerequisites

- Python 3.10 or higher
- Webcam (optional, for live detection)
- Video file (optional, for recorded detection)

### 2. Install Dependencies

```bash
# Navigate to project directory
cd smart_parking

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure Parking Slots

The system comes with default 6 parking slots. To customize:

```bash
# Run the slot creation script
python create_slots.py
```

To define custom slots, edit the `slots.pkl` file or modify `create_slots.py`.

## 🚀 Running the Application

### Basic Usage (Webcam)

```bash
python app.py
```

The server will start at `http://localhost:5000`

### With Custom Port

```bash
# Run on custom port (e.g., 8080)
python app.py 8080
```

### With Video File

Edit `app.py` to specify a video file path, or pass it as a query parameter:

```
http://localhost:5000/video_feed?video=path/to/your/video.mp4
```

## 📖 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Main dashboard |
| `/video_feed` | Live video stream |
| `/api/status` | Get parking status (JSON) |
| `/api/slots` | Get slot configuration |
| `/api/reset` | Reset detector |

### Example API Response

```json
{
  "success": true,
  "data": {
    "total_slots": 6,
    "empty_slots": 3,
    "occupied_slots": 3,
    "available": true,
    "status": "Parking Available"
  }
}
```

## 🎯 How It Works

### 1. Video Processing Pipeline

1. **Frame Capture**: Read frames from video source (webcam/video file)
2. **Preprocessing**: Resize, convert to grayscale, apply Gaussian blur
3. **Thresholding**: Apply adaptive thresholding for edge detection
4. **Slot Detection**: For each parking slot:
   - Crop the region of interest
   - Count non-zero pixels (white pixels = empty space)
   - Compare against threshold to determine status

### 2. Visualization

- **Green Rectangle**: Empty parking slot
- **Red Rectangle**: Occupied parking slot
- **Slot Number**: Displayed inside each rectangle

### 3. Alert System

- **Parking Available**: When at least 1 slot is empty
- **Parking Full**: When all slots are occupied

## 🔧 Configuration

### Adjusting Detection Sensitivity

In `parking_detector.py`, modify the `occupancy_threshold`:

```python
detector = ParkingDetector(occupancy_threshold=0.15)  # Lower = more strict
```

### Adding More Parking Slots

Edit `create_slots.py` and add more slot coordinates:

```python
default_slots = [
    (50, 100, 80, 120),   # Slot 1
    (150, 100, 80, 120),  # Slot 2
    # Add more slots here...
]
```

## 📝 Data Logging

Parking data is automatically logged to `parking_log.csv`:

```csv
Timestamp,Slo

t ID,Status
2024-01-15 10:30:00,1,EMPTY
2024-01-15 10:30:00,2,OCCUPIED
...
```

## 🐛 Troubleshooting

### Issue: "Could not open video source"

**Solution**: Ensure webcam is connected or provide a valid video file path.

### Issue: "Slots file not found"

**Solution**: Run `python create_slots.py` to generate the default slots file.

### Issue: Poor detection accuracy

**Solution**: 
- Adjust `occupancy_threshold` in `parking_detector.py`
- Ensure good lighting in the video feed
- Adjust slot coordinates in `slots.pkl`

### Issue: Video stream not loading

**Solution**: 
- Check if Flask server is running
- Ensure port 5000 is not in use
- Try a different browser

## 📦 Requirements

```
Flask>=2.3.0
opencv-python>=4.8.0
numpy>=1.24.0
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is for educational purposes.

---

**Note**: For production deployment, consider:
- Using a production WSGI server (Gunicorn, uWSGI)
- Implementing authentication
- Adding HTTPS
- Using a proper database instead of CSV