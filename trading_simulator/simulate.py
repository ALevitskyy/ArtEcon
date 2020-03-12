from flask import (
    Blueprint,
    url_for,
    redirect,
    render_template,
    session,
    request,
    send_file,
    request,
    flash,
)
from flask_wtf import Form
from flask_wtf.file import FileField
from wtforms.validators import NumberRange
from wtforms import StringField, SelectField, IntegerField, DecimalField
from wtforms.widgets import TextInput
from wtforms_components import DateTimeField, DateRange
from models import db, Post, Tag
from datetime import datetime
from flask.json import jsonify
from werkzeug import secure_filename
import json
import pandas as pd
import re
import sys
import pickle
import string
import os
import random
import tempfile

DATA_PATH = "https://s3.us-east-2.amazonaws.com/artecon/cur_data/curdata_"


def get_tags():
    tags_query = db.engine.execute(
        "Select Count(tag_id),tag_title from Tag group by tag_title order by Count(tag_id) desc limit 8"
    )
    return [i[1] for i in tags_query]


COMMISIONS = {
    "AUDUSD": 0.00025,
    "EURCHF": 0.0003,
    "EURGBP": 0.00025,
    "EURJPY": 0.032,
    "EURUSD": 0.00019,
    "GBPUSD": 0.00024,
    "NZDUSD": 0.0003,
    "USDCAD": 0.0003,
    "USDCHF": 0.00025,
    "USDJPY": 0.02,
}
CURR_CODES = [
    ("0", "AUDUSD"),
    ("1", "EURCHF"),
    ("2", "EURGBP"),
    ("3", "EURJPY"),
    ("4", "EURUSD"),
    ("5", "GBPUSD"),
    ("6", "NZDUSD"),
    ("7", "USDCAD"),
    ("8", "USDCHF"),
    ("9", "USDJPY"),
]
CANDLE_TYPES = [
    ("5M", "5M"),
    ("30M", "30M"),
    ("1H", "1H"),
    ("4H", "4H"),
    ("8H", "8H"),
    ("1D", "1D"),
]
LEVERAGES = [
    ("1", "x1"),
    ("5", "x5"),
    ("20", "x20"),
    ("50", "x50"),
    ("100", "x100"),
    ("200", "x200"),
    ("400", "x400"),
]
BUY_SELL = [("BUY", "BUY"), ("SELL", "SELL")]


class InitForm(Form):
    init_cash = IntegerField(
        "Initial Cash",
        default=200,
        validators=[
            NumberRange(min=1, message="The field only accepts positive integer values")
        ],
    )
    leverage = SelectField("Leverage", choices=LEVERAGES)
    lot_size = IntegerField(
        "Lot Size",
        default=10000,
        validators=[
            NumberRange(min=1, message="The field only accepts positive integer values")
        ],
    )
    date_time = DateTimeField(
        "Start Date",
        validators=[DateRange(min=datetime(2015, 1, 1), max=datetime(2018, 6, 29))],
    )


class MakeDealForm(Form):
    currency2 = SelectField("Currency", choices=CURR_CODES)
    lot_number = DecimalField(
        "Number of lots",
        default=1,
        validators=[
            NumberRange(
                min=0.00000001, message="The field only accepts positive values"
            )
        ],
    )
    buy_sell = SelectField("BUY/SELL", choices=BUY_SELL)


class CloseDealForm(Form):
    id = StringField("id")


class CandleRequestForm(Form):
    date_time = DateTimeField(
        "Start Date",
        default=pd.to_datetime("2016-01-01 09:00:00"),
        validators=[DateRange(min=datetime(2015, 1, 1), max=datetime(2018, 6, 29))],
    )
    currency = SelectField("Currency", choices=CURR_CODES)
    candle_type = SelectField("Candle", choices=CANDLE_TYPES)
    candle_number = IntegerField(
        "Number of candles",
        default=300,
        validators=[
            NumberRange(min=1, message="The field only accepts positive integer values")
        ],
    )
    skipped_candles = IntegerField("Candles already skipped", default=0)


