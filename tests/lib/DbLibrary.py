import sqlite3
from robot.api import logger


def check_connection(f):
    """
    Декоратор проверяет создано ли соединение с базой данных,
    перед выполнением запроса
    """

    def _check_connection(instance, *args, **kwargs):
        if not instance._connection:
            raise ConnectionError("Не установлено соединение с базой данных")
        else:
            return f(instance, *args, **kwargs)

    return _check_connection


class DbLibrary:
    """
    Класс содержит методы для работы с базой данных тестируемого приложения
    """
    _DEFAULT_NEW_USER_DATA = {
        'client_name': 'Foma Bezrukov',
        'client_balance': 5.0
    }

    def __init__(self, db_path):
        """
        Инициализирует обьект для работы с БД
        В качестве входящего параметра принимает путь к фалу БД sqlite

        :param db_path: str
        """
        self._db_path = db_path
        self._connection = None
        self._cursor = None

    def create_connection(self):
        """
        Создает соединение с БД
        :return: None
        """
        self._connection = sqlite3.connect(self._db_path)
        self._cursor = self._connection.cursor()

    def close_connection(self):
        """
        Закрывает соединение с БД
        :return: None
        """
        self._cursor.close()
        self._connection.close()
        self._cursor = None
        self._connection = None

    @check_connection
    def get_or_create_client_with_positive_balance(self):
        """
        Метод возвращает клиента, подходящего под условия: \
            баланс клиента положительный,\
            у клиента есть услуга доступная для подключения \

        В случае если клиент не найден в базе данных, \
        метод создает нового клиента, подходящего под условия

        :return: Dict(
            'clinet_id' => int,
            'name' => str,
            'balance' => float
        )
        """

        sql_query = (
            "SELECT CLIENTS.CLIENT_ID, CLIENTS.CLIENT_NAME, BALANCES.BALANCE"
            " FROM CLIENTS"
            " INNER JOIN BALANCES ON CLIENTS_CLIENT_ID = CLIENTS.CLIENT_ID"
            " WHERE BALANCES.BALANCE > 0 AND"
            "  (SELECT count(*) "
            "   FROM  CLIENT_SERVICE CS"
            "   WHERE CS.CLIENTS_CLIENT_ID = CLIENTS.CLIENT_ID)"
            "     < (SELECT count(*)  FROM  SERVICES)"
            " LIMIT 1"
        )

        self._cursor.execute(sql_query)
        result = self._cursor.fetchone()

        if result:
            client = {
                "client_id": result[0],
                "client_name": result[1],
                "client_balance": result[2],
            }
            return client

        else:
            logger.warn(
                "Клиент с положительным балансом и доступными "
                "для подключения услугами не найден")

            return self.create_client_with_positive_balance(
                self._DEFAULT_NEW_USER_DATA['client_name'],
                self._DEFAULT_NEW_USER_DATA['client_balance'])

    @check_connection
    def get_client_balance(self, client_id):
        """
        Метод возвращает баланс клиента с идентификатором client_id

        :param client_id: int идентификатор клиента
        :return: float баланс клиента
        """
        sql_query = (
            "SELECT BALANCE"
            " FROM BALANCES"
            " WHERE CLIENTS_CLIENT_ID = (?)"
        )

        self._cursor.execute(sql_query, (client_id,))
        result = self._cursor.fetchone()

        assert result, 'Не удалось найти баланс ' \
                       'клиента с идентификатором {}'.format(client_id)

        return result[0]

    @check_connection
    def create_client_with_positive_balance(self, name, balance):
        """
        Метод создает нового пользователя в БД. Возвращает словарь, содержащий \
        информацию о созданном пользователе.

        :param name: str имя создаваемого пользователя, например: 'Foma Sumkov'
        :param balance: float баланс создаваемого пользователя: например 5.0
        :return: Dict(
            'clinet_id' => int,
            'client_name' => str,
            'client_balance' => float
        )
        """
        sql_query_new_client = "INSERT INTO CLIENTS(CLIENT_NAME) VALUES (?)"
        self._cursor.execute(sql_query_new_client, (name,))
        client_id = self._cursor.lastrowid

        sql_query_balance = "INSERT INTO BALANCES(CLIENTS_CLIENT_ID, BALANCE)" \
                            "VALUES(?, ?)"

        self._cursor.execute(sql_query_balance, (client_id, balance,))
        self._connection.commit()

        logger.debug(
            "Создан клиент, подходяший под условия: {} - {}".format(client_id,
                                                                   name))

        client = {
            "client_id": client_id,
            "client_name": name,
            "client_balance": balance,
        }

        return client
