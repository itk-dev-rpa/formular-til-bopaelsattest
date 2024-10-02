"""This module contains the main process of the robot."""

import os
from datetime import date

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from itk_dev_shared_components.misc import cpr_util
from itk_dev_shared_components.kmd_nova.authentication import NovaAccess
import pyodbc

from robot_framework.sub_process import word_process, database, nova_process
from robot_framework.sub_process.word_process import format_date_long, format_date_short
from robot_framework import config


def process(orchestrator_connection: OrchestratorConnection) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    conn = database.connect()

    nova_creds = orchestrator_connection.get_credential(config.NOVA_API)
    nova_access = NovaAccess(nova_creds.username, nova_creds.password)

    cpr = ''

    create_attest(
        cpr=cpr,
        citizenship=True,
        civil_status=True,
        cpr_kids=True,
        name_history=True,
        address_history_from=date(2015, 1, 1),
        conn=conn,
        nova_access=nova_access
    )


def create_attest(cpr: str, citizenship: bool, civil_status: bool, cpr_kids: bool,
                  name_history: bool, address_history_from: date,
                  conn: pyodbc.Connection, nova_access: NovaAccess):
    data = database.get_person_info(cpr, conn)
    data["cpr"] = f"{cpr[:6]}-{cpr[6:]}"

    data["birthdate"] = format_date_long(cpr_util.get_birth_date(cpr))
    data["creation_date"] = format_date_long(date.today())

    # TODO
    # nova_case = nova_process.add_case(cpr, nova_access)
    # data["case_number"] = nova_case.uuid
    data["case_number"] = "S1234-123456"

    if name_history:
        data["name_history"] = database.get_name_history(cpr, conn)

    address_history = database.get_address_history(cpr, address_history_from, conn)
    if len(address_history) > 1:
        data["address_history"] = address_history
        data["date_from"] = format_date_long(address_history_from)
        data["date_to"] = format_date_long(date.today())

    if citizenship:
        data["citizenship"] = database.get_citizenship(cpr, conn)

    if civil_status:
        data["civil_status"] = database.get_civil_status(cpr, conn)

    if cpr_kids:
        kids = database.get_kids_cpr(cpr, conn)
        data["cpr_kids"] = kids if kids else '-'

    word_file = word_process.fill_template(data)

    with open("Output.docx", "wb") as doc:
        doc.write(word_file.read())

    os.startfile("Output.docx")


if __name__ == '__main__':
    conn_string = os.getenv("OpenOrchestratorConnString")
    crypto_key = os.getenv("OpenOrchestratorKey")
    oc = OrchestratorConnection("Bopælsattest Test", conn_string, crypto_key, "")
    process(oc)
