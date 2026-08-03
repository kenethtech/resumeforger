from flask_mailman import EmailMessage
import re
from collections import Counter
from flask import jsonify, render_template_string, url_for
from website.templates.auth.reset_password_template import ( reset_password_html_template )
from datetime import datetime, UTC, tzinfo
from . import db
from .models import Subscription

def extract_keywords(text):
    #Define the stop words to ignore
    stop_words = {'the', 'and', 'a', 'an', 'to', 'of', 'in', 'for', 'with', 'on', 'at', 'by', 'from', 'or', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}

    #clean and extract words
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 2]

    return Counter(keywords)


def calculate_ats_score(job_description, generated_content):
    
    if not job_description or not generated_content:
        ats_score = 65
        return ats_score
    
    job_keywords = extract_keywords(job_description)
    content_keywords = extract_keywords(generated_content)

    #top keywords from job description
    top_job_keywords = [word for word, count in job_keywords.most_common(25)]

    #calculate matches
    matched_keywords = sum(1 for kw in top_job_keywords if kw in content_keywords)
    total_important_keywords = len(top_job_keywords)

    #base score 
    keyword_match_score = (matched_keywords / max(total_important_keywords, 1)) * 60

    bonus = 0
    content_lower = generated_content.lower()

    if "experience" in content_lower and "year" in content_lower:
        bonus += 8
    
    if any(word in content_lower for word in ["led", "managed", "developed", "increased", "improved", "achieved"]):
        bonus += 12
    
    if len(generated_content.split()) > 180 and len(generated_content.split()) < 650:
        bonus += 10
    
    final_score = min(98, max(58, int(keyword_match_score + bonus)))

    return final_score

def send_reset_password_email(user):
    try:
        reset_password_url = url_for(
        'auth.request_reset_password',
        token = user.generate_reset_password_token(),
        user_id = user.id,
        _external = True
        )

        email_body = render_template_string(reset_password_html_template, reset_password_url=reset_password_url)
        message = EmailMessage(
            subject= "Reset Password",
            body=email_body,
            to= [user.email],
        )
        message.content_subtype = 'html'
        message.send()

    except Exception as e:
        return jsonify({
            "error": "Failed to send reset password instructions to your email!"
        })

def reset_credits_if_needed(user):
    now = datetime.now(UTC)
    last_reset = user.last_reset_credit

    if last_reset.tzinfo is None:
        last_reset = last_reset.replace(tzinfo=UTC)

    if user.tiers == 'free' and (now - last_reset).days >= 30:
        user.credits = 100
        user.credits_consumed = 0
        user.last_reset_credit = now

def create_user_subscription(user, plan):
    credits_plans ={
                'one-thousand-credits': 1000,
                'five-thousand-credits': 5000,
                'ten-thousand-credits': 10000
            }
    if user.subscriptions: #Delete existing subscription if any
        db.session.delete(user.subscriptions)

    new_subscription = Subscription(
        user_id=user.id,
        tier='premium',
        plan=plan,
        remaining_credits=credits_plans[plan]

    )
    db.session.add(new_subscription)


