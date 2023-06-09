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
    session,
)  # noqa: E501
import os
from dotenv import load_dotenv
from utils import (
    send_sms,
    extract_customer_numbers_from_spreadsheet,
    allowed_file,
)
from werkzeug.utils import secure_filename


# Load app settings
load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", None)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.teardown_appcontext(close_db)


@app.route("/confirm")
def confirm():
    """Confirm to the user that they are happy for the SMS messages to
    be sent"""
    try:
        if "confirm" in request.args:
            for number in session["numbers_to_contact"]:
                message_sent = send_sms(number, "Mow your lawn")
                if message_sent[0] == 500:
                    flash(message_sent[1])
                    flash("Tip: No spaces permitted in number")
                    flash(
                        "Do not use the + before the international countrycode."  # noqa: E501
                    )  # noqa: E501
                    flash(
                        "Omit the first 0 from the number. Example: 31612345678"  # noqa: E501
                    )  # noqa: E501

    except Exception() as e:
        log.error(f"Error sending SMS messages: {e}")
        return "Error sending SMS messages", 500
    return render_template("confirmation.html")


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
        file = request.files["file"]
        if "file" not in request.files or file.filename == "":
            flash("No file selected")
            return render_template("index.html")
        elif allowed_file(file.filename):
            # Save the uploaded file to the uploads folder
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            numbers_to_contact = extract_customer_numbers_from_spreadsheet(
                filename
            )  # noqa: E501

            # Store numbers to contact in session
            session["numbers_to_contact"] = numbers_to_contact

            # Redirect to confirmation before sending sms messages
            return redirect(url_for("confirm"))
        else:
            flash("The file extension is not allowed")
            return render_template("index.html")

    return render_template("index.html")


@app.route("/download/<filename>")
def download(filename=None):
    if filename is None:
        return render_template("upload.html")
    return render_template("finished.html")
