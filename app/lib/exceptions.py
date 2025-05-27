FILE_VERSION = "0.1.1"

class HoyoHelperError(Exception):
    def __init__(self, message, *args):
        """
        The function is a constructor that initializes an object with a message attribute.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param message ()  - The `__init__` method you provided is a constructor for a class. It takes
        a `message` parameter and any additional arguments passed as `*args`. The
        `super().__init__(message, *args)` line is calling the constructor of the superclass (parent
        class) with the `message
        
        .-.-.-.
        
        
        """
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        """
        The `__str__` function in Python returns the message attribute of the object when it is
        converted to a string.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `__str__` method is returning the `message` attribute of the object.
        
        .-.-.-.
        
        
        """
        return self.message


class WebhookError(HoyoHelperError):
    def __init__(self, message, url: str = None, original_exception: Exception = None, *args):
        """
        This Python function initializes an object with a message, URL, and original exception.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param message ()  - The `message` parameter is a required argument that represents the error
        message or description that you want to associate with the exception. It is typically a string
        that provides information about the error that occurred.
        
        .-.-.-.
        
        @ param url (str)  - The `url` parameter in the `__init__` method is a string type parameter
        that represents the URL associated with the exception. It is an optional parameter with a
        default value of `None`, which means it can be provided when creating an instance of the class
        but is not required.
        
        .-.-.-.
        
        @ param original_exception (Exception)  - The `original_exception` parameter in the `__init__`
        method is used to store the original exception that occurred before this custom exception was
        raised. This can be helpful for debugging purposes as it allows you to track the chain of
        exceptions that led to the current one.
        
        .-.-.-.
        
        
        """
        super().__init__(message, *args)
        self.url = url
        self.original_exception = original_exception

    def __str__(self):
        """
        The function `__str__` returns a formatted error message including the error message, URL
        (truncated), and original exception details.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `__str__` method is returning a formatted string that includes the error message,
        truncated URL if available, and information about the original exception (its type and a
        truncated string representation).
        
        .-.-.-.
        
        
        """
        msg = f"WebhookError: {self.message}"
        if self.url:
            msg += f" (URL: {self.url[:20]}...)"
        if self.original_exception:
            msg += f" | Original: {type(self.original_exception).__name__}: {str(self.original_exception)[:50]}..."
        return msg


class LoginManagerError(HoyoHelperError):
    pass


class APIRequestError(LoginManagerError):
    def __init__(self, message, url: str = None, status_code: int = None, response_text: str = None, original_exception: Exception = None, *args):
        """
        This Python function initializes an object with message, URL, status code, response text, and
        original exception attributes.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param message ()  - The `message` parameter is a string that represents the error message or
        description for the exception being raised. It is a required parameter for initializing this
        custom exception class.
        
        .-.-.-.
        
        @ param url (str)  - The `url` parameter in the `__init__` method is a string that represents
        the URL associated with the message. It is an optional parameter with a default value of `None`,
        which means it can be provided when creating an instance of the class but is not required.
        
        .-.-.-.
        
        @ param status_code (int)  - The `status_code` parameter in the `__init__` method is used to
        store the HTTP status code of a response. It is an integer value that represents the status of
        the HTTP request made to a particular URL.
        
        .-.-.-.
        
        @ param response_text (str)  - The `response_text` parameter in the `__init__` method is used to
        store the text of the response received from a request. This can be useful for debugging or
        displaying the response content in case of an error or for further processing in your code.
        
        .-.-.-.
        
        @ param original_exception (Exception)  - The `original_exception` parameter in the `__init__`
        method is used to store the original exception that occurred. This can be helpful for debugging
        and understanding the root cause of the error that led to the creation of the current exception
        object. Storing the original exception allows you to trace back the
        
        .-.-.-.
        
        
        """
        super().__init__(message, *args)
        self.url = url
        self.status_code = status_code
        self.response_text = response_text
        self.original_exception = original_exception

    def __str__(self):
        """
        The function `__str__` returns a formatted string representation of an APIRequestError object.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `__str__` method is returning a formatted string that includes information about
        an API request error object. It includes the error message, URL, status code, partial response
        text, and the type of the original exception. The information is joined together with a pipe
        character (|) and returned as a single string.
        
        .-.-.-.
        
        
        """
        parts = [f"APIRequestError: {self.message}"]
        if self.url: parts.append(f"URL: {self.url}")
        if self.status_code: parts.append(f"Status: {self.status_code}")
        if self.response_text: parts.append(f"Response (partial): {self.response_text[:100]}")
        if self.original_exception: parts.append(f"Original: {type(self.original_exception).__name__}")
        return " | ".join(parts)


