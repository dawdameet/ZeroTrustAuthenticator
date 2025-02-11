import pandas as pd
import numpy as np

# Generate synthetic data
np.random.seed(42)
data = {
    'avg_mouse_speed': np.random.uniform(1.0, 3.0, 100),
    'click_frequency': np.random.uniform(0.05, 0.5, 100),
    'label': ['legitimate' if i % 2 == 0 else 'suspicious' for i in range(100)]
}

df = pd.DataFrame(data)
df.to_csv('labeled_behavior_data.csv', index=False)

print("Synthetic data saved to 'labeled_behavior_data.csv'")