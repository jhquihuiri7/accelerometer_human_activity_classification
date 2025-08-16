def get_activity_intervals(df):
    import pandas as pd

    intervals = []
    current_activity = None
    start_time = None
    
    if 'activity' not in df.columns:
        return intervals
    
    try:
        for index, row in df.iterrows():
            index = int(index)

            if pd.isna(row['activity']) or row['activity'] == 'unknown':
                if current_activity is not None and current_activity != 'unknown':
                    intervals.append({
                        'start': start_time,
                        'end': df.iloc[index-1]['t'],
                        'activity': current_activity
                    })
                current_activity = None
                start_time = None
                continue

            if current_activity is None or row['activity'] != current_activity:
                if current_activity is not None and current_activity != 'unknown':
                    intervals.append({
                        'start': start_time,
                        'end': df.iloc[index-1]['t'],
                        'activity': current_activity
                    })
                
                current_activity = row['activity']
                start_time = row['t']

        if current_activity is not None and current_activity != 'unknown':
            intervals.append({
                'start': start_time,
                'end': df.iloc[-1]['t'],
                'activity': current_activity
            })
            
    except Exception as e:
        print(f"Error processing activity intervals: {str(e)}")
        print(f"Failed at index {index}, activity: {row.get('activity')}")
    
    return intervals