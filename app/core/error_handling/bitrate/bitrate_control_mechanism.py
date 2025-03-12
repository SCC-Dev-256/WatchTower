from app.core.error_handling import BitrateOptimizer

# This file contains the BitrateControlManager class, which is used to manage the bitrate of an encoder.
# The BitrateControlManager class has the following methods:
# - adjust_bitrate: Adjusts the bitrate of an encoder.

# The following areas are blank and require input from the user:
# - Additional error handling logic for specific error types or logging requirements that are not yet defined.
# - Configuration details for retry logic, such as exponential backoff or jitter, that may need customization.
# - Any additional metrics or logging categories that the user might want to track.
# - Specific logic for handling different error types in the `adjust_bitrate` method.
# - Detailed implementation for methods like `adjust_bitrate`.

# Levels of abstraction that need to be made specific:
# 1. Error Handling Logic: Define specific logic for handling different types of errors (e.g., network, streaming, recording).
# 2. Retry Logic: Customize and add any additional retry mechanisms, such as exponential backoff or jitter.
# 3. Metrics: Customize and add any additional metrics that need to be tracked.
# 4. Logging: Configure log formatting and output destinations as per the application's requirements.
# 5. Error Analysis: Implement detailed logic for analyzing errors and providing insights.
# 6. Error Entry Creation: Ensure the error data captures all necessary details for each error type.
# 7. Error Processing: Define the specific steps to process and handle each error type in the `adjust_bitrate` method.

class BitrateControlManager:
    def __init__(self, logger, get_device_param, get_current_frame, prev_frames):
        self.logger = logger
        self._get_device_param = get_device_param
        self._get_current_frame = get_current_frame
        self._prev_frames = prev_frames
        self.optimizer = BitrateOptimizer()

    async def adjust_bitrate(self, encoder_id):
        try:
            # Retrieve current bitrate
            current_bitrate = await self._get_device_param(encoder_id, 'Video Bit Rate')
            
            # Get current and previous frames
            curr_frame = self._get_current_frame(current_bitrate)
            prev_frame = self._prev_frames.get(encoder_id)

            # Calculate optimized bitrate
            optimized_bitrate, status = self.optimizer.optimize_bitrate(
                prev_frame=prev_frame,
                curr_frame=curr_frame
            )

            # Store current frame as previous for next iteration
            self._prev_frames[encoder_id] = curr_frame

            # Log the optimization status
            self.logger.info(f"Bitrate optimization: {status}")

        except Exception as e:
            # Log any errors encountered during optimization
            self.logger.error(f"Failed to optimize bitrate: {str(e)}") 