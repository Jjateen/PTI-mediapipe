import pandas as pd
import matplotlib.pyplot as plt

# Load the time series data from the CSV file
df = pd.read_csv('hand_control_data.csv')

# Convert the 'Timestamp' column to datetime format
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')

# Plot the time series data
plt.figure(figsize=(12, 6))

# Plot Middle Finger Angle
plt.subplot(2, 1, 1)
plt.plot(df['Timestamp'], df['Middle_Finger_Angle'], label='Middle Finger Angle', color='blue')
plt.title('Middle Finger Angle Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Angle (degrees)')
plt.legend()

# Plot Error
plt.subplot(2, 1, 2)
plt.plot(df['Timestamp'], df['Error'], label='Error', color='red')
plt.title('Error Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Error (degrees)')
plt.legend()

plt.tight_layout()
plt.show()