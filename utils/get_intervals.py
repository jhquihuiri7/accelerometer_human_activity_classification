def get_activity_intervals(df):
    intervals = []
    current_activity = None
    start_time = None
    
    for index, row in df.iterrows():
        if current_activity is None or row['activity'] != current_activity:
            if current_activity is not None and current_activity != 'unknown':
                intervals.append({
                    'start': start_time,  # Already datetime
                    'end': df.iloc[index-1]['t'],  # Already datetime
                    'activity': current_activity
                })
            
            current_activity = row['activity']
            start_time = row['t']
        
        if index == len(df) - 1 and current_activity != 'unknown':
            intervals.append({
                'start': start_time,
                'end': row['t'],
                'activity': current_activity
            })
    
    return intervals