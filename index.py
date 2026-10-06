from flask import Flask, request, redirect, url_for, render_template_string, flash
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "clean_snap_secret_key"

# =========================================================
# SETTINGS
# =========================================================

DATABASE = "clean_snap.db"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "webp", "gif"
}


# =========================================================
# DATABASE
# =========================================================

def get_db():

    db = sqlite3.connect(DATABASE)

    db.row_factory = sqlite3.Row

    return db


def create_database():

    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS complaints (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            complaint_id TEXT UNIQUE,

            name TEXT,

            mobile TEXT,

            waste_type TEXT,

            amount INTEGER,

            description TEXT,

            latitude REAL,

            longitude REAL,

            photo TEXT,

            status TEXT,

            created_at TEXT,

            updated_at TEXT

        )
    """)

    db.commit()

    db.close()


# =========================================================
# CHECK IMAGE
# =========================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# COMPLETE CSS
# =========================================================

CSS = """

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #f1f6f3;
    color: #17231c;
}


/* ================= HEADER ================= */

header {
    background: #126b3a;
    color: white;
    padding: 18px 6%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
}

header h1 {
    margin: 0;
    font-size: 27px;
}

header p {
    margin: 5px 0 0;
}

header a {
    color: white;
    text-decoration: none;
    border: 1px solid white;
    padding: 10px 15px;
    border-radius: 8px;
}

header a:hover {
    background: white;
    color: #126b3a;
}


/* ================= MAIN ================= */

main {
    max-width: 950px;
    margin: 25px auto;
    padding: 0 15px;
}


/* ================= CARD ================= */

.card {
    background: white;
    padding: 22px;
    margin-bottom: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.intro {
    border-left: 6px solid #126b3a;
}


/* ================= FORM ================= */

label {
    display: block;
    font-weight: bold;
    margin-top: 18px;
    margin-bottom: 7px;
}

input,
select,
textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #ccd7d0;
    border-radius: 8px;
    font-size: 15px;
    outline: none;
}

input:focus,
select:focus,
textarea:focus {
    border-color: #126b3a;
}

textarea {
    resize: vertical;
}


/* ================= RANGE ================= */

input[type="range"] {
    padding: 0;
}

.meter {
    height: 16px;
    width: 100%;
    background: #e2e8e4;
    border-radius: 20px;
    overflow: hidden;
    margin-top: 8px;
}

#meterFill {
    height: 100%;
    width: 40%;
    background: #e5a500;
    transition: width 0.2s;
}

.amount-text {
    color: #126b3a;
    font-weight: bold;
}


/* ================= BUTTONS ================= */

button {
    cursor: pointer;
}

.location-btn {
    background: #e6f2ea;
    color: #126b3a;
    border: none;
    padding: 12px 16px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 15px;
}

.location-btn:hover {
    background: #d5eadd;
}

.submit-btn {
    width: 100%;
    margin-top: 25px;
    padding: 15px;
    background: #126b3a;
    color: white;
    border: none;
    border-radius: 9px;
    font-size: 17px;
    font-weight: bold;
}

.submit-btn:hover {
    background: #0c512b;
}


/* ================= GPS ================= */

.two-inputs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.location-status {
    color: #126b3a;
    font-size: 14px;
}


/* ================= ALERT ================= */

.alert {
    padding: 14px;
    margin-bottom: 15px;
    border-radius: 8px;
    font-weight: bold;
}

.success {
    background: #dff5e5;
    color: #17622f;
}

.error {
    background: #fde2e2;
    color: #9a2929;
}


/* ================= COMPLAINT ================= */

.complaint {
    border: 1px solid #d9e3dc;
    padding: 15px;
    margin-top: 15px;
    border-radius: 10px;
    display: flex;
    gap: 18px;
}

.complaint-image {
    width: 160px;
    height: 120px;
    object-fit: cover;
    border-radius: 8px;
}

.complaint-details {
    flex: 1;
}

.complaint-details h3 {
    margin-top: 0;
}


/* ================= STATUS ================= */

.status {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 20px;
    background: #e5f2e9;
    color: #126b3a;
    font-size: 12px;
    margin-left: 5px;
    font-weight: bold;
}


