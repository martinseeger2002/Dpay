import base64

def create_html_files(start, end):
    """
    Creates multiple HTML files numbered from 'start' to 'end'.
    Each file's title and other content are dynamically generated to include its sequence number.
    Files are named in the format 'dpaystoneXXXXX.html', where 'XXXXX' is a zero-padded number.
    """
    template = """<!DOCTYPE html>
<html>
<head>
    <title>DPAY Stone #{0}</title>
    <meta charset="utf-8">
    <script type="module" src="/content/c3b478dc1b3a0fa789c65e53aebaa47bd6917a0d17384891bd694c42b1036133i0"></script>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden; /* Prevents scroll bars */
        }}
        model-viewer {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #000000; /* Adjusted for clarity */
        }}
    </style>
    <script>
      window.onload = function() {{
        var encodedText = '{1}';
        var decodedText = atob(encodedText);  // Decode the Base64 text
        document.getElementById('hidden-content').innerHTML = decodedText;  // Display the decoded text in the div
      }};
    </script>
</head>
<body>
    <model-viewer src="/content/1101c9b8c3219c40ba5b63a04e4246aa0ef31457aeda689f11fc0478ece4c049i0" camera-controls="" touch-action="pan-y" auto-rotate="" ar-status="not-presenting" style="width: 100%; height: 100%;"></model-viewer>
    <div id="hidden-content"></div>  <!-- Content will be filled by JavaScript -->
</body>
</html>
"""
    encoded_message = base64.b64encode('Hello World! MUCH WOW FROM @DOGEPAY_DRC20 AND @GREATAPE42069E MUCH ENJOY! SUCH FREE AIRDROP!'.encode()).decode()
    
    for i in range(start, end + 1):
        file_name = f"dpaystone{str(i).zfill(5)}.html"  # Generates a filename with a zero-padded sequence number
        with open(file_name, "w") as file:
            file.write(template.format(i, encoded_message))  # Writes the template to the file with the current number replacing {0} and the encoded message

# Example call that creates files from dpaystone00001.html to dpaystone00002.html
create_html_files(1, 1500)
