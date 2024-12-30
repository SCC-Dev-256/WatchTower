class RestartMonitor:
    def __init__(self):
        pass

    async def monitor_restart_loop(self, encoder_id: str):
        # Get recent logs from encoder
        log_data = await self._get_device_logs(encoder_id)
        log_lines = log_data.splitlines()
        
        # Check for storage corruption pattern
        restart_keywords = ["initialization", "assigning", "network access"]
        
        # Small log file indicates recent reset
        if len(log_lines) <= 10:
            # Check for reset keywords in limited log entries
            if any(keyword in line.lower() for line in log_lines for keyword in restart_keywords):
                self.logger.critical(
                    "Storage corrupt reboot cycle detected",
                    extra={
                        'encoder_id': encoder_id,
                        'anomaly_type': 'Storage Reboot Cycle'
                    }
                )
                
                # Update metrics
                self.metrics['storage_failures'].labels(encoder_id).inc()
                
                # Take corrective action
                await self._handle_corrupted_storage(encoder_id)
                return

        # Also check general restart count as backup
        restart_count = self.metrics['restart_count'].labels(encoder_id).inc()
        if restart_count > 3:  # Threshold for general restarts
            self.logger.warning(f"Encoder {encoder_id} has restarted {restart_count} times")
            await self._take_preventive_action(encoder_id)