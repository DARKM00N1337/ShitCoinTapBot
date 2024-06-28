import asyncio
from random import randint
from urllib.parse import unquote
import json
import os
import sys
import psutil
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import base64
import aiohttp
from aiohttp_proxy import ProxyConnector, ProxyType
from better_proxy import Proxy
from bot.config import settings
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers
from .agents import generate_random_user_agent

class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.is_tapping = False
        self.click_counter = 0
        self.random_clicks_threshold = randint(a=settings.CLICKS_FOR_SLEEP[0], b=settings.CLICKS_FOR_SLEEP[1])
        self.tasks_checked = False
        self.proxy = None

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            self.proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=self.proxy.protocol,
                hostname=self.proxy.host,
                port=self.proxy.port,
                username=self.proxy.login,
                password=self.proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            with_tg = True

            if not self.tg_client.is_connected:
                with_tg = False
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            bot = await self.tg_client.resolve_peer('ShitCoinTap_Bot')
            app = InputBotAppShortName(bot_id=bot, short_name="Game")
            web_view = await self.tg_client.invoke(RequestAppWebView(
                peer=bot,
                app=app,
                platform='android',
                write_allowed=True
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

            if with_tg is False:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)

    async def connect(self, user_id: int, init_data: str):
        init_data_base64 = base64.b64encode(init_data.encode()).decode()
        url = f"wss://cmonkey.vip/api/users/{user_id}/actions?init-data={init_data_base64}"
        user_agent = generate_random_user_agent(device_type='android', browser_type='chrome')

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'ru,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Host': 'cmonkey.vip',
            'Origin': 'https://sexyzbot.pxlvrs.io',
            'Referer': 'https://cmonkey.vip/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            "User-Agent": user_agent
        }

        proxy = None
        if self.proxy:
            proxy = f"http://{self.proxy.host}:{self.proxy.port}"
            proxy_auth = aiohttp.BasicAuth(self.proxy.login, self.proxy.password)
        else:
            proxy_auth = None

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                url,
                headers=headers,
                proxy=proxy,
                proxy_auth=proxy_auth
            ) as websocket:
                await self.send_message(websocket)
                await self.listen(websocket, init_data_base64)

    async def reconnect(self, user_id: int, init_data: str):
        await asyncio.sleep(90)
        await self.connect(user_id, init_data)

    async def listen(self, websocket, init_data_base64: str):
        try:
            async for message in websocket:
                await self.handle_message(message, websocket, init_data_base64)
        except aiohttp.WSServerHandshakeError as e:
            logger.error(f"{self.session_name} | Disconnected. ERROR: {e}")

    async def send_minigame(self, websocket):
        message = {"type": "minigame", "success": True, "result": 3500}
        await websocket.send_json(message)

    async def send_message(self, websocket):
        if not websocket.closed:
            message = {"type": "game", "click": 1}
            await websocket.send_json(message)
            self.click_counter += 1
            if self.click_counter >= self.random_clicks_threshold:
                await self.sleep_random_short()
                self.click_counter = 0
                self.random_clicks_threshold = randint(a=settings.CLICKS_FOR_SLEEP[0], b=settings.CLICKS_FOR_SLEEP[1])
        else:
            logger.info(f"{self.session_name} | Nothing was sent to websocket")

    async def check_memory_usage(self):
        # !!!!!!Проверка использования памяти и перезапуск при превышении лимита!!!!!!!!!!
        process = psutil.Process(os.getpid())
        while True:
            memory_info = process.memory_info()
            heap_total = psutil.virtual_memory().total
            if memory_info.rss > 0.8 * heap_total:
                logger.error(f"{self.session_name} | Restarting...")
                sys.exit(1)
            await asyncio.sleep(10)

    async def sleep_with_random_delay(self):
        delay = randint(a=settings.LONG_SLEEP_BETWEEN_TAP[0], b=settings.LONG_SLEEP_BETWEEN_TAP[1])
        logger.info(
            f"{self.session_name} | Sleeping for {delay} seconds. ")
        await asyncio.sleep(delay)

    async def sleep_random_short(self):
        delay = randint(a=settings.SLEEP_BETWEEN_TAP[0], b=settings.SLEEP_BETWEEN_TAP[1])
        logger.info(f"{self.session_name} | Sleeping for {delay} seconds.")
        await asyncio.sleep(delay)

    async def handle_message(self, message, websocket, init_data_base64: str):
        try:
            data = json.loads(message.data)

            if data["energy"] % settings.SHOW_BALANCE_EVERY_TAPS == 0:
                logger.info(
                    f"{self.session_name} | <green>Tapping</green> | <yellow>Energy: {data['energy']}</yellow> | <blue>Balance: {data['coins']}</blue>")

            if data["energy"] < randint(a=settings.SLEEP_BY_MIN_ENERGY_IN_RANGE[0], b=settings.SLEEP_BY_MIN_ENERGY_IN_RANGE[1]):
                logger.info(f"{self.session_name} | <red>Energy is low: {data['energy']}.</red> Sleeping. | Balance: {data['coins']}")
                self.is_tapping = False
                await self.sleep_with_random_delay()
                await self.reconnect(await self.get_user_id(), await self.get_tg_web_data(self.tg_client.proxy))
            elif data.get("minigame"):
                await self.send_minigame(websocket)
                logger.success(f"{self.session_name} | <red>Minigame!</red> ")
            else:
                if not self.is_tapping:
                    logger.success(f"{self.session_name} | <green>Start tapping!</green> | ")
                    self.is_tapping = True
                await self.send_message(websocket)

                if not self.tasks_checked:
                    await self.check_and_complete_tasks(init_data_base64)
                    self.tasks_checked = True

        except json.JSONDecodeError as e:
            logger.error(f"{self.session_name} | Error: {e}")
            await self.reconnect(await self.get_user_id(), await self.get_tg_web_data(self.tg_client.proxy))

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def get_user_id(self) -> int:
        try:
            if not self.tg_client.is_connected:
                await self.tg_client.connect()

            me = await self.tg_client.get_me()
            user_id = me.id
            return user_id
        except Exception as error:
            logger.error(f"{self.session_name} | Error getting user ID: {error}")
            raise error

    async def get_tasks(self, init_data_base64: str) -> list:
        headers = {
            "accept": "*/*",
            "accept-language": "ru,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "init-data": init_data_base64,
            "pragma": "no-cache",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": generate_random_user_agent(device_type='android', browser_type='chrome')
        }

        if self.proxy:
            connector = ProxyConnector(
                proxy_type=ProxyType.HTTP,
                host=self.proxy.host,
                port=self.proxy.port,
                username=self.proxy.login,
                password=self.proxy.password
            )
        else:
            connector = None

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                'https://cmonkey.vip/api/users/tasks',
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('tasks', [])
                else:
                    logger.error(f"{self.session_name} | Failed to fetch tasks with status: {response.status}")
                    return []

    async def complete_task(self, task_id: int, init_data_base64: str):
        headers = {
            "accept": "*/*",
            "accept-language": "ru,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "init-data": init_data_base64,
            "pragma": "no-cache",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": generate_random_user_agent(device_type='android', browser_type='chrome')
        }

        payload = json.dumps({"task": task_id})

        if self.proxy:
            connector = ProxyConnector(
                proxy_type=ProxyType.HTTP,
                host=self.proxy.host,
                port=self.proxy.port,
                username=self.proxy.login,
                password=self.proxy.password
            )
        else:
            connector = None

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.put(
                'https://cmonkey.vip/api/users/tasks',
                headers=headers,
                data=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"{self.session_name} | Task {task_id} updated successfully: {data.get('message')}")
                else:
                    logger.error(f"{self.session_name} | Failed to complete task {task_id} with status: {response.status} - {await response.text()}")

    async def check_and_complete_tasks(self, init_data_base64: str):
        tasks = await self.get_tasks(init_data_base64)
        for task in tasks:
            if task['id'] in [1, 2, 3] and not task['completed']:
                await self.complete_task(task['id'], init_data_base64)
                await asyncio.sleep(1)  # Add a delay between tasks to avoid being rate-limited

    async def run(self, proxy: str | None) -> None:

        proxy_conn = ProxyConnector.from_url(proxy) if proxy else None

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)

            while True:
                try:
                    tg_web_data = await self.get_tg_web_data(proxy=proxy)
                    user_id = await self.get_user_id()
                    await self.connect(user_id, tg_web_data)

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {error}")
                    await asyncio.sleep(delay=3)


async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
