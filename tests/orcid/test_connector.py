import requests  # noqa: INP001


def test_api() -> None:
    # ORCID iD of the researcher
    orcid_id = "0000-0002-1597-7258"
    api_url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    access_token = "0e80a4e4-4a06-4f0a-a353-77c6fb62e1be"  # noqa: S105
    # Set headers for the request
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}

    # Make the request to ORCID API
    response = requests.get(api_url, headers=headers, timeout=5)
    assert response.status_code == 200
    if response.status_code == 200:
        orcid_data = response.json()  # noqa: F841


def test_simple_call() -> None:
    url = "https://sandbox.orcid.org/oauth/authorize?client_id=APP-Q0MJ2SJAAVUW563V&response_type=code&scope=%2Fauthenticate&redirect_uri=https:%2F%2Fwww.rki.de%2F"

    payload = {}
    headers = {
        "Cookie": "AWSELB=43655BD9169005A277CE30781A8B0A8EC55EDF15FAF4A895D4C48C69709A4303B5A780A3E0214269B310AABB09334AB147CEE82589FCEC70F7FC34893BACF19F25FB503711; AWSELBCORS=43655BD9169005A277CE30781A8B0A8EC55EDF15FAF4A895D4C48C69709A4303B5A780A3E0214269B310AABB09334AB147CEE82589FCEC70F7FC34893BACF19F25FB503711"
    }

    response = requests.request("GET", url, headers=headers, data=payload, timeout=5)
    assert response.status_code == 200