/* ================= STATS ================= */

.stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}

.stat {
    background: white;
    padding: 20px;
    text-align: center;
    border-radius: 12px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.07);
}

.stat small {
    display: block;
    color: #647068;
}

.stat strong {
    display: block;
    font-size: 32px;
    color: #126b3a;
    margin-top: 5px;
}


/* ================= ADMIN ================= */

.admin-complaint {
    border: 1px solid #d9e3dc;
    border-radius: 10px;
    padding: 15px;
    margin-top: 15px;
    display: flex;
    gap: 18px;
}

.admin-image {
    width: 180px;
    height: 140px;
    object-fit: cover;
    border-radius: 8px;
}

.actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 15px;
}

.actions button {
    border: none;
    padding: 9px 12px;
    border-radius: 7px;
    font-weight: bold;
}

.btn-submitted {
    background: #edf1ee;
}

.btn-progress {
    background: #fff0c7;
}

.btn-resolved {
    background: #dff5e4;
    color: #17622f;
}

.btn-rejected {
    background: #fde2e2;
    color: #9a2929;
}


/* ================= DANGER ================= */

.danger {
    background: #fde2e2;
    color: #9a2929;
    border: none;
    padding: 10px 14px;
    border-radius: 8px;
    font-weight: bold;
}


/* ================= SECTION HEADER ================= */

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
}


/* ================= MAP LINK ================= */

.map-link {
    color: #126b3a;
    font-weight: bold;
    text-decoration: none;
}

.map-link:hover {
    text-decoration: underline;
}


/* ================= EMPTY ================= */

.empty {
    text-align: center;
    padding: 30px;
    color: #68736d;
}


/* ================= FOOTER ================= */

footer {
    text-align: center;
    padding: 25px;
    color: #68736d;
}


/* ================= MOBILE ================= */

@media(max-width: 650px) {

    header {
        flex-direction: column;
        align-items: flex-start;
    }

    header a {
        width: 100%;
        text-align: center;
    }

    .two-inputs {
        grid-template-columns: 1fr;
    }

    .stats {
        grid-template-columns: 1fr 1fr;
    }

    .complaint,
    .admin-complaint {
        flex-direction: column;
    }

    .complaint-image,
    .admin-image {
        width: 100%;
        height: 200px;
    }

    .section-header {
        flex-direction: column;
        align-items: flex-start;
    }

}

"""


# =========================================================
# CITIZEN PAGE HTML
# =========================================================

HOME_HTML = """

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>Clean Snap</title>

<style>

{{ css }}

</style>

</head>


<body>


<header>

<div>

<h1>🧹 Clean Snap</h1>

<p>Snap the Waste Out</p>

</div>


<a href="/admin">

🏛️ Authority Dashboard

</a>

</header>


<main>


{% with messages =
get_flashed_messages(with_categories=true) %}

{% for category, message in messages %}

<div class="alert {{ category }}">

{{ message }}

</div>

{% endfor %}

{% endwith %}


<!-- INTRO -->

<section class="card intro">

<h2>Report Garbage</h2>

<p>

Take a photo of garbage,
capture its GPS location
and send a complaint.

</p>

</section>


<!-- FORM -->

<form
class="card"
action="/submit"
method="POST"
enctype="multipart/form-data"
>


<label>

📸 Garbage Photo *

</label>


<input
type="file"
name="photo"
accept="image/*"
capture="environment"
required
>


<p>

Take a photo of the garbage.

</p>


<!-- TYPE -->

<label>

🗑️ Garbage Type

</label>


<select name="waste_type">

<option>Mixed Waste</option>

<option>Dry Waste</option>

<option>Wet Waste</option>

<option>Plastic Waste</option>

<option>Construction Waste</option>

<option>Other</option>

</select>


<!-- AMOUNT -->

<label>

📊 Garbage Amount:

<span
id="amountText"
class="amount-text"
>
40%
</span>

</label>


<input
id="amount"
type="range"
name="amount"
min="1"
max="100"
value="40"
>


<div class="meter">

<div id="meterFill"></div>

</div>


<p>

The meter represents the estimated
amount of garbage.

