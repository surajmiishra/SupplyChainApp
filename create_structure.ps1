$root = "D:\SupplyChainApp"
$dirs = @("$root\templates", "$root\static\css", "$root\static\js", "$root\static\images", "$root\venv")
foreach ($d in $dirs) { New-Item -Path $d -ItemType Directory -Force | Out-Null }

# app.py
$app = @"
# filepath: d:\SupplyChainApp\app.py
from flask import Flask, render_template, request
app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        # handle uploaded vendor file here
        pass
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
"@
Set-Content -Path "$root\app.py" -Value $app -Encoding UTF8

# requirements.txt
$req = @"
# filepath: d:\SupplyChainApp\requirements.txt
Flask
SQLAlchemy
"@
Set-Content -Path "$root\requirements.txt" -Value $req -Encoding UTF8

# templates/base.html
$base = @"
<!-- filepath: d:\SupplyChainApp\templates\base.html -->
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>Supply Chain App</title>
  <link rel='stylesheet' href='/static/css/style.css'>
</head>
<body>
  <header><h1>Supply Chain App</h1></header>
  <main>
    {% block content %}{% endblock %}
  </main>
  <script src='/static/js/scripts.js'></script>
</body>
</html>
"@
Set-Content -Path "$root\templates\base.html" -Value $base -Encoding UTF8

# templates/index.html
$index = @"
<!-- filepath: d:\SupplyChainApp\templates\index.html -->
{% extends 'base.html' %}
{% block content %}
<form method='get' action='/'>
  <input name='q' placeholder='Search vendors or items'>
  <button type='submit'>Search</button>
</form>
{% endblock %}
"@
Set-Content -Path "$root\templates\index.html" -Value $index -Encoding UTF8

# templates/upload.html
$upload = @"
<!-- filepath: d:\SupplyChainApp\templates\upload.html -->
{% extends 'base.html' %}
{% block content %}
<form method='post' enctype='multipart/form-data'>
  <input type='file' name='file'>
  <button type='submit'>Upload</button>
</form>
{% endblock %}
"@
Set-Content -Path "$root\templates\upload.html" -Value $upload -Encoding UTF8

# static files
Set-Content -Path "$root\static\css\style.css" -Value "/* filepath: d:\SupplyChainApp\static\css\style.css */`nbody{font-family:Arial,Helvetica,sans-serif;}" -Encoding UTF8
Set-Content -Path "$root\static\js\scripts.js" -Value "// filepath: d:\SupplyChainApp\static\js\scripts.js`n// add JS here" -Encoding UTF8

Write-Host "SupplyChainApp structure and starter files created at $root"
