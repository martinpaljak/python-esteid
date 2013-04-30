import time
from esteid.ddoc_base import SOAPStatusError

SUPPORTED_LANGS = {
        "et" : "EST",
        "en" : "ENG",
        "ru" : "RUS",
}

def set_params(req, given_params):
    """Set request's parameters after validating the values.

    Supports Language, AdditionalDataToBeDisplayed and MessageToDisplay.
    :raise AttributeError: invalid parameter value
    """
    if "Language" in given_params:
        lang = given_params["Language"]
        try:
            req.Language = SUPPORTED_LANGS[lang]
        except KeyError:
            raise AttributeError("Language code '%s' not in '%s'"
                    % (lang, ','.join(SUPPORTED_LANGS.values())))
    if "AdditionalDataToBeDisplayed" in given_params:
        msg = given_params["AdditionalDataToBeDisplayed"]
        if len(msg) > 50:
            raise AttributeError("Messages can not be longer than "
                    "50 characters.")
        req.AdditionalDataToBeDisplayed = msg
    if "MessageToDisplay" in given_params:
        msg = given_params["MessageToDisplay"]
        if len(msg) > 40:
            raise AttributeError("MessageToDisplay can not be longer than 40 characters.")            
        req.MessageToDisplay = msg

def token_is_valid(token):
    """
    Does a basic validation of the token.
    Length should be at least 5, less than 20 and it should be numeric with
    an optional + in the beginning.
    """
    if not token or len(token) < 5 or len(token) > 20 \
            or not token[1:].isdigit()\
            or not (token[0]=='+' or token[0].isdigit()):
        return False
    return True

def is_ee_idcode(token):
    """
    No country code, only ID-code.

    Precondition: token[1:].isdigit(), token[0] == + or digit
    """
    if token[0] == '+' or not len(token) == 11:
        return False

    # A stricter alternative to the manual date range check:
    # try:
    #   datetime.datetime((1900 + int(token[1:3]) if int(token[0]) < 5
    #       else 2000 + int(token[1:3])),
    #           int(token[3:5]), int(token[5:7]))
    # except ValueError:
    #   return False
    #
    # Alas, "the concept of century was not clearly defined in the
    # relevant standard during 2000, causing some people born during
    # that year to have a 20th century prefix and others a 21st century
    # prefix in their identification code."

    if not 1 <= int(token[0]) <= 6 \
            or not 1 <= int(token[3:5]) <= 12 \
            or not 1 <= int(token[5:7]) <= 31:
        return False

    csum = sum([int(token[i]) * (i % 9 + 1)
        for i in xrange(0,10)]) % 11
    if csum == 10:
        csum = sum([int(token[i]) * ((i + 2) % 9 + 1)
            for i in xrange(0,10)]) % 11

    return int(token[10]) == csum

def normalize_phone_number(token, country_prefix="372"):
    """
    Precondition: token[1:].isdigit().
    """
    if token[0] == "+":
        return token
    if token.startswith(country_prefix):
        return "+" + token
    if token.startswith("00"):
        return "+" + token[2:]
    if token[0] == "0":
        return ''.join(("+", country_prefix, token[1:]))
    return ''.join(("+", country_prefix, token))

def _poll_until_status(where, ddoc_proxy_call, status_call,
        status_field, expected_status):
    """
    Poll DigiDoc service until expected or error status received.
    """
    # Sleep before the first call so that the user can enter the pin.
    # Two minutes total polling time, starts from end.
    poll_intervals = [10, 10, 7, 7, 7, 7, 7,
            5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 15, 20]

    while poll_intervals:
        time.sleep(poll_intervals.pop())
        ret = ddoc_proxy_call(status_call)

        statuscode = getattr(ret, status_field)
        if statuscode in ("REQUEST_OK", "OUTSTANDING_TRANSACTION"):
            continue
        elif statuscode == "MID_NOT_READY":
            # do an extra sleep
            time.sleep(5)
        elif statuscode == expected_status:
            return ret
        else:
            raise SOAPStatusError(status_call.__class__.__name__, statuscode)

    raise SOAPStatusError(where, "POLL_COUNT_EXCEEDED")