</p>


<!-- DESCRIPTION -->

<label>

📝 Description

</label>


<textarea
name="description"
rows="4"
placeholder="Describe the garbage problem..."
></textarea>


<!-- GPS -->

<label>

📍 GPS Location

</label>


<button
type="button"
class="location-btn"
onclick="getLocation()"
>

Get My Current Location

</button>


<p
id="locationStatus"
class="location-status"
>

Location not captured.

</p>


<div class="two-inputs">


<input
id="latitude"
name="latitude"
placeholder="Latitude"
readonly
required
>


<input
id="longitude"
name="longitude"
placeholder="Longitude"
readonly
required
>


</div>


<!-- NAME -->

<label>

👤 Your Name

</label>


<input
name="name"
placeholder="Enter your name"
required
>


<!-- MOBILE -->

<label>

📱 Mobile Number

</label>


<input
name="mobile"
type="tel"
pattern="[0-9]{10}"
placeholder="10 digit mobile number"
required
>


<!-- SUBMIT -->

<button
type="submit"
class="submit-btn"
>

🚨 Submit Garbage Complaint

</button>


</form>


<!-- COMPLAINT HISTORY -->

<section class="card">


<h2>

📋 Complaint History

</h2>


{% if complaints %}


{% for c in complaints %}


<div class="complaint">


{% if c.photo %}

<img
src="/uploads/{{ c.photo }}"
class="complaint-image"
>

{% endif %}


<div class="complaint-details">


<h3>

{{ c.complaint_id }}

<span class="status">

{{ c.status }}

</span>

</h3>


<p>

<b>Garbage Type:</b>

{{ c.waste_type }}

</p>


<p>

<b>Garbage Amount:</b>

{{ c.amount }}%

</p>


<p>

<b>Location:</b>

{{ c.latitude }},
{{ c.longitude }}

</p>


<p>

<b>Date:</b>

{{ c.created_at }}

</p>


{% if c.description %}

<p>

<b>Description:</b>

{{ c.description }}

</p>

{% endif %}


<a
class="map-link"
target="_blank"
href="https://www.google.com/maps?q={{ c.latitude }},{{ c.longitude }}"
>

🗺️ Open Location

</a>


</div>

</div>


{% endfor %}


{% else %}


<div class="empty">

No complaints submitted yet.

</div>


{% endif %}


</section>


</main>


<footer>

Clean Snap © 2026

</footer>


<script>


// ============================
// GARBAGE METER
// ============================

const amount =
document.getElementById("amount");

const amountText =
document.getElementById("amountText");

const meterFill =
document.getElementById("meterFill");


function updateMeter() {

amountText.innerText =
amount.value + "%";

meterFill.style.width =
amount.value + "%";

}


amount.addEventListener(
"input",
updateMeter
);


updateMeter();


// ============================
// GPS
// ============================

function getLocation() {


const status =
document.getElementById(
"locationStatus"
);


if (!navigator.geolocation) {

status.innerText =
"GPS is not supported.";

return;

}


status.innerText =
"Getting GPS location...";


navigator.geolocation.getCurrentPosition(

function(position) {


const latitude =
position.coords.latitude;

const longitude =
position.coords.longitude;


document.getElementById(
"latitude"
).value =
latitude.toFixed(6);


document.getElementById(
"longitude"
).value =
longitude.toFixed(6);


status.innerText =
"✓ GPS location captured";


},


function(error) {


status.innerText =
"Unable to get GPS location.";


alert(
"Please allow location permission."
);


},


{

enableHighAccuracy: true,

timeout: 10000,

maximumAge: 0

}

);


}

</script>


</body>

</html>

"""


# =========================================================
# ADMIN PAGE
# =========================================================

ADMIN_HTML = """

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>
Clean Snap Authority
</title>

<style>

{{ css }}

</style>

</head>


<body>


<header>

<div>

<h1>
🏛️ Clean Snap
</h1>

<p>
Municipal Authority Dashboard
</p>

</div>


<a href="/">
📱 Citizen App
</a>

</header>


<main>


{% with messages =
get_flashed_messages(with_categories=true) %}

{% for category, message in messages %}

