from __future__ import annotations

import json
from typing import Any


def _payload_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True).lower()


def is_spam_like_outreach(payload: dict[str, Any]) -> bool:
    text = _payload_text(payload)
    blocked_terms = [
        "mass blast",
        "mass email",
        "bulk send",
        "spam",
        "fake familiarity",
        "fake testimonial",
        "scrape",
        "scraped",
        "10000",
        "10,000",
    ]
    return any(term in text for term in blocked_terms)


def is_regulated_revenue_request(payload: dict[str, Any]) -> bool:
    text = _payload_text(payload)
    blocked_terms = [
        "tax filing",
        "avoid tax",
        "legal interpretation",
        "investment return",
        "securities",
        "accounting advice",
        "tax advice",
        "legal advice",
    ]
    return any(term in text for term in blocked_terms)


def safe_outreach_result() -> dict[str, Any]:
    return {
        "warning": "This request appears to involve spam-like outreach. I can help create a low-volume personalized outreach plan instead.",
        "safe_alternative": {
            "plan": [
                "Identify a small list of relevant prospects with legitimate business context.",
                "Personalize each message using public, truthful context.",
                "Ask for a low-friction conversation and stop after respectful follow-up.",
            ],
            "human_approval_required": True,
        },
        "cold_email": {
            "subject": "Relevant workflow idea",
            "body": "Hi, I noticed a possible operational bottleneck that may be relevant to your team. If useful, I can share a short, specific workflow audit. Would a brief conversation make sense?",
        },
        "linkedin_dm": "I may have a relevant workflow observation for your team. Open to a brief, low-pressure conversation?",
        "wechat_dm": "你好，我可以帮你做一个低频、个性化的流程体检建议。所有外联内容都需要人工确认后再发送。",
        "x_dm": "I may have a relevant workflow note for your team. Worth a short conversation?",
        "follow_up_1": "Following up once. If this is not relevant, no worries.",
        "follow_up_2": "Last note from me. Happy to leave it here if now is not a fit.",
        "soft_cta": "Would it be useful to review a short personalized audit?",
        "objection_responses": [
            {
                "objection": "Not interested",
                "response": "Understood. I will not keep following up. Wishing you well.",
            }
        ],
        "referral_request": "Is there one person for whom a respectful workflow audit would be genuinely useful?",
        "content_posts": [
            {
                "platform": "LinkedIn",
                "post": "Outbound works best when it is low-volume, truthful, and useful before it asks.",
                "cta": "Share this with someone reviewing their outreach process.",
            },
            {
                "platform": "X",
                "post": "A good cold message should be easy to say no to.",
                "cta": "Keep outreach human-approved.",
            },
            {
                "platform": "WeChat",
                "post": "好的客户触达不是群发，而是真实、具体、克制的沟通。",
                "cta": "先人工确认，再发送。",
            },
        ],
        "human_approval_required": True,
    }
