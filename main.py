import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import serial
import sys

class AcousticCameraVisualizer:
    def __init__(self, window_size=500, downsample=5, update_interval=50):
        # Store parameters
        self.window_size = window_size
        self.downsample = downsample
        self.update_interval = update_interval
        self.scaling_factors = [1.0, 1.0]  # For 2 microphones
        
        # Create figure and subplots
        plt.style.use('dark_background')
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        self.fig.suptitle('Acoustic Camera - Dual Microphone Audio Waveforms')
        
        # Setup raw data plot
        self.ax1.set_ylabel('Amplitude')
        self.ax1.set_ylim(0, 1024)  # Adjust for typical ADC range
        self.ax1.set_xlim(0, window_size)
        self.line1_micL, = self.ax1.plot([], [], 'c-', linewidth=1, label='Mic Left')
        self.line1_micR, = self.ax1.plot([], [], 'm-', linewidth=1, label='Mic Right')
        
        # Setup downsampled plot
        self.ax2.set_xlabel('Sample')
        self.ax2.set_ylabel('Amplitude')
        self.ax2.set_ylim(0, 1024)  # Adjust for typical ADC range
        self.ax2.set_xlim(0, window_size // downsample)
        self.line2_micL, = self.ax2.plot([], [], 'c-', linewidth=1, label='Mic Left (Downsampled)')
        self.line2_micR, = self.ax2.plot([], [], 'm-', linewidth=1, label='Mic Right (Downsampled)')
        
        # Add legends
        self.ax1.legend(loc='upper right')
        self.ax2.legend(loc='upper right')
        
        # Initialize data storage
        self.raw_data = [deque([0] * window_size, maxlen=window_size) for _ in range(2)]
        self.downsampled_data = [deque([0] * (window_size // downsample), 
                                      maxlen=window_size // downsample) for _ in range(2)]
        
        # Create x-axis data
        self.x_data_raw = np.arange(window_size)
        self.x_data_downsampled = np.arange(0, window_size, downsample)
        
    def update(self, frame, ser):
        try:
            while ser.in_waiting:
                try:
                    line = ser.readline().decode().strip()
                    values = list(map(int, line.split(',')))
                    
                    if len(values) == 2:  # 2 microphones
                        # Debug: print first few values
                        if len(self.raw_data[0]) < 5:
                            print(f"Received: {values}")
                        
                        # Add to raw data (no scaling for now)
                        for i in range(2):
                            self.raw_data[i].append(values[i])
                        
                        # Add to downsampled data every Nth sample
                        if len(self.raw_data[0]) % self.downsample == 0:
                            for i in range(2):
                                self.downsampled_data[i].append(values[i])
                except (ValueError, UnicodeDecodeError):
                    continue
            
            # Update plots
            self.line1_micL.set_data(self.x_data_raw, list(self.raw_data[0]))
            self.line1_micR.set_data(self.x_data_raw, list(self.raw_data[1]))
            
            self.line2_micL.set_data(self.x_data_downsampled, list(self.downsampled_data[0]))
            self.line2_micR.set_data(self.x_data_downsampled, list(self.downsampled_data[1]))
            
            return (self.line1_micL, self.line1_micR,
                    self.line2_micL, self.line2_micR)
        
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            sys.exit(1)

def main():
    # Setup serial connection
    try:
        ser = serial.Serial('/dev/cu.usbmodem2101', 115200)
        ser.readline()  # Clear any initial data
        print("Serial connection established")
    except serial.SerialException as e:
        print(f"Failed to connect to serial port: {e}")
        sys.exit(1)
    
    # Create visualizer
    visualizer = AcousticCameraVisualizer(
        window_size=500,
        downsample=5,
        update_interval=50
    )
    
    # Create animation
    ani = FuncAnimation(
        visualizer.fig, 
        visualizer.update, 
        fargs=(ser,),
        interval=visualizer.update_interval, 
        blit=True,
        cache_frame_data=False
    )
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()