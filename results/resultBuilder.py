"""

"""
from abc import ABC, abstractmethod

class ResultBuilder(ABC):
    """
    Builder for constructing results from various inputs.
    The ResultBuilder can be extended to support different formats and types of results.
    """

    @classmethod
    @abstractmethod
    def build(cls, time_stamp: str, work_authorization_number: str, description: str) -> str:
        """
        Build a string representation of the results.
        The format will be:

        ## Results
        ### time_stamp
        > work_authorization_number
        description
        """
        raise NotImplementedError("The build method must be implemented by subclasses of ResultBuilder.")

    @classmethod
    @abstractmethod
    def parse(cls, full_result_str: str):
        """
        Parse a string representation of the results to extract the components.
        This method can be implemented to reverse the build process and extract the time_stamp, work_authorization_number, and description from the full_result_str.
        """
        raise NotImplementedError("The parse method must be implemented by subclasses of ResultBuilder.")
    
