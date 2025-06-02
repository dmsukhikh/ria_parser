from w3lib.url import url_query_cleaner
from scrapy.dupefilters import RFPDupeFilter
from scrapy.utils.request import fingerprint


class CustomRequestFingerprinter:
    def fingerprint(self, request):
        new_request = request.replace(url=url_query_cleaner(request.url))
        return fingerprint(new_request)


class CustomDupeFilter(RFPDupeFilter):
    """Custom dupefilter for preventing parsing same urls but with different
    search query parameters"""

    def __init__(self, path=None, debug=False, *, fingerprinter=None):
        super().__init__(
            path=path, debug=debug, fingerprinter=CustomRequestFingerprinter())
        
