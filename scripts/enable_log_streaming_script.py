from enable_log_streaming.enable_log_streaming import enable_log_streaming

environment_name = "expense-application-env"
retention_days = 7

# the enable_log_streaming is an custom-built library for enabling the logs from elastic beanstalk 


try:
    response = enable_log_streaming(environment_name, retention_days)
    print("Log streaming enabled successfully.")
    print(response)
except Exception as e:
    print("Error enabling log streaming:")
    print(e)
