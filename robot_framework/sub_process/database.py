from datetime import date

import pyodbc

from robot_framework.sub_process.word_process import format_date_short
from robot_framework import config


def connect() -> pyodbc.Connection:
    return pyodbc.connect(config.DATABASE_CONN_STRING)


def get_person_info(cpr: str, connection: pyodbc.Connection) -> dict[str, str]:
    """Get basic personal info from database.

    Args:
        cpr: The cpr number to look up.

    Returns:
        A dict containing: Address name, Full name, Address, Zip and city
    """
    result = connection.execute(
        """
        SELECT Adresseringsnavn, Borgerligtnavn, Adresseringsadresse, PostnummerOgBy
        FROM DWH.Mart.AdresseAktuel
        WHERE CPR = ?
        """,
        cpr).fetchone()

    return {
        "address_name": result[0],
        "full_name": result[1],
        "address": result[2],
        "zip_city": result[3]
    }


def get_address_history(cpr: str, date_from: date, connection: pyodbc.Connection) -> list[dict[str, str]]:
    cursor = connection.execute(
        """
        SELECT DISTINCT
            fh.DatoTilflyt, fh.DatoFraflyt,
            ah.Vejnavn, ah.HusNr, ah.Etage, ah.Side, ah.Postnummer, ah.Postdistrikt
        FROM DWH.dwh.Flyttehistorik as fh
        JOIN DWH.Mart.AdresseHistorik as ah
            on fh.Adressenoegle = ah.Adressenoegle AND fh.CPR = ah.cpr
        WHERE
            fh.cpr = ? AND
            fh.DatoFraFlyt > ?
        ORDER BY fh.DatoTilflyt DESC
        """,
        cpr,
        date_from
    )

    address_history = []
    for row in cursor:
        address_history.append(
            {
                "from": format_date_short(row[0]),
                "to": format_date_short(row[1]),
                "address": _format_address(*row[2:])
            }
        )

    return address_history


def _format_address(road: str, number: str, floor: str, side: str, zip: str, city: str) -> str:
    address = f"{road} {number.lstrip("0")}, "

    if floor:
        address += f"{floor.lstrip("0").lower()}. "

    if side:
        address += f"{side.lstrip("0").lower()}, "

    address += f"{zip} {city}"
    return address


def get_name_history(cpr: str, conn: pyodbc.Connection) -> list[dict[str, str]]:
    result = conn.execute(
        """
        SELECT
        Fornavn, Mellemnavn, Efternavn, GyldigFra, GyldigTil
        FROM DWH.dwh.BorgerDim
        WHERE cpr = ?
        ORDER BY GyldigFra DESC
        """,
        cpr
    )

    # Convert to dicts
    dict_list = []
    for row in result:
        dict_list.append(
            {
                "from": _convert_stupid_date(row[3]),
                "to": _convert_stupid_date(row[4]),
                "name": " ".join(row[:3])
            }
        )

    # Merge identical names next to each other
    name_history = [dict_list[0]]
    for d in dict_list[1:]:
        if d["name"] == name_history[-1]["name"]:
            name_history[-1]["from"] = d["from"]
        else:
            name_history.append(d)

    return name_history


def _convert_stupid_date(input: int) -> str:
    """Convert an integer date in the format yyyymmdd
    to a nicely formatted date string.

    Args:
        input: A stupid integer date

    Returns:
        A nice date string.
    """
    s = str(input)
    d = date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    return format_date_short(d)


def get_citizenship(cpr: str, conn: pyodbc.Connection) -> str:
    return conn.execute("SELECT statsborgerskab FROM DWH.Mart.AdresseAktuel WHERE cpr = ?", cpr).fetchval()


def get_civil_status(cpr: str, conn: pyodbc.Connection) -> str:
    return conn.execute("SELECT civilstand FROM DWH.Mart.AdresseAktuel WHERE cpr = ?", cpr).fetchval()


def get_kids_cpr(cpr: str, conn: pyodbc.Connection) -> str:
    cursor = conn.execute(
        """
        SELECT child.cpr
        FROM DWH.Mart.AdresseAktuel as parent
        JOIN DWH.Mart.AdresseAktuel as child ON
            (child.MorCPR = parent.cpr or child.FarCPR = parent.cpr)
        WHERE
            parent.cpr = ?
            AND parent.Adressenoegle = child.Adressenoegle
        """,
        cpr
    )

    cpr_list = []
    for row in cursor:
        cpr = row[0]
        cpr_list.append(f"{cpr[:6]}-{cpr[6:]}")
    return ", ".join(cpr_list)


if __name__ == '__main__':
    cpr = ''
    ah = get_kids_cpr(cpr, connect())

    for a in ah:
        print(a)
