import cv2
import numpy as np
import mss
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage
import pyautogui
from PIL import Image, ImageChops
import os
from datetime import datetime

class SmartScrollCapture(QObject):
    """Advanced scrolling screenshot with smart element detection"""
    
    capture_progress = pyqtSignal(int, int)  # current, total
    capture_completed = pyqtSignal(list)     # list of captured images
    capture_error = pyqtSignal(str)
    
    def __init__(self, canvas=None):
        super().__init__()
        self.canvas = canvas
        self.screen_capturer = mss.mss()
        self.is_capturing = False
        self.captured_images = []
        self.scroll_positions = []
        self.stable_regions = set()  # Regions that don't change (headers, navbars, etc.)
        
    def capture_scrolling_screenshot(self, target_window=None, max_scrolls=50):
        """Capture scrolling screenshot with smart element detection"""
        if self.is_capturing:
            self.capture_error.emit("Capture already in progress")
            return
            
        self.is_capturing = True
        self.captured_images = []
        self.scroll_positions = []
        self.stable_regions = set()
        
        try:
            # Get the target area to capture
            if target_window:
                # Capture specific window
                capture_area = self.get_window_geometry(target_window)
            else:
                # Capture current screen area
                screen = QApplication.primaryScreen()
                capture_area = screen.geometry()
                
            print(f"🎯 Starting smart scroll capture for area: {capture_area}")
            
            # Initial capture
            initial_img = self.capture_area(capture_area)
            if initial_img is None:
                raise Exception("Failed to capture initial screen")
                
            self.captured_images.append(initial_img)
            self.scroll_positions.append(0)
            
            # Analyze initial image for stable regions
            self.detect_stable_regions(initial_img, capture_area)
            
            # Start scrolling and capturing
            scroll_count = 0
            previous_img = initial_img
            
            while scroll_count < max_scrolls and self.is_capturing:
                # Scroll down
                pyautogui.scroll(-3)  # Scroll down 3 units
                time.sleep(0.5)  # Wait for scroll to complete
                
                # Capture current view
                current_img = self.capture_area(capture_area)
                if current_img is None:
                    break
                    
                # Check if we've reached the end (no significant change)
                if self.is_end_of_scroll(previous_img, current_img):
                    print("🏁 Reached end of scrollable content")
                    break
                
                # Check for duplicate content (already captured)
                if not self.is_duplicate_content(previous_img, current_img):
                    self.captured_images.append(current_img)
                    self.scroll_positions.append(scroll_count + 1)
                    print(f"📄 Captured scroll position {scroll_count + 1}")
                else:
                    print(f"⏭ Skipping duplicate content at position {scroll_count + 1}")
                
                previous_img = current_img
                scroll_count += 1
                
                # Emit progress
                self.capture_progress.emit(scroll_count, max_scrolls)
                
            # Process and stitch captured images
            if len(self.captured_images) > 1:
                final_image = self.stitch_scroll_images()
                if final_image is not None:
                    # Save the result
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"scroll_capture_{timestamp}.png"
                    # Use the configured screenshots path from canvas
                    save_path = self.canvas.screenshots_path if hasattr(self.canvas, 'screenshots_path') else os.path.join(os.getcwd(), "captures")
                    filepath = os.path.join(save_path, filename)
                                    
                    # Create captures directory if it doesn't exist
                    os.makedirs(save_path, exist_ok=True)
                                    
                    # Convert PIL to OpenCV and save
                    cv_img = cv2.cvtColor(np.array(final_image), cv2.COLOR_RGB2BGR)
                    cv2.imwrite(filepath, cv_img)
                    
                    print(f"✅ Scroll capture saved: {filepath}")
                    self.capture_completed.emit([filepath])
                else:
                    self.capture_error.emit("Failed to stitch captured images")
            else:
                # Save single image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.png"
                # Use the configured screenshots path from canvas
                save_path = self.canvas.screenshots_path if hasattr(self.canvas, 'screenshots_path') else os.path.join(os.getcwd(), "captures")
                filepath = os.path.join(save_path, filename)
                os.makedirs(save_path, exist_ok=True)
                
                cv_img = cv2.cvtColor(np.array(self.captured_images[0]), cv2.COLOR_RGB2BGR)
                cv2.imwrite(filepath, cv_img)
                
                print(f"✅ Single capture saved: {filepath}")
                self.capture_completed.emit([filepath])
                
        except Exception as e:
            error_msg = f"Capture failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.capture_error.emit(error_msg)
        finally:
            self.is_capturing = False
            
    def capture_area_screenshot(self, area=None):
        """Capture specific area screenshot"""
        try:
            if area is None:
                # Full screen capture
                screen = QApplication.primaryScreen()
                area = screen.geometry()
                
            img = self.capture_area(area)
            if img is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"area_capture_{timestamp}.png"
                # Use the configured screenshots path from canvas
                save_path = self.canvas.screenshots_path if hasattr(self.canvas, 'screenshots_path') else os.path.join(os.getcwd(), "captures")
                filepath = os.path.join(save_path, filename)
                os.makedirs(save_path, exist_ok=True)
                
                cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                cv2.imwrite(filepath, cv_img)
                
                print(f"✅ Area capture saved: {filepath}")
                return filepath
            else:
                raise Exception("Failed to capture area")
                
        except Exception as e:
            error_msg = f"Area capture failed: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
            
    def capture_full_screenshot(self):
        """Capture full screen screenshot"""
        try:
            # Get all monitors
            monitors = self.screen_capturer.monitors
            
            # Capture primary monitor
            screenshot = self.screen_capturer.grab(monitors[1])  # monitors[0] is all monitors combined
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"full_capture_{timestamp}.png"
            # Use the configured screenshots path from canvas
            filepath = os.path.join(self.canvas.screenshots_path if hasattr(self.canvas, 'screenshots_path') else os.path.join(os.getcwd(), "captures"), filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            img.save(filepath)
            print(f"✅ Full screen capture saved: {filepath}")
            return filepath
            
        except Exception as e:
            error_msg = f"Full screen capture failed: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
            
    def capture_code_editor_screenshot(self):
        """Smart capture for code editors - only capture scrollable code area"""
        try:
            print("📝 Starting code editor capture...")
            
            # This would need to detect code editor windows and their scrollable areas
            # For now, we'll capture the active window and apply smart scrolling
            active_window = self.get_active_window()
            if active_window:
                return self.capture_scrolling_screenshot(active_window)
            else:
                # Fallback to area selection
                return self.capture_area_screenshot()
                
        except Exception as e:
            error_msg = f"Code editor capture failed: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
            
    def capture_window_screenshot(self, window_title=None):
        """Capture specific window"""
        try:
            if window_title:
                # Find window by title
                target_window = self.find_window_by_title(window_title)
            else:
                # Capture active window
                target_window = self.get_active_window()
                
            if target_window:
                img = self.capture_window(target_window)
                if img is not None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"window_capture_{timestamp}.png"
                    filepath = os.path.join(os.getcwd(), "captures", filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    img.save(filepath)
                    print(f"✅ Window capture saved: {filepath}")
                    return filepath
                    
            raise Exception("Window not found or capture failed")
            
        except Exception as e:
            error_msg = f"Window capture failed: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
            
    # Helper methods
    def capture_area(self, area):
        """Capture specific screen area"""
        try:
            monitor = {
                "top": area.y(),
                "left": area.x(),
                "width": area.width(),
                "height": area.height()
            }
            screenshot = self.screen_capturer.grab(monitor)
            return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        except Exception as e:
            print(f"Capture area error: {e}")
            return None
            
    def capture_window(self, window):
        """Capture specific window"""
        try:
            # Get window geometry
            geometry = self.get_window_geometry(window)
            return self.capture_area(geometry)
        except Exception as e:
            print(f"Capture window error: {e}")
            return None
            
    def detect_stable_regions(self, image, area):
        """Detect regions that remain static (headers, navbars, etc.)"""
        # This is a simplified implementation
        # In a full implementation, you'd analyze multiple frames to identify
        # regions that don't change between scrolls
        width, height = image.size
        
        # Assume top 15% and bottom 10% might be stable regions (headers/footers)
        header_height = int(height * 0.15)
        footer_height = int(height * 0.10)
        
        self.stable_regions = {
            'header': (0, 0, width, header_height),
            'footer': (0, height - footer_height, width, height)
        }
        
        print(f"🔍 Detected stable regions: header={header_height}px, footer={footer_height}px")
        
    def is_end_of_scroll(self, prev_img, curr_img):
        """Detect if we've reached the end of scrollable content"""
        try:
            # Convert to grayscale for comparison
            prev_gray = prev_img.convert('L')
            curr_gray = curr_img.convert('L')
            
            # Calculate difference
            diff = ImageChops.difference(prev_gray, curr_gray)
            diff_array = np.array(diff)
            
            # If very little has changed, we might be at the end
            change_ratio = np.count_nonzero(diff_array) / diff_array.size
            
            # Threshold for "end of content" - very little change
            return change_ratio < 0.02
            
        except Exception as e:
            print(f"End of scroll detection error: {e}")
            return False
            
    def is_duplicate_content(self, prev_img, curr_img):
        """Detect if current content is duplicate of previous"""
        try:
            # Focus on the middle region (most likely to contain unique content)
            width, height = prev_img.size
            
            # Define middle region (avoiding potential stable regions)
            middle_top = int(height * 0.2)
            middle_bottom = int(height * 0.8)
            middle_region = (0, middle_top, width, middle_bottom)
            
            # Crop to middle region
            prev_middle = prev_img.crop(middle_region)
            curr_middle = curr_img.crop(middle_region)
            
            # Compare middle regions
            diff = ImageChops.difference(prev_middle, curr_middle)
            diff_array = np.array(diff)
            
            # If middle content is very similar, it's likely duplicate
            change_ratio = np.count_nonzero(diff_array) / diff_array.size
            
            # Threshold for "duplicate content"
            return change_ratio < 0.1
            
        except Exception as e:
            print(f"Duplicate content detection error: {e}")
            return False
            
    def stitch_scroll_images(self):
        """Stitch captured scroll images together"""
        try:
            if len(self.captured_images) < 2:
                return self.captured_images[0] if self.captured_images else None
                
            # Start with first image
            result = self.captured_images[0].copy()
            
            # For each subsequent image, find overlap and stitch
            for i in range(1, len(self.captured_images)):
                next_img = self.captured_images[i]
                result = self.stitch_two_images(result, next_img)
                
            return result
            
        except Exception as e:
            print(f"Image stitching error: {e}")
            return None
            
    def stitch_two_images(self, img1, img2):
        """Stitch two images together with overlap detection"""
        try:
            # Simple stitching - place img2 below img1
            # In a full implementation, you'd detect overlap and blend
            width1, height1 = img1.size
            width2, height2 = img2.size
            
            # Create new image with combined height
            result_width = max(width1, width2)
            result_height = height1 + height2
            result = Image.new('RGB', (result_width, result_height))
            
            # Paste images
            result.paste(img1, (0, 0))
            result.paste(img2, (0, height1))
            
            return result
            
        except Exception as e:
            print(f"Two image stitching error: {e}")
            # Fallback - return the first image
            return img1
            
    # System-specific methods (would need platform-specific implementations)
    def get_active_window(self):
        """Get currently active window"""
        # This would need platform-specific implementation
        # For Windows: use win32gui
        # For macOS: use Quartz
        # For Linux: use X11
        return None
        
    def find_window_by_title(self, title):
        """Find window by title"""
        # Platform-specific window finding
        return None
        
    def get_window_geometry(self, window):
        """Get window geometry"""
        # Platform-specific geometry retrieval
        from PyQt5.QtCore import QRect
        screen = QApplication.primaryScreen()
        return screen.geometry()