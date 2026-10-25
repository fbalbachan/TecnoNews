# -*- coding: utf-8 -*-
from datetime import timedelta

import wikipedia

# Wikimedia rejects generic clients (HTTP 429/403) and asks bots for a descriptive User-Agent with contact
# information: https://meta.wikimedia.org/wiki/User-Agent_policy. Override it with [wikipedia] user_agent.
DEFAULT_USER_AGENT = "TecnoNews/1.0 (Spanish news analysis)"


def configure():
    user_agent = DEFAULT_USER_AGENT
    try:
        from src.utils.configProvider import ConfigProvider
        user_agent = ConfigProvider().get("wikipedia", "user_agent")
    except Exception:
        pass
    wikipedia.set_user_agent(user_agent)
    # bursts of searches get HTTP 429 (an HTML body the library fails to parse as JSON)
    wikipedia.set_rate_limiting(True, min_wait=timedelta(milliseconds=500))


configure()
