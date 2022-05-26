{% autoescape off %}
---
title:  {{ sequence.title }}
{% with owner=sequence.owner %}{% if owner %}author: {{ owner.username }}{% endif %}{% endwith %}
{% if sequence.abstract %}abstract: |
    {{ sequence.abstract }}
{% endif %}
lang: en
dir: ltr
...
{% endautoescape %}
