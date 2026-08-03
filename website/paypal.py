import logging
from paypalserversdk.paypal_serversdk_client import PaypalServersdkClient
from paypalserversdk.configuration import Environment
from paypalserversdk.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from paypalserversdk.logging.configuration.api_logging_configuration import LoggingConfiguration
from paypalserversdk.logging.configuration.api_logging_configuration import RequestLoggingConfiguration
from paypalserversdk.logging.configuration.api_logging_configuration import ResponseLoggingConfiguration
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
import os
from dotenv import load_dotenv
import requests
load_dotenv()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10, exp_base=2),
    retry=retry_if_exception_type(requests.exceptions.RequestException)
)
def get_paypal_client():
    try:
         
        client = PaypalServersdkClient(
            client_credentials_auth_credentials= ClientCredentialsAuthCredentials(
                o_auth_client_id=os.getenv("PAYPAL_CLIENT_ID"),
                o_auth_client_secret=os.getenv("PAYPAL_CLIENT_SECRET")
            ),
            environment= Environment.SANDBOX,
            logging_configuration= LoggingConfiguration(
                log_level= logging.INFO,
                request_logging_config= RequestLoggingConfiguration(
                    log_body= True
                ),
                response_logging_config= ResponseLoggingConfiguration(
                    log_headers= True
                )
            )
        )
        return client

    except Exception as e:
        logging.error(f"Error creating PayPal client: {e}")
        raise e
    