def enforce(expressionToTest, errorMessage):
    if not expressionToTest:
        raise Exception(errorMessage)
