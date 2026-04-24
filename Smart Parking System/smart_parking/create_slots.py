"""
Script to generate default parking slots
=========================================
Run this script to create the slots.pkl file with default parking slot coordinates.
"""

import pickle
import os


def create_default_slots():
    """Create default parking slot configuration."""
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
    
    return default_slots


def save_slots(slots, filepath):
    """Save parking slot coordinates to a pickle file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'wb') as f:
        pickle.dump(slots, f)
    
    print(f"Slots saved to: {filepath}")
    print(f"Created {len(slots)} parking slots")


if __name__ == "__main__":
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create slots.pkl in the same directory
    slots_path = os.path.join(script_dir, "slots.pkl")
    
    # Generate and save default slots
    slots = create_default_slots()
    save_slots(slots, slots_path)
    
    print("\nDefault parking slots created successfully!")
    print("You can modify slots.pkl to define custom parking slot positions.")