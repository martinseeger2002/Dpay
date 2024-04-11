def create_html_files(start, end):
    """
    Creates multiple HTML files with titles 'Nerd Stone #x',
    where x is a number in the specified range. Each file is
    named sequentially (e.g., NerdStone00001.html).
    """
    template = """<!DOCTYPE html>
<html>
<head>
    <title>DPAY Stone #{}</title>
        <meta charset="utf-8">
    <script type="module" src="/content/c3b478dc1b3a0fa789c65e53aebaa47bd6917a0d17384891bd694c42b1036133i0"></script>
    <style>
      model-viewer {
        position: fixed;
        width: 100%;
        height: 100%;
      }
    </style>
  </head>
  <body>
      <model-viewer src="/content/1101c9b8c3219c40ba5b63a04e4246aa0ef31457aeda689f11fc0478ece4c049i0" camera-controls="" touch-action="pan-y" auto-rotate="" ar-status="not-presenting" style="width: 100%; height: 100%;"></model-viewer>
  </body>
</html>
"""

    for i in range(start, end + 1):
        file_name = f"NerdStone{str(i).zfill(5)}.html"
        with open(file_name, "w") as file:
            file.write(template.format(i))

# Change the range here for your desired start and end
create_html_files(1, 1000)
