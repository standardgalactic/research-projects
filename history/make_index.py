import os

html = []

html.append("""
<html>
<head>
<title>History Visualizer</title>
<style>
body{background:black;color:#00ff66;font-family:monospace;padding:20px}
img{max-width:900px;border:1px solid #00ff66}
.panel{margin-bottom:40px}
</style>
</head>
<body>
<h1>History Visualizer</h1>
""")

# scan png outputs
for root,dirs,files in os.walk("."):
    for f in files:
        if f.endswith(".png") and "frame_" not in f:
            path=os.path.join(root,f)
            html.append(f"""
<div class="panel">
<h2>{f}</h2>
<img src="{path}">
</div>
""")

html.append("</body></html>")

with open("index.html","w") as f:
    f.write("\n".join(html))
