import cv2
import numpy as np
import psutil
from typing import Tuple, Optional

class BitrateOptimizer:
    def __init__(self):
        # Default bitrate settings from Parameter_Configuration_Table.csv
        self.default_video_bitrate = 10000  # kbps
        self.min_video_bitrate = 500  # kbps
        self.max_video_bitrate = 50000  # kbps
        
        # Motion complexity thresholds
        self.low_motion_threshold = 0.05
        self.high_motion_threshold = 0.15
        
        # Network bandwidth thresholds (in Mbps)
        self.min_bandwidth = 1
        self.target_bandwidth = 10
        
    def calculate_motion_complexity(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> float:
        """Calculate motion complexity between two frames"""
        # Convert frames to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        # Compute absolute difference between frames
        frame_diff = cv2.absdiff(prev_gray, curr_gray)
        
        # Threshold the difference
        _, diff_thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
        
        # Calculate the percentage of changed pixels
        motion_complexity = np.sum(diff_thresh) / (diff_thresh.size * 255)
        return motion_complexity

    def get_network_bandwidth(self) -> float:
        """Get current network bandwidth in Mbps"""
        net_io = psutil.net_io_counters()
        bytes_per_sec = net_io.bytes_sent + net_io.bytes_recv
        mbps = (bytes_per_sec * 8) / (1024 * 1024)  # Convert to Mbps
        return mbps

    def calculate_motion_scale(self, motion_complexity: float) -> float:
        """Calculate scaling factor based on motion complexity"""
        if motion_complexity < self.low_motion_threshold:
            return 0.8  # Reduce bitrate for static scenes
        elif motion_complexity > self.high_motion_threshold:
            return 1.5  # Increase bitrate for high motion
        return 1.0

    def calculate_bandwidth_scale(self, current_bandwidth: float) -> float:
        """Calculate scaling factor based on available bandwidth"""
        if current_bandwidth < self.min_bandwidth:
            return 0.5  # Significantly reduce bitrate
        
        bandwidth_ratio = current_bandwidth / self.target_bandwidth
        return min(1.0, bandwidth_ratio)

    def optimize_bitrate(self, prev_frame: Optional[np.ndarray] = None, 
                        curr_frame: Optional[np.ndarray] = None) -> Tuple[int, str]:
        """
        Optimize bitrate based on motion complexity and network conditions
        Returns: (optimized_bitrate, status_message)
        """
        try:
            # Get network bandwidth
            bandwidth = self.get_network_bandwidth()
            bandwidth_scale = self.calculate_bandwidth_scale(bandwidth)
            
            # Calculate motion scale if frames provided
            motion_scale = 1.0
            if prev_frame is not None and curr_frame is not None:
                motion_complexity = self.calculate_motion_complexity(prev_frame, curr_frame)
                motion_scale = self.calculate_motion_scale(motion_complexity)
            
            # Calculate optimized bitrate
            optimized_bitrate = int(self.default_video_bitrate * motion_scale * bandwidth_scale)
            
            # Ensure bitrate stays within bounds
            optimized_bitrate = max(self.min_video_bitrate, 
                                  min(optimized_bitrate, self.max_video_bitrate))
            
            status = f"Bitrate optimized: {optimized_bitrate}kbps (motion_scale={motion_scale:.2f}, bandwidth_scale={bandwidth_scale:.2f})"
            return optimized_bitrate, status
            
        except Exception as e:
            return self.default_video_bitrate, f"Optimization failed: {str(e)}. Using default bitrate."
