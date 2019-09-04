import warnings

# disable the psycopg2 warning
# this needs to run before `psycopg2` is imported
warnings.filterwarnings("ignore", category=UserWarning, module="psycopg2")


bind = ["0.0.0.0:5000"]
workers = 4
timeout = 600
