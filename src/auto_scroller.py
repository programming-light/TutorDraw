import pyautogui
import time
import cv2
import numpy as np
from PIL import Image, ImageChops
import os
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QRect

class EnhancedAutoScroller(QObject):
    """Enhanced auto-scrolling with intelligent content detection"""
    
    # Signals
    scroll_progress = pyqtSignal(int, int)  # current_position, total_sections
    section_captured = pyqtSignal(dict)     # section_info
    capture_completed = pyqtSignal(str)     # final_file_path
    capture_error = pyqtSignal(str)
    scroll_speed_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.is_capturing = False
        self.is_paused = False
        self.scroll_speed = 5  # 1-10 scale
        self.captured_sections = []
        self.scroll_position = 0
        self.max_scrolls = 100
        self.capture_area = None
        self.stable_regions = []
        self.last_content_hash = None
        
    def set_scroll_speed(self, speed):
        """Set scrolling speed (1-10)"""
        self.scroll_speed = speed
        self.scroll_speed_changed.emit(speed)
        
    def set_capture_area(self, area):
        """Set the capture area (QRect)"""
        self.capture_area = area
        
    def start_capture(self, area=None, max_scrolls=100):
        """Start the auto-scrolling capture"""
        if self.is_capturing:
            self.capture_error.emit("Capture already in progress")
            return
            
        self.is_capturing = True
        self.is_paused = False
        self.captured_sections = []
        self.scroll_position = 0
        self.max_scrolls = max_scrolls
        self.last_content_hash = None
        
        if area:
            self.capture_area = area
            
        # Detect stable regions in initial view
        self.detect_stable_regions()
        
        # Start the capture process
        self.continue_capture()
        
    def pause_capture(self):
        """Pause the capture"""
        self.is_paused = True
        
    def resume_capture(self):
        """Resume the capture"""
        self.is_paused = False
        self.continue_capture()
        
    def stop_capture(self):
        """Stop the capture and process results"""
        self.is_capturing = False
        self.is_paused = False
        
        if self.captured_sections:
            self.process_captured_sections()
        else:
            self.capture_error.emit("No sections were captured")
            
    def continue_capture(self):
        """Continue the capture process"""
        if not self.is_capturing or self.is_paused:
            return
            
        if self.scroll_position >= self.max_scrolls:
            self.stop_capture()
            return
            
        # Capture current section
        section_image = self.capture_current_section()
        if section_image is None:
            self.capture_error.emit("Failed to capture section")
            return
            
        # Check if content is new/different
        if self.is_new_content(section_image):
            # Save the section
            section_info = {
                'position': self.scroll_position,
                'image': section_image,
                'timestamp': datetime.now()
            }
            
            self.captured_sections.append(section_info)
            self.section_captured.emit(section_info)
            
            # Emit progress
            self.scroll_progress.emit(self.scroll_position + 1, self.max_scrolls)
            
        # Scroll to next position
        scroll_amount = self.get_scroll_amount()
        self.perform_scroll(scroll_amount)
        
        self.scroll_position += 1
        
        # Continue with delay based on speed setting
        delay = self.get_scroll_delay()
        QTimer.singleShot(int(delay * 1000), self.continue_capture)
        
    def capture_current_section(self):
        """Capture the current screen section"""
        try:
            if self.capture_area:
                # Capture specific area
                screenshot = pyautogui.screenshot(region=(
                    self.capture_area.x(),
                    self.capture_area.y(),
                    self.capture_area.width(),
                    self.capture_area.height()
                ))
            else:
                # Full screen capture
                screenshot = pyautogui.screenshot()
                
            return screenshot
            
        except Exception as e:
            print(f"Capture error: {e}")
            return None
            
    def is_new_content(self, image):
        """Check if the current content is new (not duplicate)"""
        try:
            # Convert to grayscale for comparison
            gray_image = image.convert('L')
            
            # Create hash of current content (excluding stable regions)
            current_hash = self.hash_image_content(gray_image)
            
            # Compare with last content
            if self.last_content_hash is not None:
                similarity = self.compare_hashes(self.last_content_hash, current_hash)
                # If very similar (>90%), consider it duplicate
                if similarity > 0.90:
                    return False
                    
            self.last_content_hash = current_hash
            return True
            
        except Exception as e:
            print(f"Content detection error: {e}")
            return True  # Default to capturing if detection fails
            
    def hash_image_content(self, image):
        """Create hash of image content (excluding stable regions)"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Remove stable regions from consideration
            for region in self.stable_regions:
                x, y, w, h = region
                img_array[y:y+h, x:x+w] = 128  # Neutral gray value
                
            # Create simple hash by resizing and averaging
            small_img = cv2.resize(img_array, (16, 16))
            avg = small_img.mean()
            hash_bits = (small_img > avg).astype(int)
            
            return hash_bits.flatten()
            
        except Exception as e:
            print(f"Hash creation error: {e}")
            return np.array([0] * 256)  # Default hash
            
    def compare_hashes(self, hash1, hash2):
        """Compare two image hashes and return similarity (0-1)"""
        try:
            # Calculate Hamming distance
            diff = np.sum(hash1 != hash2)
            total = len(hash1)
            similarity = 1 - (diff / total)
            return similarity
        except:
            return 0.0
            
    def detect_stable_regions(self):
        """Detect stable regions (headers, navbars, etc.)"""
        try:
            # Capture initial view
            initial_image = self.capture_current_section()
            if not initial_image:
                return
                
            width, height = initial_image.size
            
            # Common stable region positions (can be made configurable)
            self.stable_regions = [
                # Top header (15% of height)
                (0, 0, width, int(height * 0.15)),
                # Bottom footer (10% of height)  
                (0, int(height * 0.90), width, int(height * 0.10)),
                # Left sidebar (if present - 20% of width)
                (0, 0, int(width * 0.20), height),
                # Right sidebar (if present - 20% of width)
                (int(width * 0.80), 0, int(width * 0.20), height)
            ]
            
            print(f"🔍 Detected {len(self.stable_regions)} potential stable regions")
            
        except Exception as e:
            print(f"Stable region detection error: {e}")
            self.stable_regions = []
            
    def perform_scroll(self, amount):
        """Perform the actual scrolling"""
        try:
            # Use mouse wheel scrolling
            pyautogui.scroll(-amount)  # Negative for down scrolling
            time.sleep(0.1)  # Small delay for scroll to complete
        except Exception as e:
            print(f"Scroll error: {e}")
            
    def get_scroll_amount(self):
        """Get scroll amount based on speed setting"""
        # Speed 1-10 maps to scroll amounts 1-10
        base_amount = self.scroll_speed
        # Add some randomness to make it more natural
        variation = np.random.randint(-1, 2)
        return max(1, base_amount + variation)
        
    def get_scroll_delay(self):
        """Get delay between scrolls based on speed"""
        # Speed 1 = 1.0 second delay, Speed 10 = 0.1 second delay
        return 1.1 - (self.scroll_speed * 0.1)
        
    def process_captured_sections(self):
        """Process and combine all captured sections"""
        try:
            if len(self.captured_sections) == 0:
                self.capture_error.emit("No sections to process")
                return
                
            if len(self.captured_sections) == 1:
                # Single section - just save it
                section = self.captured_sections[0]
                filepath = self.save_single_image(section['image'])
                self.capture_completed.emit(filepath)
                return
                
            # Multiple sections - stitch them together
            stitched_image = self.stitch_sections()
            if stitched_image:
                filepath = self.save_stitched_image(stitched_image)
                self.capture_completed.emit(filepath)
            else:
                self.capture_error.emit("Failed to stitch captured sections")
                
        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            print(f"❌ {error_msg}")
            self.capture_error.emit(error_msg)
            
    def stitch_sections(self):
        """Stitch captured sections together"""
        try:
            # Start with first image
            result = self.captured_sections[0]['image'].copy()
            
            # For each subsequent section, find overlap and combine
            for i in range(1, len(self.captured_sections)):
                next_section = self.captured_sections[i]['image']
                result = self.combine_images(result, next_section)
                
            return result
            
        except Exception as e:
            print(f"Stitching error: {e}")
            return None
            
    def combine_images(self, img1, img2):
        """Combine two images with overlap detection"""
        try:
            # Simple vertical stacking approach
            # In a more advanced implementation, you'd detect overlap
            # and blend the images smoothly
            
            width1, height1 = img1.size
            width2, height2 = img2.size
            
            # Use the maximum width
            result_width = max(width1, width2)
            result_height = height1 + height2
            
            # Create new image
            result = Image.new('RGB', (result_width, result_height))
            
            # Paste images
            result.paste(img1, (0, 0))
            result.paste(img2, (0, height1))
            
            return result
            
        except Exception as e:
            print(f"Image combination error: {e}")
            return img1  # Return first image as fallback
            
    def save_single_image(self, image):
        """Save a single captured image"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.png"
        filepath = os.path.join(os.getcwd(), "captures", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        image.save(filepath)
        return filepath
        
    def save_stitched_image(self, image):
        """Save the stitched final image"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scroll_capture_{timestamp}.png"
        filepath = os.path.join(os.getcwd(), "captures", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        image.save(filepath)
        return filepath
        
    def get_capture_info(self):
        """Get information about current capture"""
        return {
            'is_capturing': self.is_capturing,
            'is_paused': self.is_paused,
            'scroll_position': self.scroll_position,
            'sections_captured': len(self.captured_sections),
            'scroll_speed': self.scroll_speed,
            'stable_regions': len(self.stable_regions)
        }