<div class="alert {{ category }}">

{{ message }}

</div>

{% endfor %}

{% endwith %}


<!-- STATISTICS -->

<section class="stats">


<div class="stat">

<small>
Total Complaints
</small>

<strong>
{{ total }}
</strong>

</div>


<div class="stat">

<small>
Submitted
</small>

<strong>
{{ submitted }}
</strong>

</div>


<div class="stat">

<small>
In Progress
</small>

<strong>
{{ progress }}
</strong>

</div>


<div class="stat">

<small>
Resolved
</small>

<strong>
{{ resolved }}
</strong>

</div>


</section>


<!-- COMPLAINTS -->

<section class="card">


<div class="section-header">


<h2>
📋 Garbage Complaints
</h2>


<form
action="/clear-data"
method="POST"
onsubmit="return confirm(
'Delete all demo complaints?'
)"
>


<button
class="danger"
type="submit"
>

Clear Demo Data

</button>


</form>


</div>


{% if complaints %}


{% for c in complaints %}


<div class="admin-complaint">


{% if c.photo %}

<img
src="/uploads/{{ c.photo }}"
class="admin-image"
>

{% endif %}


<div>


<h3>

{{ c.complaint_id }}

<span class="status">

{{ c.status }}

</span>

</h3>


<p>

<b>Citizen:</b>

{{ c.name }}

</p>


<p>

<b>Mobile:</b>

{{ c.mobile }}

</p>


<p>

<b>Waste Type:</b>

{{ c.waste_type }}

</p>


<p>

<b>Garbage Amount:</b>

{{ c.amount }}%

</p>


<p>

<b>GPS:</b>

{{ c.latitude }},
{{ c.longitude }}

</p>


<p>

<b>Reported:</b>

{{ c.created_at }}

</p>


{% if c.description %}

<p>

<b>Description:</b>

{{ c.description }}

</p>

{% endif %}


<a
class="map-link"
target="_blank"
href="https://www.google.com/maps?q={{ c.latitude }},{{ c.longitude }}"
>

🗺️ Open Location in Google Maps

</a>


<!-- STATUS -->

<div class="actions">


<form
method="POST"
action="/admin/status/{{ c.id }}"
>

<input
type="hidden"
name="status"
value="Submitted"
>

<button
class="btn-submitted"
>

Submitted

</button>

</form>


<form
method="POST"
action="/admin/status/{{ c.id }}"
>

<input
type="hidden"
name="status"
value="In Progress"
>

<button
class="btn-progress"
>

In Progress

</button>

</form>


<form
method="POST"
action="/admin/status/{{ c.id }}"
>

<input
type="hidden"
name="status"
value="Resolved"
>

<button
class="btn-resolved"
>

Resolved

</button>

</form>


<form
method="POST"
action="/admin/status/{{ c.id }}"
>

<input
type="hidden"
name="status"
value="Rejected"
>

<button
class="btn-rejected"
>

Rejected

</button>

</form>


</div>


</div>

</div>


{% endfor %}


{% else %}


<div class="empty">

No complaints available.

</div>


{% endif %}


</section>


</main>


<footer>

Clean Snap Authority Dashboard

</footer>


</body>

</html>

"""


# =========================================================
# HOME ROUTE
# =========================================================

@app.route("/")
def home():

    db = get_db()

    complaints = db.execute(
        """
        SELECT *
        FROM complaints
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()


    return render_template_string(

        HOME_HTML,

        css=CSS,

        complaints=complaints

    )


# =========================================================
# SUBMIT ROUTE
# =========================================================

