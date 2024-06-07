def list_to_str_for_sql_queries(list):
    return str(list).replace('[', '(').replace(']', ')')
