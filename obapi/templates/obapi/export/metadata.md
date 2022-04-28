{% autoescape off %}
---
title:  {{ sequence.title }}
author: {{ sequence.owner.username }}
{% if sequence.abstract %}abstract: |
    {{ sequence.abstract }}
{% endif %}
lang: en
dir: ltr
...
{% endautoescape %}
