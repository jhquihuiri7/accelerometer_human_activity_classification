def label_activity(client, selected_timestamps, activity="unknown"):
    import pandas as pd
    from io import StringIO
    selected_timestamps = [p['x'] for p in selected_timestamps['points']]
    timestamps = pd.to_datetime(selected_timestamps).astype('int64') // 1_000_000
    blob = client.bucket("cardiocareai1.firebasestorage.app").get_blob("acc/6NX2wXNm0tbodQE5xi83jsv3R4e2_20250812_141313_UNKNOWN.csv")
    csv_data = blob.download_as_text()
    df = pd.read_csv(StringIO(csv_data))
    if "activity" not in df.columns:
        df["activity"] = "unknown"
    df.loc[df['t'].isin(timestamps), 'activity'] = activity
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")