class APIDataError(LoginManagerError):
    def __init__(self, message, key_missing: str = None, retcode: int = None, api_message: str = None, api_response_preview: str = None, *args):
        """
        This Python function initializes attributes for a custom exception class with optional
        parameters.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param message ()  - The `message` parameter is a required argument that represents the main
        message or description of the exception being raised. It is passed to the parent class
        constructor as the main message.
        
        .-.-.-.
        
        @ param key_missing (str)  - The `key_missing` parameter in the `__init__` method is a string
        parameter that represents a key that is missing in a data structure or object. It can be used to
        provide additional information about the missing key when handling errors or exceptions related
        to missing keys.
        
        .-.-.-.
        
        @ param retcode (int)  - The `retcode` parameter in the `__init__` method is used to store an
        integer value that represents a return code. This return code can be used to indicate the status
        or outcome of an operation or function call. It can help in identifying whether the operation
        was successful or if there was
        
        .-.-.-.
        
        @ param api_message (str)  - The `api_message` parameter in the `__init__` method is used to
        store a message related to an API response. This message could provide additional information or
        context about the response received from an API.
        
        .-.-.-.
        
        @ param api_response_preview (str)  - The `api_response_preview` parameter in the `__init__`
        method is used to store a preview of the API response. This can be helpful for debugging or
        displaying a concise summary of the API response data.
        
        .-.-.-.
        
        
        """
        super().__init__(message, *args)
        self.key_missing = key_missing
        self.retcode = retcode
        self.api_message = api_message
        self.api_response_preview = api_response_preview

    def __str__(self):
        """
        The function `__str__` returns a formatted string representation of an `APIDataError` object.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `__str__` method is returning a formatted string that includes information about
        an `APIDataError` object. The returned string includes the error message, any missing key,
        return code, API message, and a preview of the API response. Each piece of information is
        separated by a pipe character `|`.
        
        .-.-.-.
        
        
        """
        parts = [f"APIDataError: {self.message}"]
        if self.key_missing: parts.append(f"Missing Key: {self.key_missing}")
        if self.retcode is not None: parts.append(f"Retcode: {self.retcode}")
        if self.api_message: parts.append(f"API Msg: {self.api_message}")
        if self.api_response_preview: parts.append(f"Response Preview: {self.api_response_preview[:100]}")
        return " | ".join(parts)


class AssetFetchError(LoginManagerError):
    def __init__(self, message, url: str = None, original_exception: Exception = None, *args):
        """
        This Python function initializes an object with a message, URL, and original exception.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param message ()  - The `message` parameter is a required argument that represents the error
        message or description associated with the exception being raised. It is a string that provides
        information about the error that occurred.
        
        .-.-.-.
        
        @ param url (str)  - The `url` parameter in the `__init__` method is a string type parameter
        that represents the URL associated with the exception. It is an optional parameter with a
        default value of `None`, which means it can be provided when creating an instance of the class
        but is not required.
        
        .-.-.-.
        
        @ param original_exception (Exception)  - The `original_exception` parameter in the `__init__`
        method is used to store the original exception that occurred. This can be helpful for debugging
        purposes as it allows you to track the original exception that led to the creation of the
        current exception instance.
        
        .-.-.-.
        
        
        """
        super().__init__(message, *args)
        self.url = url
        self.original_exception = original_exception

    def __str__(self):
        """
        The function `__str__` returns a formatted error message including the message, URL, and
        original exception type.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `__str__` method is returning a formatted string that includes the error message,
        URL (if available), and the type of the original exception (if available).
        
        .-.-.-.
        
        
        """
        msg = f"AssetFetchError: {self.message}"
        if self.url: msg += f" (URL: {self.url})"
        if self.original_exception: msg += f" | Original: {type(self.original_exception).__name__}"
        return msg


class CardGenerationError(LoginManagerError):
    pass


class SigninError(LoginManagerError):
    def __init__(self, message, retcode: int = None, api_message: str = None, gt_risk_code: int = None, *args):
        """
        This Python function initializes an object with message, return code, API message, and GT risk
        code attributes.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param message ()  - The `message` parameter is a required argument that represents the main
        message or description of the exception being raised. It is passed to the parent class's
        `__init__` method to handle the main message of the exception.
        
        .-.-.-.
        
        @ param retcode (int)  - The `retcode` parameter in the `__init__` method is an optional integer
        parameter that represents a return code. It is used to indicate the status or outcome of a
        particular operation or function. In the context of the code snippet you provided, `retcode` is
        initialized with a default
        
        .-.-.-.
        
        @ param api_message (str)  - The `api_message` parameter in the `__init__` method is a string
        that represents a message related to an API response or interaction. It can be used to provide
        additional information or context about the API operation that triggered the exception.
        
        .-.-.-.
        
        @ param gt_risk_code (int)  - The `gt_risk_code` parameter in the `__init__` method is used to
        store an integer value representing a risk code related to a specific message or operation. It
        is an optional parameter with a default value of `None`, which means it can be provided when
        initializing an instance of the
        
        .-.-.-.
        
        
        """
        super().__init__(message, *args)
        self.retcode = retcode
        self.api_message = api_message
        self.gt_risk_code = gt_risk_code

    def __str__(self):
        """
        The function `__str__` returns a formatted string representation of an object with specific
        attributes.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns The `__str__` method is returning a formatted string that includes the error message,
        return code, API message, and GT risk code (if available), separated by pipes (|).
        
        .-.-.-.
        
        
        """
        parts = [f"SigninError: {self.message}"]
        if self.retcode is not None: parts.append(f"Retcode: {self.retcode}")
        if self.api_message: parts.append(f"API Msg: {self.api_message}")
        if self.gt_risk_code is not None: parts.append(f"GT Risk Code: {self.gt_risk_code}")
        return " | ".join(parts)