import meltano.error
import logging


def do_raise(error_type, *args):
    raise error_type(*args)


def test_aggregate_default():
    aggregator = meltano.error.ExceptionAggregator(Exception)

    for i in range(0, 10):
        aggregator.call(do_raise, Exception, "Error {}".format(i))

    try:
        aggregator.raise_aggregate()
    except Exception as e:
        logging.info(str(e))


def test_aggregate_custom():
    @meltano.error.aggregate
    class CustomError(meltano.error.Error):
        pass

    aggregator = meltano.error.ExceptionAggregator(CustomError)

    for i in range(0, 10):
        aggregator.call(do_raise, CustomError, "Error {}".format(i))

    try:
        aggregator.raise_aggregate()
    except CustomError as custom:
        logging.info(str(custom))
    except meltano.error.Error as err:
        raise "Catched by the meltano.error.Error clause."
    except Exception as e:
        raise "Catched by the Exception clause."
