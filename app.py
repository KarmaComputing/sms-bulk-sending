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
from utils import send_sms, extract_customer_numbers_from_spreadsheet, allowed_file
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", None)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if "file" not in request.files or file.filename == "":
            flash("No file selected")
            return render_template("index.html")
        elif allowed_file(file.filename):
            # Save the uploaded file to the uploads folder
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            numbers_to_contact = extract_customer_numbers_from_spreadsheet(filename)
            for number in numbers_to_contact:
                message_sent = send_sms(number, "Mow your lawn")
                if message_sent[0] == 500:
                    flash(message_sent[1])
                    flash(
                        "Tip: Receiver number of the SMS message. No spaces, do not use the + before the international countrycode. Omit the first 0 from the number. Example: 31612345678"
                    )
                    return render_template("index.html")
            return redirect(url_for("download", filename=filename))
        else:
            flash("The file extension is not allowed")
            return render_template("index.html")

    return render_template("index.html")


@app.route("/download/<filename>")
def download(filename=None):
    if filename is None:
        return render_template("upload.html")
    return render_template("finished.html")