class SeshLoadForm(Form):
    sesh_file = FileField("File")


simulate = Blueprint("simulator", __name__, template_folder="templates")


def get_current_price(currency):
    skipping = session["skip_date"]
    date = session["start_date"]
    index = pd.read_pickle("index.pkl")
    index = index.index.get_loc(pd.to_datetime(date), method="nearest")
    if index + skipping >= 260884:
        raise ValueError("Not enough data on server")
    index = int(currency) * 260885 + index
    index += skipping

    file_number = int(index / 2500) * 2500
    leftover = index % 2500
    pandas_params = dict(
        index_col=0,
        names=["coin", "high", "low", "open", "close"],
        skiprows=leftover,
        header=0,
        nrows=2,
    )
    pandas_params["skiprows"] = leftover - 2
    data = pd.read_csv(DATA_PATH + str(file_number) + ".csv", **pandas_params)
    init_price = data.close[1]
    data["date"] = data.index
    date = data.date[1]
    return (init_price, date)


def get_total_cash():
    session["total_cash"] = 0
    session["total_cash"] += session["init_cash"]
    for i in session["log"]:
        session["total_cash"] += i["profit"]


def get_free_margin():
    session["free_cash"] = 0
    session["free_cash"] += session["init_cash"]
    for i in session["log"]:
        session["free_cash"] += i["profit"]
        if i["status"] == "Active":
            session["free_cash"] -= (
                i["size"] * session["lot_size"] / session["leverage"]
            )


def calculate_deal_profit(log_record):
    if log_record["order"] == "BUY":
        difference = (
            log_record["current_price"]
            - log_record["initial_price"]
            - COMMISIONS[log_record["currency"]]
        ) / log_record["current_price"]
    else:
        difference = (
            log_record["initial_price"]
            - log_record["current_price"]
            - COMMISIONS[log_record["currency"]]
        ) / log_record["current_price"]
    profit = session["lot_size"] * log_record["size"] * difference
    return profit


@simulate.route("/getData", methods=["POST"])
def getData():
    form = CandleRequestForm()
    if form.validate_on_submit():
        currency = form.currency.data
        date = form.date_time.data
        type = form.candle_type.data
        candle_type = form.candle_type.data
        number = int(form.candle_number.data)
        if candle_type == "30M":
            number = number * 6
        elif candle_type == "1H":
            number = number * 12
        elif candle_type == "4H":
            number = number * 12 * 4
        elif candle_type == "8H":
            number = number * 12 * 4 * 2
        elif candle_type == "1D":
            number = number * 12 * 24
        skipping = int(form.skipped_candles.data)
        index = pd.read_pickle("index.pkl")
        index = index.index.get_loc(pd.to_datetime(date), method="nearest")
        if index < number:
            return jsonify(
                errorrs="There is not enough historical data in database to process your request. The records in database starts on 1st of January 2015, and there is no data prior"
            )
        if index + skipping >= 260884:
            return jsonify(
                errorrs="There is no data in the database past the current date of simulation, so you would not be able to continue simulation"
            )
        index = int(currency) * 260885 + index
        index += skipping

        file_number = int(index / 2500) * 2500
        leftover = index % 2500
        pandas_params = dict(
            index_col=0,
            names=["coin", "high", "low", "open", "close"],
            skiprows=0,
            header=0,
            nrows=leftover,
        )
        if leftover < number:
            data = pd.read_csv(DATA_PATH + str(file_number) + ".csv", **pandas_params)
        else:
            pandas_params["nrows"] = number
            pandas_params["skiprows"] = leftover - number
            data = pd.read_csv(DATA_PATH + str(file_number) + ".csv", **pandas_params)
        candles_left = number - leftover
        while candles_left > 2500:
            pandas_params["nrows"] = 2500
            file_number -= 2500
            data2 = pd.read_csv(DATA_PATH + str(file_number) + ".csv", **pandas_params)

            data = pd.concat([data2, data])
            candles_left -= 2500
        if candles_left > 0:
            pandas_params["skiprows"] = 2500 - candles_left
            pandas_params["nrows"] = candles_left
            file_number -= 2500
            data2 = pd.read_csv(DATA_PATH + str(file_number) + ".csv", **pandas_params)
            data = pd.concat([data2, data])
        data["date"] = data.index
        resample_dict = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "date": "first",
        }
        data.index = pd.to_datetime(data.index)
        if candle_type == "30M":
            data = data.resample("30T").agg(resample_dict)
        elif candle_type == "1H":
            data = data.resample("1H").agg(resample_dict)
        elif candle_type == "4H":
            data = data.resample("4H").agg(resample_dict)
        elif candle_type == "8H":
            data = data.resample("8H").agg(resample_dict)
        elif candle_type == "1D":
            data = data.resample("24H").agg(resample_dict)
        data = data.dropna(axis=0, how="any")
        chart_data = data.to_dict(orient="records")
        return jsonify(chart_data)
    return jsonify(errorrs=form.errors)


