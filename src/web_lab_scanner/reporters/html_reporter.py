from __future__ import annotations

from pathlib import Path

from jinja2 import Template

from web_lab_scanner.models import ScanResult


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Web Lab Scanner Report</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 2rem;
      color: #222;
      background: #fafafa;
    }
    h1, h2, h3 {
      margin-bottom: 0.4rem;
    }
    .meta, .summary, .finding {
      background: white;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1rem;
    }
    .finding h3 {
      margin-top: 0;
    }
    .severity {
      font-weight: bold;
    }
    .High { color: #b00020; }
    .Medium { color: #c77700; }
    .Low { color: #2f6f44; }
    .Info { color: #3366cc; }
    code {
      background: #f3f3f3;
      padding: 0.1rem 0.3rem;
      border-radius: 4px;
    }
  </style>
</head>
<body>
  <h1>Web Lab Scanner Report</h1>

  <div class="meta">
    <h2>Scan Metadata</h2>
    <p><strong>Target:</strong> {{ result.target }}</p>
    <p><strong>Pages Scanned:</strong> {{ result.pages_scanned|length }}</p>
    <p><strong>HTTP Status:</strong> {{ result.metadata.get("status_code", "N/A") }}</p>
    <p><strong>Content-Type:</strong> {{ result.metadata.get("content_type", "N/A") }}</p>
    <p><strong>Forms Detected:</strong> {{ result.metadata.get("forms_detected", 0) }}</p>
  </div>

  <div class="summary">
    <h2>Summary</h2>
    <p><strong>Total Findings:</strong> {{ result.summary.total_findings }}</p>
    <ul>
      <li>High: {{ result.summary.by_severity["High"] }}</li>
      <li>Medium: {{ result.summary.by_severity["Medium"] }}</li>
      <li>Low: {{ result.summary.by_severity["Low"] }}</li>
      <li>Info: {{ result.summary.by_severity["Info"] }}</li>
    </ul>
  </div>

  <div class="meta">
    <h2>Pages Scanned</h2>
    <ul>
      {% for page in result.pages_scanned %}
      <li><code>{{ page }}</code></li>
      {% endfor %}
    </ul>
  </div>

  <h2>Findings</h2>
  {% if result.findings %}
    {% for finding in result.findings %}
    <div class="finding">
      <h3>{{ finding.title }}</h3>
      <p><span class="severity {{ finding.severity }}">{{ finding.severity }}</span> | Confidence: {{ finding.confidence }}</p>
      <p><strong>Category:</strong> {{ finding.category }}</p>
      <p><strong>URL:</strong> <code>{{ finding.url }}</code></p>
      <p><strong>Method:</strong> {{ finding.method or "N/A" }}</p>
      <p><strong>Parameter:</strong> {{ finding.parameter or "N/A" }}</p>
      <p><strong>Evidence:</strong> {{ finding.evidence }}</p>
      <p><strong>Recommendation:</strong> {{ finding.recommendation }}</p>
    </div>
    {% endfor %}
  {% else %}
    <div class="finding">
      <p>No findings were generated.</p>
    </div>
  {% endif %}
</body>
</html>
"""


def write_html_report(result: ScanResult, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    template = Template(HTML_TEMPLATE)
    rendered = template.render(result=result)

    path.write_text(rendered, encoding="utf-8")
