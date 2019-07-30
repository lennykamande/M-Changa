import logging

from google.appengine.ext import ndb

from models.v1.mixins import AuditedModelMixin
from models.v1.project_funding import ProjectFunding

#checking if transaction is sandbox or production mode
class MyGateTransactionMode():
    TEST = 0
    LIVE = 1

    @classmethod
    def modes(cls):
        return [
            cls.TEST,
            cls.LIVE
        ]

#transaction responses from each transaction
class MyGateResponseCode():
    SUCCESSFUL = 0
    FAILED = -1
    SUCCESSFUL_WITH_WARNING = 1

    @classmethod
    def responses(cls):
        return [
            cls.SUCCESSFUL,
            cls.FAILED,
            cls.SUCCESSFUL_WITH_WARNING
        ]


class MyGatePayment(AuditedModelMixin, ndb.Model):
    # pre calling to myGate
    project_funding_key = ndb.KeyProperty(required=True, kind=ProjectFunding)
    # reference_guid = ndb.StringProperty(required=True)
    amount = ndb.FloatProperty(required=True)
    transaction_mode = ndb.IntegerProperty(required=True, choices=MyGateTransactionMode.modes())
    payment_url = ndb.StringProperty(required=True)

    # post calling to myGate
    response_received = ndb.BooleanProperty(required=True, default=False)

    # myGate response
    country_code = ndb.StringProperty()
    currency_code = ndb.StringProperty()
    merchant_reference = ndb.StringProperty()
    transaction_index = ndb.StringProperty()
    mygate_amount = ndb.FloatProperty()  # actually passed back as _AMOUNT, need to differentiate from our own amount
    payment_method = ndb.StringProperty()
    shtoken = ndb.StringProperty()
    locale = ndb.StringProperty()
    txt_acquirer_datetime = ndb.StringProperty()
    txt_price = ndb.StringProperty()
    result = ndb.IntegerProperty()
    field_names = ndb.StringProperty()
    bank_3d_status = ndb.StringProperty()  # eg 07 (actually passed back as _3DSTATUS but variable names can't start with a numeral)
    bank_error_code = ndb.StringProperty()
    bank_error_message = ndb.StringProperty()
    panhashed = ndb.StringProperty()
    card_country = ndb.StringProperty()  # eg United States
    error_code = ndb.StringProperty()
    error_message = ndb.StringProperty()
    error_source = ndb.StringProperty()
    error_detail = ndb.StringProperty()
    variable_1 = ndb.StringProperty()
    variable_2 = ndb.StringProperty()

    def safe_string(self, value):
        if not value:
            return value

        truncated = value[:500]

        if len(value) != len(truncated):
            logging.warn(u"Had to truncate the following string: {0}".format(value))

        return truncated

    def store_mygate_response(self, post_dict):
        try:
            self.response_received = True

            self.country_code = self.safe_string(post_dict.get("_COUNTRYCODE", None))
            self.currency_code = self.safe_string(post_dict.get("_CURRENCYCODE", None))
            self.merchant_reference = self.safe_string(post_dict.get("_MERCHANTREFERENCE", None))
            self.transaction_index = self.safe_string(post_dict.get("_TRANSACTIONINDEX", None))

            mygate_amount = post_dict.get("_AMOUNT", None)
            self.mygate_amount = float(mygate_amount) if mygate_amount else None

            self.payment_method = self.safe_string(post_dict.get("_PAYMETHOD", None))
            self.shtoken = self.safe_string(post_dict.get("_SHTOKEN", None))
            self.locale = self.safe_string(post_dict.get("_LOCALE", None))
            self.txt_acquirer_datetime = self.safe_string(post_dict.get("TXTACQUIRERDATETIME", None))
            self.txt_price = self.safe_string(post_dict.get("TXTPRICE", None))

            result = post_dict.get("_RESULT", None)
            self.result = int(result) if result else None

            self.field_names = self.safe_string(post_dict.get("FIELDNAMES", None))
            self.bank_3d_status = self.safe_string(post_dict.get("_3DSTATUS", None))
            self.bank_error_code = self.safe_string(post_dict.get("_BANK_ERROR_CODE", None))
            self.bank_error_message = self.safe_string(post_dict.get("_BANK_ERROR_MESSAGE", None))
            self.panhashed = self.safe_string(post_dict.get("_PANHASHED", None))
            self.card_country = self.safe_string(post_dict.get("_CARDCOUNTRY", None))
            self.error_code = self.safe_string(post_dict.get("_ERROR_CODE", None))
            self.error_message = self.safe_string(post_dict.get("_ERROR_MESSAGE", None))
            self.error_source = self.safe_string(post_dict.get("_ERROR_SOURCE", None))
            self.error_detail = self.safe_string(post_dict.get("_ERROR_DETAIL", None))

            self.variable_1 = self.safe_string(post_dict.get("VARIABLE1", None))
            self.variable_2 = self.safe_string(post_dict.get("VARIABLE2", None))
        except:  # noqa: E722
            logging.error("Could not store MyGate response")
            for k, v in post_dict.iteritems():
                logging.info(u'{0}: {1}'.format(k, v))

            raise
