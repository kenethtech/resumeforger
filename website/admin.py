from flask import Blueprint, jsonify, redirect, render_template, flash, request, url_for
from flask_jwt_extended import jwt_required
from flask_login import current_user, login_required
from .models import Subscription, User, Payment, Generation
from . import db
admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@login_required
@jwt_required()
def dashboard():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", category="error")
        return redirect(url_for('views.home'))
    return render_template('admin/dashboard.html', user=current_user)


@admin.route('/view-users')
@login_required
def view_users():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", category="error")
        return redirect(url_for('views.home'))
    users = User.query.all()
    return render_template('admin/view_users.html', user=current_user, users=users)

@admin.route('/delete-user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    if not current_user.is_admin:
        flash("You do not have permission to perform this action.", category="error")
        return redirect(url_for('views.home'))

    user = User.query.get(id)

    if user.is_admin:
        flash("You cannot delete an admin user.", category="error")
        return redirect(url_for('admin.view_users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", category="success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the user.", category="error")

    return redirect(url_for('admin.view_users'))

@admin.route('/edit-user', methods=['GET', 'POST'])
@login_required
def edit_user():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", category="error")
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        user = User.query.get_or_404(request.form.get('id'))
        if user:
            user.email = request.form.get('email')
            user.is_admin = bool(int(request.form.get('is_admin')))
            user.is_active_flag = bool(int(request.form.get('is_active')))
            db.session.commit()
            flash("User updated successfully.", category="success")
            return redirect(url_for('admin.view_users'))

    return render_template('admin/edit_user.html', user=current_user, edit_user=user)

@admin.route('/view-payments', methods=['GET'])
@login_required
def view_payments():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", category="error")
        return redirect(url_for('views.home'))
    payments = Payment.query.all()

    return render_template('admin/view_payments.html', user=current_user, payments=payments)

@admin.route('/generated-content', methods=['GET'])
@login_required
def view_generated_content():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", category="error")
        return redirect(url_for('views.home'))
    generations = Generation.query.all()

    return render_template('admin/view_generated_content.html', user=current_user, generations=generations)

@admin.route('/view-subscriptions', methods=['GET'])
@login_required
def view_subscriptions():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", category="error")
        return redirect(url_for('views.home'))
    subscriptions = Subscription.query.all()

    return render_template('admin/view_subscriptions.html', user=current_user, subscriptions=subscriptions)