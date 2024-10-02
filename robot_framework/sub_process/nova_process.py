import uuid
from datetime import datetime

from itk_dev_shared_components.kmd_nova import nova_cases
from itk_dev_shared_components.kmd_nova import cpr as nova_cpr
from itk_dev_shared_components.kmd_nova.authentication import NovaAccess
from itk_dev_shared_components.kmd_nova.nova_objects import NovaCase, CaseParty, Caseworker, Department


def add_case(cpr: str, nova_access: NovaAccess) -> NovaCase:
    """Add a case and a task to KMD Nova on the given person.

    Args:
        candidate: The person to add the case to.
        nova_access: The NovaAccess object used to authenticate.
    """
    party = CaseParty(
        role="Primær",
        identification_type="CprNummer",
        identification=cpr,
        name="Testbruger Et"  # TODO: nova_cpr.get_address_by_cpr(cpr, nova_access)['name']
    )

    caseworker = Caseworker(  # TODO: Correct caseworker
        name='Rpabruger Rpa16 - MÅ IKKE SLETTES',
        ident='AZRPA16',
        uuid='02b35232-9fc4-4e95-aab7-fa9d0e1910cc'
    )

    department = Department(
        id=70403,
        name="Folkeregister og Sygesikring",
        user_key="4BFOLKEREG"
    )

    security_unit = Department(
        id=818485,
        name="Borgerservice",
        user_key="4BBORGER"
    )

    case = NovaCase(
        uuid=str(uuid.uuid4()),
        title=f"Bopælsattest {datetime.now().strftime("%d/%m/%Y")}",
        case_date=datetime.now(),
        progress_state="Opstaaet",
        case_parties=[party],
        kle_number="23.05.03",
        proceeding_facet="G01",
        sensitivity="Fortrolige",
        caseworker=caseworker,
        responsible_department=department,
        security_unit=security_unit,
    )

    # task = Task(
    #     uuid=str(uuid.uuid4()),
    #     title="Udrejsekontrol",
    #     description=description,
    #     caseworker=caseworker,
    #     status_code="N",
    #     deadline=None
    # )

    nova_cases.add_case(case, nova_access)
    # nova_tasks.attach_task_to_case(case.uuid, task, nova_access)

    # Get case back to populate case number
    case = nova_cases.get_case(case.uuid, nova_access)
    return case
