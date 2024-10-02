from datetime import date
from io import BytesIO

from itk_dev_shared_components.misc import cpr_util
import babel.dates

from docxtpl import DocxTemplate


def fill_template(context) -> BytesIO:
    doc = DocxTemplate("Bopaelsattest - Jinja skabelon.docx")
    doc.render(context)

    file = BytesIO()
    doc.save(file)
    file.seek(0)
    return file


def format_date_long(input: date) -> str:
    """Format a date as '1. januar 2015'"""
    return babel.dates.format_date(input, format="long", locale="da")


def format_date_short(input: date) -> str:
    """Format a date as '01.01.2015'"""
    if input == date(9999, 12, 31):
        return "-"
    return babel.dates.format_date(input, format="medium", locale="da")


if __name__ == '__main__':
    import os

    minimum_context = {
        "cpr": "123456-1234",
        "address_name": "John J. Johnson",
        "full_name": "John Jacob Johnson",
        "address": "Vejnavn 99, st. tv.",
        "zip_city": "9999 By N",
        "creation_date": format_date_long(date.today()),
        "birthdate": format_date_long(date(2000, 1, 1)),
        "case_number": "S1234-12345"
    }

    address_history = [
        {"from": format_date_short(date(2000, 1, 1)), "to": format_date_short(date(2001, 1, 1)), "address": "Vej 1, 1111 By"},
        {"from": format_date_short(date(2001, 1, 1)), "to": format_date_short(date(2005, 2, 3)), "address": "Vej 2, 2222 By"},
        {"from": format_date_short(date(2005, 2, 3)), "to": "", "address": "Vej 3, 3333 By"}
    ]

    name_history = [
        {"from": format_date_short(date(2000, 1, 1)), "to": format_date_short(date(2001, 1, 1)), "name": "Navn1 Navnsen1"},
        {"from": format_date_short(date(2001, 1, 1)), "to": format_date_short(date(2005, 2, 3)), "name": "Navn2 Navnsen2"},
        {"from": format_date_short(date(2005, 2, 3)), "to": "", "name": "Navn3 Navnsen3"}
    ]

    maximum_context = {
        "cpr": "123456-1234",
        "address_name": "John J. Johnson",
        "full_name": "John Jacob Johnson",
        "address": "Vejnavn 99, st. tv.",
        "zip_city": "9999 By N",
        "creation_date": format_date_long(date.today()),
        "birthdate": format_date_long(date(2000, 1, 1)),

        "citizenship": "Tyskland",
        "civil_status": "Gift",
        "cpr_kids": ", ".join(("123456-1234", "123456-1234")),

        "date_from": format_date_long(date(2000, 1, 1)),
        "date_to": format_date_long(date.today()),
        "address_history": address_history,

        "name_history": name_history,

        "case_number": "S1234-12345"
    }

    file = fill_template(minimum_context)
    with open("min output.docx", 'wb') as document:
        document.write(file.read())
    os.startfile("min output.docx")

    file = fill_template(maximum_context)
    with open("max output.docx", 'wb') as document:
        document.write(file.read())
    os.startfile("max output.docx")
