*** Settings ***
Documentation       Содержит тест кейс для тестирования API приложения
Resource    resource_test_api.robot

Test Setup    Setup Test Api
Test Teardown     Teardown Test Api
Test Timeout    2 min

*** Test Cases ***

Test connect of the service to the client
    [Documentation]    Проверяет подключение услуги клиенту через API

    # Получаем клиента с положительным балансом
    ${client}    DbLibrary.Get Or Create Client With Positive Balance

    # Запоминаем баланс
    ${old_balance}    set variable    ${client['client_balance']}
    ${client_id}    set variable    ${client['client_id']}

    # Получаем услуги подключенные клиенту
    ${connected_services}    ApiLibrary.Get Connected Services    ${client['client_id']}

    # Получаем все услуги
    ${all_services}    ApiLibrary.Get All Services

    # Ищем услугу, которую можно подключить
    ${available_service}    ApiLibrary.Get Unconnected Service
    ...     ${connected_services}   ${all_services}

    # Подключаем эту услугу через API
    ApiLibrary.Connect Service To Client
    ...    ${client['client_id']}    ${available_service['id']}

    # Ждем подключения услуги
    Wait Until Keyword Succeeds
        ...    1 min    5 sec    ApiLibrary.Check Connection Of Service
        ...    ${client['client_id']}    ${available_service['id']}

    # Вычисляем ожидаемый баланс
    ${expected_balance}    Evaluate    ${old_balance} - ${available_service['cost']}

    # Получаем баланс клиента
    ${new_balance}    DbLibrary.Get Client Balance    ${client_id}

    # Сравниваем баланс клиента с ожидаемым балансом
    should be equal as numbers
    ...    ${new_balance}    ${expected_balance}
