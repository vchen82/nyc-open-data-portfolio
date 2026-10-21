{% macro text_type() %}{{ 'string' if target.type == 'bigquery' else 'varchar' }}{% endmacro %}
{% macro safe_cast(expression, kind) -%}
  {{ 'safe_cast' if target.type == 'bigquery' else 'try_cast' }}({{ expression }} as {{ kind }})
{%- endmacro %}
{% macro norm(expression) -%}
  nullif(upper(trim({{ expression }})), '')
{%- endmacro %}
{% macro zip_code(expression) -%}
  case when {{ 'regexp_contains' if target.type == 'bigquery' else 'regexp_full_match' }}(trim({{ expression }}), '^[0-9]{5}$')
    then trim({{ expression }}) end
{%- endmacro %}
{% macro key(columns) -%}
  {% if target.type == 'bigquery' %}to_hex({% endif %}md5(concat(
  {% for c in columns %}
    case when {{ c }} is null then '-1:' else concat(cast(length(cast({{ c }} as {{ text_type() }})) as {{ text_type() }}), ':', cast({{ c }} as {{ text_type() }})) end{% if not loop.last %}, {% endif %}
  {% endfor %}
  )){% if target.type == 'bigquery' %}){% endif %}
{%- endmacro %}
{% macro date_part(part, expression) -%}cast(extract({{ part }} from {{ expression }}) as integer){%- endmacro %}
{% macro ratio(numerator, denominator) -%}
  1.0 * ({{ numerator }}) / nullif(({{ denominator }}), 0)
{%- endmacro %}
