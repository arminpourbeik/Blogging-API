import traceback
from time import time

from flask import render_template, make_response
from flask_restful import Resource

from api.models.confirmation import Confirmation, ConfirmationSchema
from api.models.user import User
from api.utils.responses import response_with
from api.utils import responses as resp
from api.utils.email import MailgunException

NOT_FOUND = "Confirmation reference not found."
EXPIRED = "The link has expired."
ALREADY_CONFIRMED = "Registration has already been confirmed."
RESEND_SUCCESSFUL = "E-mail confirmation successfully re-sent"

confirmation_schema = ConfirmationSchema()


class ConfirmationResource(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        """Return confirmation HTML page."""
        confirmation = Confirmation.find_by_id(confirmation_id)

        if not confirmation:
            return response_with(resp.SERVER_ERROR_404, message=NOT_FOUND)

        if confirmation.expired:
            return response_with(resp.BAD_REQUESTS_400, message=EXPIRED)

        if confirmation.confirmed:
            return response_with(resp.BAD_REQUESTS_400, message=ALREADY_CONFIRMED)

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template(
                "email/confirmation_page.html", email=confirmation.user.email
            ),
            200,
            headers,
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        """Returns confirmations for a given user. Use for testing."""
        user = User.query.get_or_404(user_id)
        if not user:
            return response_with(resp.SERVER_ERROR_404)

        return (
            {
                "current_time": int(time()),
                "confirmation": [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(Confirmation.expire_at)
                ],
            },
            200,
        )

    @classmethod
    def post(cls, user_id: int):
        """Resent confirmation Email."""
        user = User.query.get_or_404(user_id)
        if not user:
            return response_with(resp.SERVER_ERROR_404)

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return response_with(
                        resp.BAD_REQUESTS_400, message=ALREADY_CONFIRMED
                    )
                confirmation.force_to_expire()

            new_confirmation = Confirmation(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()

            return response_with(resp.SUCCESS_201, message=RESEND_SUCCESSFUL)
        except MailgunException as e:
            return response_with(resp.SERVER_ERROR_500, message=str(e))
        except:
            traceback.print_exc()
            return response_with(resp.SERVER_ERROR_500)