@app.route(
    "/submit",
    methods=["POST"]
)
def submit():


    name = request.form.get(
            "name",
            ""
        ).strip()


    mobile = request.form.get(
            "mobile",
            ""
        ).strip()


    waste_type = request.form.get(
            "waste_type",
            "Mixed Waste"
        )


    description =request.form.get(
            "description",
            ""
        ).strip()


    try:

        amount = int(
                request.form.get(
                    "amount",
                    40
                )
            )

        latitude = float(
                request.form.get(
                    "latitude"
                )
            )

        longitude =float(
                request.form.get(
                    "longitude"
                )
            )

    except:

        flash(
            "Please capture GPS location.",
            "error"
        )

        return redirect("/")


    if not mobile.isdigit() or len(mobile) != 10:

        flash(
            "Enter a valid 10 digit mobile number.",
            "error"
        )

        return redirect("/")


    photo = request.files.get(
            "photo"
        )


    filename = None


    if photo and photo.filename:


        if not allowed_file(
            photo.filename
        ):

            flash(
                "Invalid image format.",
                "error"
            )

            return redirect("/")


        original = secure_filename(
                photo.filename
            )


        filename = (
            datetime.now().strftime(
                "%Y%m%d%H%M%S%f"
            )
            + "_"
            + original
        )


        photo.save(
            os.path.join(
                UPLOAD_FOLDER,
                filename
            )
        )


    complaint_id ="CS-" + datetime.now().strftime(
            "%Y%m%d%H%M%S%f"
        )[-10:]


    created =datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


    db = get_db()


    db.execute(
        """
        INSERT INTO complaints

        (
            complaint_id,
            name,
            mobile,
            waste_type,
            amount,
            description,
            latitude,
            longitude,
            photo,
            status,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """,

        (
            complaint_id,
            name,
            mobile,
            waste_type,
            amount,
            description,
            latitude,
            longitude,
            filename,
            "Submitted",
            created
        )
    )


    db.commit()

    db.close()


    flash(
        "Complaint submitted! ID: "
        + complaint_id,
        "success"
    )


    return redirect("/")


# =========================================================
# ADMIN
# =========================================================

@app.route("/admin")
def admin():


    db = get_db()


    complaints = db.execute(
            """
            SELECT *
            FROM complaints
            ORDER BY id DESC
            """
        ).fetchall()


    db.close()


    total = len(complaints)


    submitted = sum(
            c["status"] == "Submitted"
            for c in complaints
        )


    progress = sum(
            c["status"] == "In Progress"
            for c in complaints
        )


    resolved = sum(
            c["status"] == "Resolved"
            for c in complaints
        )


    return render_template_string(

        ADMIN_HTML,

        css=CSS,

        complaints=complaints,

        total=total,

        submitted=submitted,

        progress=progress,

        resolved=resolved

    )


# =========================================================
# UPDATE STATUS
# =========================================================

@app.route(
    "/admin/status/<int:id>",
    methods=["POST"]
)
def update_status(id):


    status = request.form.get(
            "status"
        )


    allowed = {

        "Submitted",

        "In Progress",

        "Resolved",

        "Rejected"

    }


    if status not in allowed:

        flash(
            "Invalid status.",
            "error"
        )

        return redirect("/admin")


    db = get_db()


    db.execute(

        """
        UPDATE complaints

        SET
            status = ?,
            updated_at = ?

        WHERE id = ?

        """,

        (

            status,

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            id

        )

    )


    db.commit()

    db.close()


    flash(
        "Complaint status updated.",
        "success"
    )


    return redirect("/admin")


# =========================================================
# UPLOADS
# =========================================================

@app.route(
    "/uploads/<filename>"
)
def uploads(filename):

    return app.send_static_file(
        filename
    )


# =========================================================
# CLEAR DATA
# =========================================================

@app.route(
    "/clear-data",
    methods=["POST"]
)
def clear_data():


    db = get_db()


    photos = db.execute(
            "SELECT photo FROM complaints"
        ).fetchall()


    for photo in photos:


        if photo["photo"]:


            path = os.path.join(
                    UPLOAD_FOLDER,
                    photo["photo"]
                )


            if os.path.exists(path):

                os.remove(path)


    db.execute(
        "DELETE FROM complaints"
    )


    db.commit()

    db.close()


    flash(
        "All demo data deleted.",
        "success"
    )


    return redirect("/admin")


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    create_database()

    print()
    print("====================================")
    print("        CLEAN SNAP PROJECT")
    print("====================================")
    print()
    print("Citizen App:")
    print("http://127.0.0.1:5000")
    print()
    print("Authority Dashboard:")
    print("http://127.0.0.1:5000/admin")
    print()

    app.run(
        debug=True
    )
