def register_update_file_dropdown_callback(app, client):
    from dash import Output, Input, State
    @app.callback(
        [Output('file-selection-dropdown', 'options'),
         Output('file-selection-dropdown', 'value'),
         Output('plot-button', 'disabled'),
         Output('status-message', 'children')],
        [Input('load-files-button', 'n_clicks')],
        [State('user-id-input', 'value')],
        prevent_initial_call=True
    )
    def update_file_dropdown(n_clicks, user_id):
        if not user_id:
            return [], None, True, "Please select a User and click 'Load Files'"

        bucket_name = "cardiocareai1.firebasestorage.app"
        folder_prefix = "acc"

        try:
            blobs = client.list_blobs(bucket_name, prefix=folder_prefix)
            files_to_analyze = []

            for blob in blobs:
                if user_id in blob.name:
                    list_name = blob.name.split("_")
                    date = list_name[1]
                    time = list_name[2]
                    files_to_analyze.append({'label': f"{date[:3]}-{date[3:5]}-{date[5:]} H {time[:2]}:{time[2:4]}:{time[4:]}", 'value': blob.name})

            if not files_to_analyze:
                return [], None, True, f"No files found for user {user_id}"

            return files_to_analyze, files_to_analyze[0]['value'], False, f"Found {len(files_to_analyze)} files for user {user_id}"

        except Exception as e:
            return [], None, True, f"Error loading files: {str(e)}"
