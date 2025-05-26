FILE_VERSION = "0.1.0"

class HoyoHelperError(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        return self.message


class WebhookError(HoyoHelperError):
    def __init__(self, message, url: str = None, original_exception: Exception = None, *args):
        super().__init__(message, *args)
        self.url = url
        self.original_exception = original_exception

    def __str__(self):
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
        super().__init__(message, *args)
        self.url = url
        self.status_code = status_code
        self.response_text = response_text
        self.original_exception = original_exception

    def __str__(self):
        parts = [f"APIRequestError: {self.message}"]
        if self.url: parts.append(f"URL: {self.url}")
        if self.status_code: parts.append(f"Status: {self.status_code}")
        if self.response_text: parts.append(f"Response (partial): {self.response_text[:100]}")
        if self.original_exception: parts.append(f"Original: {type(self.original_exception).__name__}")
        return " | ".join(parts)


class APIDataError(LoginManagerError):
    def __init__(self, message, key_missing: str = None, retcode: int = None, api_message: str = None, api_response_preview: str = None, *args):
        super().__init__(message, *args)
        self.key_missing = key_missing
        self.retcode = retcode
        self.api_message = api_message
        self.api_response_preview = api_response_preview

    def __str__(self):
        parts = [f"APIDataError: {self.message}"]
        if self.key_missing: parts.append(f"Missing Key: {self.key_missing}")
        if self.retcode is not None: parts.append(f"Retcode: {self.retcode}")
        if self.api_message: parts.append(f"API Msg: {self.api_message}")
        if self.api_response_preview: parts.append(f"Response Preview: {self.api_response_preview[:100]}")
        return " | ".join(parts)


class AssetFetchError(LoginManagerError):
    """Raised when fetching an asset (e.g., image, font) fails."""
    def __init__(self, message, url: str = None, original_exception: Exception = None, *args):
        super().__init__(message, *args)
        self.url = url
        self.original_exception = original_exception

    def __str__(self):
        msg = f"AssetFetchError: {self.message}"
        if self.url: msg += f" (URL: {self.url})"
        if self.original_exception: msg += f" | Original: {type(self.original_exception).__name__}"
        return msg


class CardGenerationError(LoginManagerError):
    pass


class SigninError(LoginManagerError):
    def __init__(self, message, retcode: int = None, api_message: str = None, gt_risk_code: int = None, *args):
        super().__init__(message, *args)
        self.retcode = retcode
        self.api_message = api_message
        self.gt_risk_code = gt_risk_code

    def __str__(self):
        parts = [f"SigninError: {self.message}"]
        if self.retcode is not None: parts.append(f"Retcode: {self.retcode}")
        if self.api_message: parts.append(f"API Msg: {self.api_message}")
        if self.gt_risk_code is not None: parts.append(f"GT Risk Code: {self.gt_risk_code}")
        return " | ".join(parts)