from flask import Flask, request, render_template, send_file
import pandas as pd
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./uploads"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            # Save the uploaded file to the uploads folder
            filename = file.filename
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            # Read the uploaded file into a pandas dataframe
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            df = pd.read_excel(filepath)

            # Display the dataframe in a table on the upload page
            return render_template("upload.html", table=df.to_html())

    return render_template("upload.html")


@app.route("/download/<filename>")
def download(filename):
    return send_file(filename, as_attachment=True)