@simulate.route("/init_session", methods=["POST"])
def initiate_session():
    init_form = InitForm()
    if init_form.validate_on_submit():
        session["init_cash"] = int(init_form.init_cash.data)
        session["free_cash"] = int(init_form.init_cash.data)
        session["total_cash"] = int(init_form.init_cash.data)
        session["leverage"] = int(init_form.leverage.data)
        session["lot_size"] = int(init_form.lot_size.data)
        session["start_date"] = init_form.date_time.data
        session["skip_date"] = 0
        session["log"] = []
        return jsonify(total_cash=session["total_cash"], free_cash=session["free_cash"])
    return jsonify(errorrs=init_form.errors)


@simulate.route("/buy_sell", methods=["POST"])
def make_deal():
    make_deal_form = MakeDealForm()
    if make_deal_form.validate_on_submit():
        try:
            if float(make_deal_form.lot_number.data) < 0:
                jsonify(errorrs="Lot size must be a positive number")
        except:
            jsonify(errorrs="Lot size must be a positive number")
        try:
            init_price, date = get_current_price(make_deal_form.currency2.data)
        except Exception as e:
            print(e)
            return jsonify(
                errorrs="Not enough historical data to statisfy your request"
            )
        if (
            float(make_deal_form.lot_number.data)
            * session["lot_size"]
            / session["leverage"]
            > session["free_cash"]
        ):
            return jsonify(
                errorrs="You don`t have enough free margin to commence the operation"
            )
        deal_dict = dict(
            id=len(session["log"]),
            currency=[
                i[1] for i in CURR_CODES if i[0] == make_deal_form.currency2.data
            ][0],
            size=float(make_deal_form.lot_number.data),
            order=make_deal_form.buy_sell.data,
            initial_price=init_price,
            current_price=init_price,
            start_date=date,
            close_date=date,
            status="Active",
        )
        deal_dict["profit"] = calculate_deal_profit(deal_dict)
        session["log"].append(deal_dict)
        get_total_cash()
        get_free_margin()
        session.modified = True
        return jsonify(
            log=session["log"],
            total_cash=session["total_cash"],
            free_cash=session["free_cash"],
        )
    return jsonify(errorrs=make_deal_form.errors)


@simulate.route("/close_deal", methods=["POST"])
def close_deal():
    close_deal_form = CloseDealForm()
    if close_deal_form.validate_on_submit():
        try:
            index = [i["id"] for i in session["log"]].index(
                int(close_deal_form.id.data)
            )
            if session["log"][index]["status"] == "Closed":
                return jsonify(errorrs="Invalid ID was selected")
            session["log"][index]["status"] = "Closed"
            get_total_cash()
            get_free_margin()
            session.modified = True
            return jsonify(
                log=session["log"],
                total_cash=session["total_cash"],
                free_cash=session["free_cash"],
            )
        except:
            return jsonify(errorrs="Invalid ID was selected")
    return jsonify(errorrs=close_deal_form.errors)


