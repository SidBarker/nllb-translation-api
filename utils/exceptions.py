class TranslationError(Exception):
    """Exception raised for errors in translation process."""
    def __init__(self, message="Error during translation process"):
        self.message = message
        super().__init__(self.message)


class UnsupportedLanguageError(Exception):
    """Exception raised when language is not supported."""
    def __init__(self, language_code=""):
        self.message = f"Language '{language_code}' is not supported"
        super().__init__(self.message)


class ModelLoadingError(Exception):
    """Exception raised when model fails to load."""
    def __init__(self, message="Failed to load translation model"):
        self.message = message
        super().__init__(self.message) 