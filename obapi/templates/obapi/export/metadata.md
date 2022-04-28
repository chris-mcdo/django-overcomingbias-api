{% autoescape off %}
---
title:  {{ sequence.title }}
author: {{ sequence.owner.username }}
{% if sequence.description %}abstract: |
    {{ sequence.description }}
{% endif %}
lang: en
dir: ltr
...
{% endautoescape %}
