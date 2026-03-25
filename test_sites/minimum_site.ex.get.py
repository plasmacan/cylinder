def main(response, logger):
    response.data = "hello world"
    logger.info('it worked!')
    return response
