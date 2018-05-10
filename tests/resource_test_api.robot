*** Settings ***
Library             lib${/}ApiLibrary.py    ${API_URL}
Library             lib${/}DbLibrary.py      ${DB_PATH}

*** Keywords ***

Setup Test Api
    ApiLibrary.Open Session
    DbLibrary.Create Connection

Teardown Test Api
    DbLibrary.Close Connection
    ApiLibrary.Close Session
