def label_activity(client, selected_timestamps, activity="unknown", selected_file=None):
    import pandas as pd
    from io import StringIO
    selected_timestamps = [p['x'] for p in selected_timestamps['points']]
    timestamps = pd.to_datetime(selected_timestamps).astype('int64') // 1_000_000
    blob = client.bucket("cardiocareai1.firebasestorage.app").get_blob(selected_file)
    csv_data = blob.download_as_text()
    df = pd.read_csv(StringIO(csv_data))
    if "activity" not in df.columns:
        df["activity"] = "unknown"
    df.loc[df['t'].isin(timestamps), 'activity'] = activity
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")
    return df