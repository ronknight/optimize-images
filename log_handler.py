import os
import csv
import datetime
from pathlib import Path

class CompressionLogger:
    """
    A class for logging image compression operations.
    """
    
    def __init__(self, log_dir="logs"):
        """
        Initialize the logger with a directory for log files.
        
        Args:
            log_dir (str): Directory to store log files
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Create a log file with current timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"compression_log_{timestamp}.csv")
        
        # Initialize CSV file with headers
        with open(self.log_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Filename', 'Original Size (KB)', 
                            'Compressed Size (KB)', 'Savings (%)', 'Status'])
    
    def log_compression(self, filename, original_size, compressed_size, status="Success"):
        """
        Log a compression operation.
        
        Args:
            filename (str): Name of the processed file
            original_size (int): Original size in bytes
            compressed_size (int): Compressed size in bytes
            status (str): Status of the operation (Success/Error)
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Convert sizes to KB
        original_kb = original_size / 1024
        compressed_kb = compressed_size / 1024
        
        # Calculate savings percentage
        if original_size > 0:
            savings = ((original_size - compressed_size) / original_size) * 100
        else:
            savings = 0
            
        # Log to CSV
        with open(self.log_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                timestamp,
                filename,
                f"{original_kb:.2f}",
                f"{compressed_kb:.2f}",
                f"{savings:.2f}",
                status
            ])
        
        return {
            'filename': filename,
            'original_size': original_kb,
            'compressed_size': compressed_kb,
            'savings': savings,
            'status': status
        }
    
    def log_error(self, filename, error_message):
        """
        Log an error that occurred during compression.
        
        Args:
            filename (str): Name of the file
            error_message (str): Description of the error
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.log_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                timestamp,
                filename,
                'N/A',
                'N/A',
                'N/A',
                f"Error: {error_message}"
            ])
    
    def get_summary(self):
        """
        Return a summary of all operations in the log.
        
        Returns:
            dict: Summary statistics
        """
        total_files = 0
        successful = 0
        failed = 0
        total_original = 0
        total_compressed = 0
        
        try:
            with open(self.log_file, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                
                for row in reader:
                    total_files += 1
                    if row[5].startswith('Error'):
                        failed += 1
                    else:
                        successful += 1
                        total_original += float(row[2])
                        total_compressed += float(row[3])
            
            if total_original > 0:
                overall_savings = ((total_original - total_compressed) / total_original) * 100
            else:
                overall_savings = 0
                
            return {
                'total_files': total_files,
                'successful': successful,
                'failed': failed,
                'total_original_kb': total_original,
                'total_compressed_kb': total_compressed,
                'overall_savings_percent': overall_savings
            }
        except Exception as e:
            return {
                'error': f"Failed to generate summary: {str(e)}"
            }
