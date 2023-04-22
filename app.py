from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    flash,
)
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", None)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected")
            return render_template("index.html")
        file = request.files["file"]
        if file.filename == "":
            flash("No file selected")
            return render_template("index.html")
        else:
            # Save the uploaded file to the uploads folder
            filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            send_sms(filename)
            return redirect(url_for("download", filename=filename))

    return render_template("index.html")


def send_sms(filename=None):
    if filename is None:
        return render_template("upload.html")
    try:
        subprocess.run(
            "python3 extract.py",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    # WIP trying to catch in case of an error doing the script run"
    except subprocess.CalledProcessError as e:
        print(e)
        return render_template("error.html")
    except Exception as e:
        print(e)
        return render_template("error.html")


@app.route("/download/<filename>")
def download(filename=None):
    if filename is None:
        return render_template("upload.html")
    return render_template("finished.html")
