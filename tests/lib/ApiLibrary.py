import requests
import itertools
import urllib.parse
from robot.api import logger


class ApiLibrary:
    """
    Класс содержит методы для работы с API тестируемого приложения
    """

    def __init__(self, root_api_url):
        """
        Инициализирует обьект для работы с API:
        Принимает адрес корневого эндпоинта
        Устанавливает заголовок запроса и роуты

        :param root_api_url: str
        """
        self._session = None
        self._HEADERS = {"Content-Type": "application/json"}
        self._CLIENT_SERVICES_URL = urllib.parse.urljoin(root_api_url,
                                                         "/client/services")
        self._ALL_SERVICES_URL = urllib.parse.urljoin(root_api_url,
                                                      "/services")
        self._ADD_NEW_SERVICE_URL = urllib.parse.urljoin(root_api_url,
                                                         "/client/add_service")

    def open_session(self):
        """
        Открывает сессию

        :return: None
        """
        self._session = requests.Session()

    def close_session(self):
        """
        Закрывает сессию

        :return: None
        """
        self._session.close()
        self._session = None

    def connect_service_to_client(self, client_id, service_id):
        """
        Добавляет клиенту услугу по ее id

        :param client_id: int id клиента в БД
        :param service_id: int id услуги в БД
        :return: None
        """
        json = {
            "client_id": client_id,
            "service_id": service_id,
        }

        response = self._post(self._ADD_NEW_SERVICE_URL, json)
        assert response.status_code == 202, \
            'Ошибка добавления услуги: ожидался статус 202, ' \
            'получен: {}'.format(response.status_code)

    def get_connected_services(self, client_id):
        """
        Выполняет запрос на получение услуг клиента. Возвращает список \
        подключенных клиенту услуг

        :param client_id: int id клиента в БД
        :return: List(
            Dict(
                'cost' => float
                'id' = > int
                'name' => str
            ),
        )
        """
        json = {
            "client_id": client_id,
        }

        response = self._post(self._CLIENT_SERVICES_URL, json)

        assert response.status_code == 200, \
            'Ошибка получения списка услуг: ожидался статус 200, ' \
            'получен: {}'.format(response.status_code)

        connected_services = response.json()

        return connected_services['items']

    def get_all_services(self):
        """
        Выполняет запрос на получение всех услуг в системе \
        Возвращает все услуги, в виде списка словарей

        :return: List(
            Dict(
                'id' => int,
                'name' => str,
                'cost' => float
            ),
        )
        """
        response = self._get(self._ALL_SERVICES_URL)

        assert response.status_code == 200, \
            'Ошибка получения списка услуг: ожидался статус 200, ' \
            'получен: {}'.format(response.status_code)

        all_services = response.json()
        return all_services['items']

    def check_connection_of_service(self, client_id, service_id):
        """
        Метод проверяет подключена ли переданная в аргументах услуга \
        переданному в аргументах клиенту.

        В случае отсутствия возбуждает AssertionError

        :param client_id: int id клиента в БД
        :param service_id: int id сервиса в БД
        :return: None
        """

        services = self.get_connected_services(client_id)

        assert (service_id in (service['id'] for service in services)), \
            'Невозможно найти услугу с идентификатором {} ' \
            'в списке подключенных'.format(service_id)

    @staticmethod
    def get_unconnected_service(connected_services, all_services):
        """
        Метод возвращает первый элемент, который есть в списке all_service
        и отсутствует в списке connected_service
        Возбуждает AssertionError если такой элемент не обнаружен.

        :param connected_services: list[dict] список подключенных услуг
        :param all_services: list[dict] список всех услуг
        :return: Dict(
                 'id' => int,
                 'name' => str,
                 'cost' => float
            ),
        )
        """
        try:
            unconnected_service = next(
                itertools.filterfalse(
                    lambda service: service in connected_services,
                    all_services))
            return unconnected_service

        except StopIteration:
            raise AssertionError(
                "Услуги, доступные для подключения, не найдены")

    def _post(self, url, json):
        """
        Отправляет POST запрос. Логирует данные запроса
        :param url: str
        :param json: dict
        :return: requests.models.Response
        """

        assert self._session, 'Сессия не открыта'

        response = self._session.post(url, json=json, headers=self._HEADERS)

        detail_response = "url: {url}\n\n" \
                          "request headers: {request_headers}\n\n" \
                          "request body: {request_body}\n\n" \
                          "status code: {status_code} \n\n" \
                          "response headers: {response_headers}\n\n" \
                          "response text: {response_text}".format(
                                status_code=response.status_code,
                                url=response.url,
                                response_headers=response.headers,
                                response_text=response.text,
                                request_headers=response.request.headers,
                                request_body=response.request.body
                            )

        logger.debug(detail_response)
        return response

    def _get(self, url):
        """
        Отправляет GET запрос. Логирует данные запроса
        :param url: str
        :return: requests.models.Response
        """

        assert self._session, 'Сессия не открыта'

        response = self._session.get(url, headers=self._HEADERS)
        detail_response = "url: {url} \n\n " \
                          "request headers: {request_headers}\n\n" \
                          "status code: {status_code} \n\n " \
                          "response headers: {response_headers}\n\n" \
                          "response text: {response_text}".format(
                                status_code=response.status_code,
                                url=response.url,
                                response_headers=response.headers,
                                response_text=response.text,
                                request_headers=response.request.headers,
                            )

        logger.debug(detail_response)
        return response
