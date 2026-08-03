from flask import Blueprint, jsonify, request
from flask_login import login_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from .paypal import get_paypal_client
from .models import User, Subscription, Payment
from . import db
from .utils import create_user_subscription

paypal_payments = Blueprint('paypal_payments', __name__)

@paypal_payments.route('/create-order/<plan>', methods=['POST'])
@jwt_required()
@login_required
def create_order(plan):
    try:
        prices = {
            'one-thousand-credits': '10',
            'five-thousand-credits': '50',
            'ten-thousand-credits': '100'
        }
        paypal_client = get_paypal_client()

        body = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "USD",
                        "value": prices[plan]
                    }
                }
            ]
        }

        response = paypal_client.orders.create_order({
            "body": body
        })

        return jsonify({
            "id": response.body.id
        }), 200
    except Exception as e:
        print(f"Error creating PayPal order: {e}")
        return jsonify({"error": str(e)}), 500


@paypal_payments.route('/capture-order', methods=['POST'])
@jwt_required()
@login_required
def capture_order():
    try:
        credits_plans ={
            'one-thousand-credits': 1000,
            'five-thousand-credits': 5000,
            'ten-thousand-credits': 10000
        }
        data = request.get_json()
        order_id = data.get('orderID')
        plan = data.get('plan')
        current_user_id = int(get_jwt_identity())

        client = get_paypal_client()

        response = client.orders.capture_order({
            "id": order_id
        })

        if response.body.status == "COMPLETED":
            capture = response.body.purchase_units[0].payments.captures[0]
            amount = capture.amount.value

            user = User.query.filter_by(id=current_user_id).first()

            payment = Payment(
                user_id=current_user_id,
                amount=amount,
                payment_method='Paypal',
                transaction_id=capture.id,
                status='completed'
            )
            db.session.add(payment)
            user.credits = (user.credits or 0) + credits_plans[plan]
            user.tiers = 'premium'
            create_user_subscription(user, plan)
            db.session.commit()

            return jsonify({
                'status': 'success'
            })

        return jsonify({
            'status': 'failed',
        })

    except Exception as e:
        print(f"Error capturing PayPal order: {e}")
        db.session.rollback()
        return jsonify({"status": "failed", "message": str(e)}), 500