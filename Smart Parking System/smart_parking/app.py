"""
Flask Application for Smart Parking System
===========================================
This module provides the web server and API endpoints
for the parking detection system.
"""

import os
import sys
from flask import Flask, render_template, Response, jsonify, request
from parking_detector import ParkingDetector, create_detector


# Initialize Flask application
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'smart-parking-secret-key-2024'
app.config['JSON_SORT_KEYS'] = False

# Global detector instance
detector = None


def get_detector():
    """
    Get or create the parking detector instance.
    Uses singleton pattern to ensure single video capture.
    
    Returns:
        ParkingDetector instance
    """
    global detector
    
    if detector is None:
        # Get video source from query params or use default
        video_source = request.args.get('video')
        
        # If no video file specified, try to find one in the project
        if not video_source:
            video_source = find_sample_video()
        
        detector = create_detector(video_source)
    
    return detector


def find_sample_video():
    """
    Look for sample video files in common locations.
    
    Returns:
        Path to video file or None
    """
    # Check for video files in the project directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    video_names = ['parking.mp4', 'video.mp4', 'test.mp4', 'parking.avi']
    
    # Check specific paths
    search_paths = [
        project_root,
        os.path.join(project_root, '..'),
        os.path.join(project_root, 'videos'),
        os.path.join(os.path.expanduser('~'), 'Videos'),
    ]
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
            
        # Check for named videos
        for name in video_names:
            path = os.path.join(search_path, name)
            if os.path.exists(path):
                print(f"Found video: {path}")
                return path
        
        # Check for any video file
        try:
            for file in os.listdir(search_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in video_extensions:
                    path = os.path.join(search_path, file)
                    print(f"Found video: {path}")
                    return path
        except:
            pass
    
    return None  # Will use webcam


@app.route('/')
def index():
    """
    Main dashboard page.
    
    Returns:
        Rendered HTML template
    """
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """
    Video streaming route.
    Uses multipart response for continuous frame delivery.
    
    Returns:
        Response with multipart/x-mixed-replace content type
    """
    detector = get_detector()
    
    return Response(
        detector.generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/api/status')
def api_status():
    """
    API endpoint for getting current parking status.
    
    Returns:
        JSON response with parking statistics
    """
    try:
        detector = get_detector()
        stats = detector.get_statistics()
        
        return jsonify({
            'success': True,
            'data': {
                'total_slots': stats['total'],
                'empty_slots': stats['empty'],
                'occupied_slots': stats['occupied'],
                'available': stats['available'],
                'status': 'Parking Available' if stats['available'] else 'Parking Full'
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/slots')
def api_slots():
    """
    API endpoint for getting detailed slot information.
    
    Returns:
        JSON response with slot details
    """
    try:
        detector = get_detector()
        
        return jsonify({
            'success': True,
            'data': {
                'slots': detector.slots,
                'total': len(detector.slots)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/reset')
def api_reset():
    """
    API endpoint to reset the detector (switch video source).
    
    Returns:
        JSON response with success status
    """
    global detector
    
    try:
        # Close existing detector
        if detector:
            detector.close_video()
        
        # Reset detector
        detector = None
        
        return jsonify({
            'success': True,
            'message': 'Detector reset successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


def run_server(host='0.0.0.0', port=5000, debug=True):
    """
    Run the Flask development server.
    
    Args:
        host: Host address to bind to
        port: Port number to listen on
        debug: Enable debug mode
    """
    print("=" * 50)
    print("Smart Parking System - Flask Server")
    print("=" * 50)
    print(f"Server starting at http://{host}:{port}")
    print(f"Dashboard: http://{host}:{port}/")
    print(f"Video Feed: http://{host}:{port}/video_feed")
    print(f"API Status: http://{host}:{port}/api/status")
    print("=" * 50)
    
    app.run(host=host, port=port, debug=debug)


# Main execution
if __name__ == '__main__':
    # Get host and port from command line arguments
    host = '0.0.0.0'
    port = 5000
    debug = True
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        host = sys.argv[2]
    if len(sys.argv) > 3:
        debug = sys.argv[3].lower() == 'true'
    
    run_server(host=host, port=port, debug=debug)