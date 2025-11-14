from jinja2 import Environment, BaseLoader, StrictUndefined
import markdown

env = Environment(loader=BaseLoader(), autoescape=True, undefined=StrictUndefined)

def render_email(subject_tmpl: str, body_md_tmpl: str, context: dict):
    subj = env.from_string(subject_tmpl).render(**context)
    body_md = env.from_string(body_md_tmpl).render(**context)
    html = markdown.markdown(body_md, extensions=["extra"])
    html += '<hr style="opacity:.2"><div style="font-size:12px;color:#777">If this was a mistake, reply STOP.</div>'
    return subj, html
