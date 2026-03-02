import pandas as pd
import numpy as np

raw_data = pd.read_csv("data/nba_draft_raw.csv")

# 1. Define your metrics
metrics = ['Height', 'Weight', 'Wingspan', 'Standing Reach', 'Hand Length', 'Hand Width', 'Standing Vert', 'Max Vert', 'Lane Agility', 'Shuttle', 'Sprint', 'Bench']

# 2. Generate a list of percentiles from 0.00 to 0.99 (100 values)
# np.arange(start, stop, step)
percentiles = np.arange(0.0, 1.0, 0.01) 

# 1. Define which metrics need to be inverted (Lower is Better)
lower_is_better = ['Lane Agility', 'Shuttle', 'Sprint']

# 2. Temporarily make those specific columns negative in your raw data
raw_data[lower_is_better] = raw_data[lower_is_better] * -1


# 3. Calculate all percentiles at once
all_percentiles = raw_data.groupby(['Position', 'Draft'])[metrics].quantile(percentiles)

# 4. Rename the index so it makes sense (it defaults to None)
all_percentiles.index.names = ['Position', 'Draft', 'Percentile']

drafted_percentiles = raw_data.groupby([
    'Position', 
    raw_data['Draft'].replace({
        'FIRST ROUND': 'DRAFTED', 
        'LOTTERY': 'DRAFTED'
    })
])[metrics].quantile(percentiles)

drafted_percentiles.index.names = ['Position', 'Draft', 'Percentile']

participant_percentiles = raw_data.groupby(['Position'])[metrics].quantile(percentiles)

# 4. Rename the index so it makes sense (it defaults to None)
participant_percentiles.index.names = ['Position', 'Percentile']


# 4. Flip the time-based metrics back to positive numbers in your resulting dataframe
all_percentiles[lower_is_better] = all_percentiles[lower_is_better] * -1
drafted_percentiles[lower_is_better] = drafted_percentiles[lower_is_better] * -1
participant_percentiles[lower_is_better] = participant_percentiles[lower_is_better] * -1

# (Optional) Flip them back in your raw_data if you plan to continue using it in the script
raw_data[lower_is_better] = raw_data[lower_is_better] * -1

# 5. Export to CSV
all_percentiles.to_csv('complete_0_to_99_percentiles.csv')
drafted_percentiles.to_csv('drafted_0_to_99_percentiles.csv')
participant_percentiles.to_csv('participant_0_to_99_percentiles.csv')
print(all_percentiles.head(15))