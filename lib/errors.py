from pathlib import Path


class ValidationError(Exception):
    """Custom exception raised when a validation error occurs."""
    pass

class NotFoundError(Exception):
    """Custom exception raised when a required resource or file is not found."""
    pass

class TracebackNotifier:
    """
    A utility class for capturing and notifying tracebacks for exceptions.

    Attributes:
        error (Exception): The exception instance for which the traceback is managed.
    """

    def __init__(self, error: Exception) -> None:
        """
        Initializes the `TracebackNotifier` instance.

        Args:
            error (Exception): The exception instance to store for traceback management.
        """
        # Store the reference to the exception
        self.error = error

    def notify_traceback(self) -> None:
        """
        Walks through and prints the traceback associated with the stored exception.
        Notifies each step in the traceback chain including the file, function name,
        and line number where the exception occurred.

        On encountering any error during notification of the traceback, it attempts to
        store the new error and recursively notify its traceback.
        """
        try:
            # Retrieve the traceback object from the exception
            traceback = self.error.__traceback__

            # Walk through each step in the traceback chain
            while traceback is not None:
                # Print the current traceback step with information about file, function, and line
                print(  # noqa: T201
                    "-->",
                    Path(traceback.tb_frame.f_code.co_filename),
                    traceback.tb_frame.f_code.co_name,
                    "line code",
                    traceback.tb_lineno,
                    end="\n"
                )
                # Proceed to the next traceback step
                traceback = traceback.tb_next
        except Exception as e:
            # Store the new exception encountered during traceback notification
            self.error = e
            # Attempt to notify its traceback recursively
            self.notify_traceback()
