from flask import (
    Flask,
    request,
    render_template,
    send_file,
    session,
    redirect,
    url_for,
    flash,
)
import pandas as pd
import os
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", None)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged-in" not in session:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/", methods=["GET", "POST"])
def login():
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    ADMIN_USER = os.getenv("ADMIN_USER")
    if (
        request.form.get("password") == ADMIN_PASSWORD
        and request.form.get("username") == ADMIN_USER
    ):
        session["logged-in"] = True
        return render_template("index.html")
    elif (
        request.form.get("password") != ADMIN_PASSWORD
        and request.form.get("username") != ADMIN_USER
    ):
        flash("Try again")
        return render_template("/login.html")
    else:
        return render_template("/login.html")


@app.route("/upload", methods=["GET", "POST"])
@login_required
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

            # Read the uploaded file into a pandas dataframe
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            df = pd.read_excel(filepath)

            # Display the dataframe in a table on the upload page
            return render_template("upload.html", table=df.to_html())

    return render_template("upload.html")


@app.route("/download/<filename>")
@login_required
def download(filename):
    return send_file(filename, as_attachment=True)