@simulate.route("/skip_frame", methods=["POST"])
def skip_date():
    try:
        skip_step = request.data.decode("UTF-8")
        skip_step = int(re.sub("[^0-9]", "", skip_step))
        if skip_step <= 0:
            raise ValueError("Skip step must be bigger than 0")
    except:
        return jsonify(errorrs="Number of skipped steps must be a postive integer")
    if "log" in session:
        session["skip_date"] += skip_step
        for i in session["log"]:
            if i["status"] == "Active":
                try:
                    i["current_price"], i["close_date"] = get_current_price(
                        [z[0] for z in CURR_CODES if z[1] == i["currency"]][0]
                    )
                except:
                    return jsonify(
                        errorrs="Your skip step request exceeeds the historical data available."
                    )
                i["profit"] = calculate_deal_profit(i)
        get_total_cash()
        get_free_margin()
        # margin call
        if session["free_cash"] < 0:
            for i in session["log"]:
                if i["status"] == "Active":
                    i["status"] == "Closed"
            get_total_cash()
            get_free_margin()
            return jsonify(
                log=session["log"],
                total_cash=session["total_cash"],
                free_cash=session["free_cash"],
                margin_call="SHIT",
            )
        session.modified = True
        return jsonify(
            log=session["log"],
            total_cash=session["total_cash"],
            free_cash=session["free_cash"],
        )
    return "skipped"


@simulate.route("/save_sesh", methods=["GET", "POST"])
def save_sesh():
    try:
        save_dict = dict()
        save_dict["init_cash"] = session["init_cash"]
        save_dict["free_cash"] = session["free_cash"]
        save_dict["total_cash"] = session["total_cash"]
        save_dict["leverage"] = session["leverage"]
        save_dict["lot_size"] = session["lot_size"]
        save_dict["start_date"] = session["start_date"]
        save_dict["skip_date"] = session["skip_date"]
        save_dict["log"] = session["log"]
        with tempfile.NamedTemporaryFile() as handle:
            pickle.dump(save_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
            handle.flush()
            return send_file(handle.name)
    except:
        return "No active game session to save"


@simulate.route("/load_sesh", methods=["POST"])
def load_sesh():
    if request.method == "POST":
        # check if the post request has the file part
        print(request.files)
        if "file" not in request.files:
            return jsonify(errorrs="No Session File Specified")
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            return jsonify(errorrs="No Session File Specified")
        if file:
            filename = secure_filename(file.filename)
            file.save(filename)
            with open(filename, "rb") as handle:
                save_dict = pickle.load(handle)
            os.remove(filename)
            session["init_cash"] = save_dict["init_cash"]
            session["free_cash"] = save_dict["free_cash"]
            session["total_cash"] = save_dict["total_cash"]
            session["leverage"] = save_dict["leverage"]
            session["lot_size"] = save_dict["lot_size"]
            session["start_date"] = save_dict["start_date"]
            session["skip_date"] = save_dict["skip_date"]
            session["log"] = save_dict["log"]
            return jsonify(
                log=session["log"],
                total_cash=session["total_cash"],
                free_cash=session["free_cash"],
                start_date=str(session["start_date"]),
                skipping=session["skip_date"],
            )


@simulate.route("/", methods=["GET", "POST"])
def simulator():
    session.clear()
    form = CandleRequestForm()
    init_form = InitForm()
    make_deal_form = MakeDealForm()
    close_deal_form = CloseDealForm()
    sesh_load_form = SeshLoadForm()
    return render_template(
        "simulator.html",
        tags=get_tags(),
        form=form,
        init_form=init_form,
        make_deal_form=make_deal_form,
        close_deal_form=close_deal_form,
        sesh_load_form=sesh_load_form,
    )
