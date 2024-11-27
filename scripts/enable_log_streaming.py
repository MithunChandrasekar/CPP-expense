from enable_log_streaming.enable_log_streaming import enable_log_streaming

# Replace with your environment name
environment_name = "expense-application-env"
retention_days = 7  # Set the retention period

try:
    response = enable_log_streaming(environment_name, retention_days)
    print("Log streaming enabled successfully.")
    print(response)
except Exception as e:
    print("Error enabling log streaming:")
    print(e)