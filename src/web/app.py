from db import get_db, close_db
import sqlalchemy
from logger import log
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
from utils import send_sms, extract_customer_numbers_from_spreadsheet


# Load app settings
load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", None)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.teardown_appcontext(close_db)


@app.route("/health")
def health():
    """check health of app by
    - checking for valid (working) database connection
    - The 200 http response can also be used as a health indicator
    """
    log.info("Checking /health")
    db = get_db()
    health = "BAD"
    try:
        result = db.execute("SELECT NOW()")
        result = result.one()
        health = "OK"
        log.info(
            f"/health reported OK including database connection: {result}"
        )  # noqa: E501
    except sqlalchemy.exc.OperationalError as e:
        msg = f"sqlalchemy.exc.OperationalError: {e}"
        log.error(msg)
    except Exception as e:
        msg = f"Error performing healthcheck: {e}"
        log.error(msg)

    return health


@app.route("/", methods=["GET", "POST"])
def index():
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
            numbers_to_contact = extract_customer_numbers_from_spreadsheet(
                filename
            )  # noqa: E501
            for number in numbers_to_contact:
                send_sms(number, "Mow your lawn")
            return redirect(url_for("download", filename=filename))

    return render_template("index.html")


@app.route("/download/<filename>")
def download(filename=None):
    if filename is None:
        return render_template("upload.html")
    return render_template("finished.html")
