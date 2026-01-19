from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from youtube_service import get_channel_id, get_channel_info

app = Flask(__name__)

DATA_DIR = "data"
TODAY_FILE = f"{DATA_DIR}/today.csv"
YESTERDAY_FILE = f"{DATA_DIR}/yesterday.csv"

os.makedirs(DATA_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    data = []
    compare = []

    if request.method == "POST":
        urls = request.form["channels"].splitlines()
        sort_by = request.form.get("sort_by")

        for url in urls:
            url = url.strip()
            if not url:
                continue

            cid = get_channel_id(url)
            if cid:
                info = get_channel_info(cid)
                if info:
                    data.append(info)

        df_today = pd.DataFrame(data)

        # ✅ SORT
        if sort_by and not df_today.empty:
            df_today = df_today.sort_values(sort_by, ascending=False)

        # ✅ QUAN TRỌNG
        data = df_today.to_dict(orient="records")

        # lưu today -> yesterday
        if os.path.exists(TODAY_FILE):
            os.replace(TODAY_FILE, YESTERDAY_FILE)

        if not df_today.empty:
            df_today.to_csv(TODAY_FILE, index=False)

        # so sánh view
        if os.path.exists(YESTERDAY_FILE) and not df_today.empty:
            df_yesterday = pd.read_csv(YESTERDAY_FILE)

            compare_df = df_today.merge(
                df_yesterday,
                on="Channel ID",
                suffixes=("_today", "_yesterday")
            )

            compare_df["View Change"] = (
                compare_df["Total Views_today"] -
                compare_df["Total Views_yesterday"]
            )

            compare = compare_df.to_dict(orient="records")

    return render_template("index.html", data=data, compare=compare)


@app.route("/export")
def export_excel():
    writer = pd.ExcelWriter("youtube_report.xlsx", engine="openpyxl")

    if os.path.exists(TODAY_FILE):
        pd.read_csv(TODAY_FILE).to_excel(writer, sheet_name="Today", index=False)

    if os.path.exists(YESTERDAY_FILE):
        pd.read_csv(YESTERDAY_FILE).to_excel(writer, sheet_name="Yesterday", index=False)

        today = pd.read_csv(TODAY_FILE)
        yesterday = pd.read_csv(YESTERDAY_FILE)

        compare = today.merge(
            yesterday,
            on="Channel ID",
            suffixes=("_today", "_yesterday")
        )

        compare["View Change"] = (
            compare["Total Views_today"] -
            compare["Total Views_yesterday"]
        )

        compare.to_excel(writer, sheet_name="Compare", index=False)

    writer.close()
    return send_file("youtube_report.xlsx", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
