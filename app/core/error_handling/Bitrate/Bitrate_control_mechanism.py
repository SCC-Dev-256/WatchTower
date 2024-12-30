from app.core.error_handling.Bitrate.optimize_bitrate import BitrateOptimizer

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