"""
Utility functions for Smart Parking System
==========================================
This module provides helper functions for:
- File path management
- Parking slot data handling
- CSV logging
- Image processing helpers
"""

import os
import csv
import pickle
from datetime import datetime
from pathlib import Path


def get_project_root():
    """
    Get the project root directory.
    Returns the absolute path to the smart_parking folder.
    """
    return Path(__file__).parent


def get_slots_file_path():
    """
    Get the path to the slots.pkl file.
    Creates the file with default slots if it doesn't exist.
    """
    slots_path = get_project_root() / "slots.pkl"
    
    # If slots.pkl doesn't exist, create default parking slots
    if not slots_path.exists():
        create_default_slots(slots_path)
    
    return str(slots_path)


def create_default_slots(output_path):
    """
    Create a default parking slot configuration.
    This creates 6 sample parking slots in a grid layout.
    
    Args:
        output_path: Path where slots.pkl will be saved
    """
    # Default parking slots (x, y, width, height)
    # These are relative coordinates that will be scaled to video size
    default_slots = [
        (50, 100, 80, 120),   # Slot 1
        (150, 100, 80, 120),  # Slot 2
        (250, 100, 80, 120),  # Slot 3
        (50, 250, 80, 120),   # Slot 4
        (150, 250, 80, 120),  # Slot 5
        (250, 250, 80, 120),  # Slot 6
    ]
    
    save_slots(default_slots, output_path)
    print(f"Created default slots at: {output_path}")


def save_slots(slots, filepath):
    """
    Save parking slot coordinates to a pickle file.
    
    Args:
        slots: List of tuples (x, y, width, height)
        filepath: Path to save the pickle file
    """
    try:
        with open(filepath, 'wb') as f:
            pickle.dump(slots, f)
        print(f"Slots saved successfully to: {filepath}")
    except Exception as e:
        print(f"Error saving slots: {e}")
        raise


def load_slots(filepath):
    """
    Load parking slot coordinates from a pickle file.
    
    Args:
        filepath: Path to the slots.pkl file
        
    Returns:
        List of tuples (x, y, width, height)
    """
    try:
        with open(filepath, 'rb') as f:
            slots = pickle.load(f)
        print(f"Loaded {len(slots)} parking slots from: {filepath}")
        return slots
    except FileNotFoundError:
        print(f"Slots file not found: {filepath}")
        # Create default slots if file doesn't exist
        create_default_slots(filepath)
        return load_slots(filepath)
    except Exception as e:
        print(f"Error loading slots: {e}")
        raise


def get_video_source(video_path=None):
    """
    Determine the video source to use.
    
    Args:
        video_path: Optional path to video file. If None, uses webcam.
        
    Returns:
        Video source (path string or webcam index)
    """
    if video_path and os.path.exists(video_path):
        return video_path
    
    # Default to webcam (0)
    print("Using webcam as video source")
    return 0


def log_parking_data(csv_path, slot_id, status, timestamp=None):
    """
    Log parking slot status to a CSV file.
    
    Args:
        csv_path: Path to the CSV log file
        slot_id: ID/number of the parking slot
        status: 'EMPTY' or 'OCCUPIED'
        timestamp: Optional timestamp (defaults to current time)
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    file_exists = os.path.exists(csv_path)
    
    try:
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                # Write header if file is new
                writer.writerow(['Timestamp', 'Slot ID', 'Status'])
            writer.writerow([timestamp, slot_id, status])
    except Exception as e:
        print(f"Error logging parking data: {e}")


def get_log_file_path():
    """
    Get the path to the parking log CSV file.
    """
    return str(get_project_root() / "parking_log.csv")


def ensure_directory(path):
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        path: Directory path to ensure exists
    """
    os.makedirs(path, exist_ok=True)


def resize_frame(frame, width=None, height=None, max_dimension=800):
    """
    Resize frame while maintaining aspect ratio.
    
    Args:
        frame: Input frame (numpy array)
        width: Target width (optional)
        height: Target height (optional)
        max_dimension: Maximum dimension if width/height not specified
        
    Returns:
        Resized frame
    """
    h, w = frame.shape[:2]
    
    if width is None and height is None:
        # Scale based on max_dimension
        if max(h, w) > max_dimension:
            scale = max_dimension / max(h, w)
            width = int(w * scale)
            height = int(h * scale)
        else:
            return frame
    
    if width and height:
        return cv2.resize(frame, (width, height))
    elif width:
        aspect = width / w
        height = int(h * aspect)
        return cv2.resize(frame, (width, height))
    elif height:
        aspect = height / h
        width = int(w * aspect)
        return cv2.resize(frame, (width, height))
    
    return frame


# Import cv2 here to avoid circular imports
import cv2


def apply_image_processing(frame):
    """
    Apply image processing steps for parking detection.
    
    Args:
        frame: Input frame (numpy array)
        
    Returns:
        Processed frame (grayscale, blurred, thresholded)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2
    )
    
    return thresh


def calculate_occupancy(cropped_region):
    """
    Calculate occupancy percentage based on non-zero pixels.
    
    Args:
        cropped_region: Binary image of the parking slot
        
    Returns:
        Occupancy ratio (0.0 to 1.0)
    """
    # Count non-zero pixels (white pixels = empty space)
    non_zero = cv2.countNonZero(cropped_region)
    total_pixels = cropped_region.shape[0] * cropped_region.shape[1]
    
    return non_zero / total_pixels if total_pixels > 0 else 0