"""
Parking Slot Detector Module
============================
This module handles the core parking detection logic using OpenCV.
It processes video frames and detects empty/occupied parking slots.
"""

import cv2
import numpy as np
from utils import (
    load_slots,
    get_slots_file_path,
    apply_image_processing,
    calculate_occupancy,
    get_video_source,
    log_parking_data,
    get_log_file_path
)


class ParkingDetector:
    """
    Main class for detecting parking slot occupancy.
    
    Attributes:
        video_source: Video file path or webcam index
        slots: List of parking slot coordinates
        occupancy_threshold: Threshold for determining empty/occupied
        frame_width: Width to resize frames for processing
    """
    
    def __init__(self, video_source=None, occupancy_threshold=0.15, frame_width=640):
        """
        Initialize the parking detector.
        
        Args:
            video_source: Path to video file or None for webcam
            occupancy_threshold: Ratio below which slot is considered empty
            frame_width: Width to resize processing frames
        """
        self.video_source = get_video_source(video_source)
        self.slots = load_slots(get_slots_file_path())
        self.occupancy_threshold = occupancy_threshold
        self.frame_width = frame_width
        self.cap = None
        self.frame_count = 0
        
        # Statistics
        self.total_slots = len(self.slots)
        self.empty_slots = 0
        self.occupied_slots = 0
        
        print(f"Parking Detector initialized with {self.total_slots} slots")
        print(f"Video source: {self.video_source}")
    
    def open_video(self):
        """
        Open the video capture device/file.
        
        Returns:
            True if successful, False otherwise
        """
        self.cap = cv2.VideoCapture(self.video_source)
        
        if not self.cap.isOpened():
            print(f"Error: Could not open video source: {self.video_source}")
            return False
        
        print("Video capture opened successfully")
        return True
    
    def close_video(self):
        """Release video capture resources."""
        if self.cap:
            self.cap.release()
            print("Video capture closed")
    
    def process_frame(self, frame):
        """
        Process a single frame to detect parking slot occupancy.
        
        Args:
            frame: Input frame from video
            
        Returns:
            Tuple of (processed_frame, slot_status_list)
        """
        # Resize frame for consistent processing
        h, w = frame.shape[:2]
        scale = self.frame_width / w
        frame_resized = cv2.resize(frame, (self.frame_width, int(h * scale)))
        
        # Apply image processing
        processed = apply_image_processing(frame_resized)
        
        # Scale slot coordinates to match resized frame
        scaled_slots = self._scale_slots(scale)
        
        # Detect occupancy for each slot
        slot_status = []
        
        for i, slot in enumerate(scaled_slots):
            x, y, slot_w, slot_h = slot
            
            # Crop the parking slot region
            slot_region = processed[y:y+slot_h, x:x+slot_w]
            
            # Skip if region is empty
            if slot_region.size == 0:
                slot_status.append({
                    'id': i + 1,
                    'status': 'UNKNOWN',
                    'occupancy': 0
                })
                continue
            
            # Calculate occupancy ratio
            occupancy = calculate_occupancy(slot_region)
            
            # Determine status based on threshold
            # Lower occupancy = more empty space = EMPTY
            # Higher occupancy = less empty space = OCCUPIED
            is_empty = occupancy < self.occupancy_threshold
            
            status = 'EMPTY' if is_empty else 'OCCUPIED'
            
            slot_status.append({
                'id': i + 1,
                'status': status,
                'occupancy': occupancy
            })
            
            # Draw rectangle on frame
            color = (0, 255, 0) if is_empty else (0, 0, 255)  # Green for empty, Red for occupied
            cv2.rectangle(frame_resized, (x, y), (x + slot_w, y + slot_h), color, 2)
            
            # Draw slot number
            cv2.putText(
                frame_resized,
                str(i + 1),
                (x + slot_w // 2 - 10, y + slot_h // 2 + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )
        
        # Update statistics
        self.empty_slots = sum(1 for s in slot_status if s['status'] == 'EMPTY')
        self.occupied_slots = sum(1 for s in slot_status if s['status'] == 'OCCUPIED')
        
        # Log data periodically (every 30 frames)
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            self._log_status(slot_status)
        
        return frame_resized, slot_status
    
    def _scale_slots(self, scale):
        """
        Scale slot coordinates to match resized frame.
        
        Args:
            scale: Scale factor from original to resized frame
            
        Returns:
            List of scaled slot coordinates
        """
        return [
            (int(x * scale), int(y * scale), int(w * scale), int(h * scale))
            for x, y, w, h in self.slots
        ]
    
    def _log_status(self, slot_status):
        """
        Log parking status to CSV file.
        
        Args:
            slot_status: List of slot status dictionaries
        """
        try:
            log_path = get_log_file_path()
            for slot in slot_status:
                log_parking_data(log_path, slot['id'], slot['status'])
        except Exception as e:
            print(f"Error logging status: {e}")
    
    def get_frame(self):
        """
        Get next frame from video source.
        
        Returns:
            Frame or None if no frame available
        """
        if not self.cap:
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            # Loop video if it's a file
            if isinstance(self.video_source, str):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
        
        return frame if ret else None
    
    def get_statistics(self):
        """
        Get current parking statistics.
        
        Returns:
            Dictionary with parking statistics
        """
        return {
            'total': self.total_slots,
            'empty': self.empty_slots,
            'occupied': self.occupied_slots,
            'available': self.empty_slots > 0
        }
    
    def generate_frames(self):
        """
        Generator function for streaming video frames.
        
        Yields:
            JPEG-encoded frames as byte strings
        """
        if not self.open_video():
            return
        
        try:
            while True:
                frame = self.get_frame()
                
                if frame is None:
                    break
                
                # Process frame
                processed_frame, slot_status = self.process_frame(frame)
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
                
                # Yield frame in multipart response format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        except Exception as e:
            print(f"Error generating frames: {e}")
        
        finally:
            self.close_video()


def create_detector(video_source=None):
    """
    Factory function to create a ParkingDetector instance.
    
    Args:
        video_source: Optional path to video file
        
    Returns:
        ParkingDetector instance
    """
    return ParkingDetector(video_source=video_source)


# Main execution for testing
if __name__ == "__main__":
    print("=" * 50)
    print("Smart Parking System - Detector Test")
    print("=" * 50)
    
    # Create detector
    detector = create_detector()
    
    # Try to open video
    if detector.open_video():
        print("\nProcessing frames...")
        
        # Process a few frames for testing
        for i in range(10):
            frame = detector.get_frame()
            if frame is not None:
                processed, status = detector.process_frame(frame)
                stats = detector.get_statistics()
                print(f"Frame {i+1}: {stats}")
        
        detector.close_video()
        print("\nTest completed successfully!")
    else:
        print("Could not open video source")