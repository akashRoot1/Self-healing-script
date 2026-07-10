import random
from flask import Flask, render_template_string
app = Flask(__name__)

ACTION_VARIANTS = [
    "Print",
    "Prints",
    "Print Document",
    "Publish",
    "Submit",
    "Publish Document",
    "Save & Print",
    "Print Now",
    "Output",
    "Print Report",
]

HTML = """
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
    <title>Document Manager</title>
    <script>
      setTimeout(() => window.location.reload(), 15000);
    </script>
    <style>
      body { font-family: Arial, sans-serif; max-width: 720px; margin: 2rem auto; }
      button { padding: 0.6rem 1rem; cursor: pointer; }
      code { background: #f5f5f5; padding: 0.1rem 0.35rem; border-radius: 4px; }
    </style>
  </head>
  <body>
    <h1> Document Manager</h1>
    <p>Primary action label changes every page load to simulate unstable UI copy.</p>
    <button id=\"primary-action\" type=\"button\">{{ action_text }}</button>

    <h3>Known variants</h3>
    <ul>
      {% for item in action_variants %}
      <li><code>{{ item }}</code></li>
      {% endfor %}
    </ul>
  </body>
</html>
"""


@app.route("/")
def index():
    action_text = random.choice(ACTION_VARIANTS)
    return render_template_string(
        HTML,
        action_text=action_text,
        action_variants=ACTION_VARIANTS,
    )


if __name__ == "__main__":
    print(" Demo app starting at http://localhost:5000")
    print("   (Button text changes on every refresh + every 15s)")
    app.run(port=5000, debug=False)
