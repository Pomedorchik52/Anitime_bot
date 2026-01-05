from telegram import BotCommand, MenuButtonCommands, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import asyncio
import json
import os
import random
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ANILIST_ENDPOINT = "https://graphql.anilist.co"
_anilist_cover_cache: dict[str, str] = {}



def _fetch_anilist_cover_url(title: str) -> str | None:
    cached = _anilist_cover_cache.get(title)
    if cached:
        return cached

    query = """
    query ($search: String) {
      Media(search: $search, type: ANIME) {
        coverImage {
          extraLarge
          large
        }
      }
    }
    """.strip()

    body = json.dumps({"query": query, "variables": {"search": title}}).encode("utf-8")
    req = Request(
        ANILIST_ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=8) as resp:
            payload = json.load(resp)
    except (HTTPError, URLError, TimeoutError, ValueError):
        return None
    data = payload.get("data")
    if not isinstance(data, dict):
        return None

    media = data.get("Media")
    if not isinstance(media, dict):
        return None

    cover = media.get("coverImage")
    if not isinstance(cover, dict):
        return None

    url = cover.get("extraLarge") or cover.get("large")
    if isinstance(url, str) and url:
        _anilist_cover_cache[title] = url
        return url

    return None


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            BotCommand("start", "Запустить бота"),
            BotCommand("help", "Показать помощь"),
            BotCommand("anime", "Посоветовать аниме"),
            BotCommand("game", "Игра"),
            BotCommand("photoid", "Получить file_id фото"),
        ]
    )
    await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())

app = Application.builder().token("").post_init(post_init).build()

aiky_messages = [
    "Я тебя люблю и очень рада, что ты здесь 💖",
    "Ты делаешь Anitime чуточку теплее для меня ✨",
    "Мне приятно видеть тебя у нас 🌸",
    "Ты — часть моего уютного мира 💫",
    "Спасибо, что заглянул, я тебя люблю 💕",
    "С тобой смотреть аниме ещё приятнее 🍿💗",
    "Для меня ты всегда желанный гость 🤍",
    "Я рада тебе больше, чем ты думаешь 😊",
    "Мне приятно быть рядом с тобой на Anitime 🌙",
    "Ты даришь мне хорошее настроение 💞",
    "Я тебя ценю и люблю 🌷",
    "Здесь я всегда рада тебе ✨",
    "Спасибо, что выбрал меня 💖",
    "Ты — важная часть Anitime для меня 🌸",
    "Оставайся со мной, я тебя люблю 💗",
    "Я всегда рада тебе и твоей улыбке 💕",
    "Ты делаешь мой день лучше ✨",
    "Спасибо, что ты со мной 💖",
    "Твоё присутствие очень ценно для меня 🌸",
    "Мне приятно, что ты выбрал Anitime 🤍",
    "Ты приносишь уют в мой мир 💫",
    "Я рада каждому твоему визиту 😊",
    "С тобой здесь по-настоящему тепло 💗",
    "Ты — гость, которого я всегда жду 🌷",
    "Я счастлива видеть тебя 💕",
    "Ты наполняешь Anitime добром для меня ✨",
    "Мне важно, что ты рядом 💖",
    "Ты делаешь это место живым для меня 🌸",
    "Спасибо, что доверяешь мне 🤍",
    "Для меня ты всегда желанный здесь 💫",
    "Я ценю каждое твоё появление 😊",
    "Ты часть моей маленькой истории 💗",
    "С тобой Anitime становится лучше для меня 🌷",
    "Я рада делить этот момент с тобой 💕",
    "Ты приносишь свет и хорошее настроение мне ✨",
]

emoji_game_list = [
    {"emoji": "🪚👨", "answer": "Человек-бензопила"},
    {"emoji": "📓💀", "answer": "ТЕТРАДЬ СМЕРТИ"},
    {"emoji": "🍥🥷", "answer": "НАРУТО"},
    {"emoji": "🏴‍☠️🗺️", "answer": "ВАН-ПИС"},
    {"emoji": "⚔️👹", "answer": "КЛИНОК РАССЕКАЮЩИЙ ДЕМОНОВ"},
    {"emoji": "🌙✨", "answer": "СЕЙЛОР МУН"},
    {"emoji": "🪨🧪", "answer": "ДОКТОР СТОУН"},
    {"emoji": "🎸😳", "answer": "ОДИНОКИЙ РОКЕР"},
    {"emoji": "👻🏮", "answer": "УНЕСЕННЫЕ ПРИЗРАКАМИ"},
    {"emoji": "🌳🐾", "answer": "МОЙ СОСЕД ТОТОРО"},
    {"emoji": "🕵️👨‍👩‍👧", "answer": "СЕМЬЯ ШПИОНОВ"},
    {"emoji": "⚔️🌑", "answer": "BERSERK"},
    {"emoji": "⛩️🗡️", "answer": "БЕЗДОМНЫЙ БОГ"},
    {"emoji": "🌀👻", "answer": "МАГИЧЕСКАЯ БИТВА"},
    {"emoji": "🎤👶⭐", "answer": "ЗВЁЗДНОЕ ДИТЯ"},
    {"emoji": "🍀⚔️", "answer": "ЧЕРНЫЙ КЛЕВЕР"},
    {"emoji": "⏳🏝️", "answer": "ЛЕТНЕЕ ВРЕМЯ"},
    {"emoji": "🎹🎻", "answer": "ТВОЯ АПРЕЛЬСКАЯ ЛОЖЬ"},
    {"emoji": "🤖👦", "answer": "ЕВАНГЕЛИОН"},
    {"emoji": "🏐🔥", "answer": "ВОЛЕЙБОЛ"},
    {"emoji": "😇🏠", "answer": "АНГЕЛ ЖИВУЩИЙ ПО СОСЕДСТВУ"},
    {"emoji": "📏💔", "answer": "5 САНТИМЕТРОВ В СЕКУНДУ"},
    {"emoji": "🦊🍵", "answer": "ЗАБОТЛИВАЯ 800-ЛЕТНЯЯ ЖЕНА"},
    {"emoji": "🚀👧❤️", "answer": "МИЛЫЙ ВО ФРАНКСЕ"},
    {"emoji": "🦸‍♂️🏫", "answer": "МОЯ ГЕРОЙСКАЯ АКАДЕМИЯ"},
    {"emoji": "🌌🔁", "answer": "ТВОЕ ИМЯ"},
    {"emoji": "🧝‍♀️🕯️", "answer": "ПРОВОЖАЮЩИЙ В ПОСЛЕДНИЙ ПУТЬ ФРИРЕН"},
    {"emoji": "🧵👗💞", "answer": "ЭТА ФАРФОРОВАЯ КУКЛА ВЛЮБИЛАСЬ"},
    {"emoji": "🕵️‍♂️⚰️", "answer": "ДЕТЕКТИВ УЖЕ МЕРТВ"},
    {"emoji": "🧑‍🎤👹", "answer": "ТОКИЙСКИЙ ГУЛЬ"},
    {"emoji": "🧱⚔️", "answer": "АТАКА ТИТАНОВ"},
    {"emoji": "♟️👑", "answer": "КОД ГИАСС"},
    {"emoji": "🧑‍🍳⚔️", "answer": "ПОВАР-БОЕЦ"},
    {"emoji": "🧠🔪", "answer": "ПАРАЗИТ"},
    {"emoji": "🎮🔁", "answer": "РЕ:ЗЕРО"},
    {"emoji": "👊👨‍🦲", "answer": "ВАНПАНЧМЕН"},
    {"emoji": "🐺🌕", "answer": "ВОЛЧИЦА И ПРЯНОСТИ"},
    {"emoji": "🧑‍🎓🧠", "answer": "КЛАСС УБИЙЦ"},
    {"emoji": "🧑‍🚀🤠", "answer": "КОБОЙ БИБОП"},
    {"emoji": "🎭🎤", "answer": "АКТЁРЫ ОСЛЕПЛЕННЫЕ СЦЕНОЙ"},
    {"emoji": "🧛‍♂️🌙", "answer": "ХЕЛЛСИНГ"},
    {"emoji": "🧬👦", "answer": "ДОРОХЕДОРО"},
    {"emoji": "💀⚔️👑", "answer": "ОВЕРЛОРД"},
    {"emoji": "🧙‍♂️📜", "answer": "РЕИНКАРНАЦИЯ БЕЗРАБОТНОГО"},
    {"emoji": "🏀🔥", "answer": "БАСКЕТБОЛ КУРОКО"},
    {"emoji": "👧🎒🌧️", "answer": "САД ИЗЯЩНЫХ СЛОВ"},
    {"emoji": "🧑‍⚕️😈", "answer": "ДОКТОР СМЕРТИ"},
    {"emoji": "🧠📱", "answer": "СТЕЙНС ГЕЙТ"},
    {"emoji": "🪄👑", "answer": "СУДЬБА: НАЧАЛО"},
    {"emoji": "🎻👦💔", "answer": "ТВОЯ ЛОЖЬ В АПРЕЛЕ"},
    {"emoji": "🏹👧", "answer": "МАДОКА МАГИКА"},
    {"emoji": "🐉⚔️", "answer": "СЕМЬ СМЕРТНЫХ ГРЕХОВ"},
    {"emoji": "🧑‍🎤🎶", "answer": "БОЧЧИ РОК"},
    {"emoji": "👊🩸", "answer": "ДОРОХЕДОРО"},
    {"emoji": "🌸👘", "answer": "КЛИНОК РАССЕКАЮЩИЙ ДЕМОНОВ: КВАРТАЛ КРАСНЫХ ФОНАРЕЙ"},
    {"emoji": "🧑‍🚒🔥", "answer": "ОГНЕННАЯ БРИГАДА ПОЖАРНЫХ"},
    {"emoji": "🕶️🤖", "answer": "ПРИЗРАК В ДОСПЕХАХ"},
    {"emoji": "🧑‍🎨👧", "answer": "ГОЛУБОЙ ПЕРИОД"},
    {"emoji": "🐱🌙", "answer": "КОШКА-ВЕДЬМА"}
]

anime_list = [
    {
        "title": "Человек-бензопила",
        "description": (
            "Дэндзи — бедный подросток, который охотится на демонов вместе с Почитой-бензопилой, "
            "чтобы выплатить долг.\n"
            "После трагедии он становится Человеком-бензопилой и вступает в ряды охотников на демонов."
        ),
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4303601/8205541e-8436-41f8-8dcf-720400965d5e/1920x1080",
    },
    {
        "title": "АЛЯ ИНОГДА КОКЕТНИЧАЕТ СО МНОЙ ПО-РУССКИ",
        "description": (
            "Романтическая комедия о школьнице Але, которая умело сочетает дерзость и очарование, "
            "кокетничая на русском языке. Следите за ее приключениями и неожиданными поворотами сюжета!"
        ),
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/9784475/b9616eb3-53fc-45b9-a803-d7328d47aa4a/1920x",
    },
    {
        "title": "BERSERK",
        "description": "Наёмник Гатс сражается против демонов и судьбы в мрачном мире, преследуемый клеймом. История дружбы, предательства и борьбы с неизбежным.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1600647/6fcabf86-0197-4bd9-a31a-f1cb460fb04c/1920x",
    },
    {
        "title": "ТЕТРАДЬ СМЕРТИ",
        "description": "Психологический триллер о старшекласснике Лайте Ягами, который находит Тетрадь смерти, позволяющую убивать людей, просто записывая их имена. Его игра в кошки-мышки с гениальным детективом L держит в напряжении до последней минуты!",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1777765/d6808a93-a518-40c4-8d01-ef9dd3bf0420/1920x",
    },
    {
        "title": "НЕОБЬЯТНЫЙ ОКЕАН",
        "description": "Эпичная комедия про студента Иори, который приезжает в приморский городок, мечтая о нормальной уни-жизни с девчонками и тусами. Но вместо этого влипает в клуб дайвинга с кучей голых алкашей-мужиков, которые заставляют его пить как не в себя.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1599028/ea5299b0-ee59-41b8-8a31-46d872bd13b1/1920x",
    },
    {
        "title": "НАРУТО",
        "description": "Удзумаки Наруто — юный ниндзя, мечтающий стать Хокаге. Он сражается с врагами, защищает друзей и раскрывает тайну Девятихвостого внутри себя, проходя путь от изгоя до героя деревни Коноха.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1704946/e63beb56-0433-4bbf-ae70-5d85a5ed8945/1920x",
    },
    {
        "title": "МАГИЧЕСКАЯ БИТВА",
        "description": "Итадори Юдзи попадает в мир проклятий после встречи с опасным артефактом. Он вступает в училище магов, чтобы сражаться с проклятиями и лишить силу легендарного Сукуны.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/6201401/bfd6c4b8-2796-4727-8725-59651d2820a7/1920x",
    },
    {
        "title": "ЗВЁЗДНОЕ ДИТЯ",
        "description": "Описание пока не добавлено.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4483445/2d7148a7-0b7d-4af5-b4ad-c86526a2d515/1920x",
    },
    {
        "title": "ЧЕРНЫЙ КЛЕВЕР",
        "description": "Аста и Юно — сироты, выросшие в церкви королевства Клевер. Юно — гений магии ветра, а Аста родился без магии, но обладает редкой анти-магией и несгибаемой волей. Они соперничают и мечтают стать Королем магов, проходя через испытания, битвы и дружбу.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4303601/d08031d8-1021-4fe1-897d-d1899d12b3b4/1920x",
    },
    {
        "title": "ЛЕТНЕЕ ВРЕМЯ",
        "description": "Синпэй Адзиро — обычный парень, который возвращается на родной остров, но после загадочной смерти подруги оказывается втянут в кошмар с тенями, убийствами и бесконечными перезапусками времени.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4303601/3baadc5f-6d3b-492e-9323-c74cd5731003/1920x",
    },
    {
        "title": "ТВОЯ АПРЕЛЬСКАЯ ЛОЖЬ",
        "description": "Коусэй Арима — талантливый пианист, потерявший способность слышать музыку после смерти матери, чья жизнь меняется, когда он встречает яркую и свободолюбивую скрипачку, возвращающую ему цвет, боль и смысл жизни.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4303601/2641b207-d7b0-45e6-8759-1190580596dc/1920x",
    },
    {
        "title": "ОДИНОКИЙ РОКЕР",
        "description": "Хитори Гото — социально тревожная школьница с мечтой стать рок-звездой, которая прячется за гитарой и неожиданно находит друзей, сцену и себя в шуме маленькой инди-группы.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4774061/e44882d4-8436-497f-b6fb-54f916db1cfe/1920x",
    },
    {
        "title": "ЕВАНГЕЛИОН",
        "description": "Школьник Синдзи Икари вынужден пилотировать гигантского био‑меха «Евангелион» для защиты человечества от Ангелов. За битвами скрываются психологические драмы и тайны организации NERV.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1900788/4a0827fc-b53b-4615-8aae-736eeb014c8b/1920x",
    },
    {
        "title": "ВОЛЕЙБОЛ",
        "description": "Сёё Хината, вдохновлённый «Маленьким гигантом», вступает в команду Карасуно и вместе с Тобио Кагеяма стремится покорить вершины школьного волейбола.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1599028/c11131ea-c6e0-4a0e-bdda-9009da1d8c30/1920x",
    },
    {
        "title": "СЕМЬЯ ШПИОНОВ",
        "description": "Семья, собранная ради тайной миссии: шпион, телепат и убийца пытаются ужиться и сохранять секреты.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/10893610/e288334b-85e2-4790-9fad-012b829132a3/1920x",
    },
    {
        "title": "СЕЙЛОР МУН",
        "description": "Усаги Цукино становится воином любви и справедливости, чтобы защитить Землю от сил тьмы, находя друзей и раскрывая судьбу Луны.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1600647/e4f95b9d-a306-4481-a19c-5e16f5591d4e/300x450",
    },
    {
        "title": "ДЕТЕКТИВ УЖЕ МЕРТВА",
        "description": "Кимидзука встречает детектива Сиесту, чья судьба оставляет загадку и след, который невозможно забыть.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4303601/9ebdf327-9687-42b5-b4ce-1faec422eb21/1920x",
    },
    {
        "title": "ЭТА ФАРФОРОВАЯ КУКЛА ВЛЮБИЛАСЬ",
        "description": "Годзё Вакана и Мэрин Китагавы создают косплей, преодолевая неуверенность и открывая чувства.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4303601/654c6424-8d9a-476a-853e-38c49eed3a21/1920x",
    },
    {
        "title": "ПРОВОЖАЮЩИЙ В ПОСЛЕДНИЙ ПУТЬ ФРИРЕН",
        "description": "Фрирен — бессмертная эльфийка-маг, которая после победы над Королём демонов отправляется в тихое путешествие, заново осмысливая дружбу, утраты и то, как мимолётна человеческая жизнь.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/9784475/c1ef8c0c-23b8-477e-a42d-9f8d85396ec8/300x450",
    },
    {
        "title": "АНГЕЛ ЖИВУЩИЙ ПО СОСЕДСТВУ",
        "description": "Махиру Сиина — идеальная школьная «ангел», которая живёт по соседству с замкнутым Аманэ, и их простая забота друг о друге постепенно превращает одиночество в тёпкую, тихую близость.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4303601/2641b207-d7b0-45e6-8759-1190580596dc/1920x",
    },
    {
        "title": "5 САНТИМЕТРОВ В СЕКУНДУ",
        "description": "Такаки Тоно — обычный мальчик, чья жизнь проходит под знаком расстояний, редких встреч и несказанных чувств, показывая, как медленно и болезненно люди могут отдаляться друг от друга.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1777765/087dfb5c-9270-4f50-826d-44a86f0bea6b/1920x",
    },
    {
        "title": "МОЙ СОСЕД ТОТОРО",
        "description": "Сацуки и Мэй — две сестры, которые переезжают в деревню и находят волшебного духа леса Тоторо, открывающего им мир детского воображения, доброты и тихого чуда.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/10703959/507d8d5c-87e0-4b2e-8da3-e699976ab1cf/1920x",
    },
    {
        "title": "ЗАБОТЛИВАЯ 800-ЛЕТНЯЯ ЖЕНА",
        "description": "Сэнко — 800-летняя лисья богиня, которая появляется в жизни уставшего офисного работника, чтобы заботой, теплом и домашним уютом исцелять его от повседневного выгорания.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1946459/4ce389cc-6a39-46a4-b60d-cef3e0d977cf/1920x",
    },
    {
        "title": "ПЕСНЬ НОЧНЫХ СОВ",
        "description": "Мидори — обычная школьница, чья жизнь переворачивается после встречи с загадочными «Ночными совами», тайным клубом ночных приключений, где она открывает дружбу, мечты и магию в тишине ночного города.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4303601/11ff3951-f0f5-426d-a75d-3f77c075c0c7/1920x",
    },
    {
        "title": "МИЛЫЙ ВО ФРАНКСЕ",
        "description": "Хиро — замкнутый подросток, который вместе с загадочной Франксом по имени 02 сражается с огромными монстрами, открывая в себе смелость, любовь и смысл собственного существования.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1900788/97e30fe2-c0c3-4993-930e-a775056e40a7/1920x",
    },
    {
        "title": "ДОКТОР СТОУН",
        "description": "Сенку Исигами — гений науки, который после таинственного каменного сна человечества решает заново восстановить цивилизацию, используя изобретения, эксперименты и смекалку, чтобы вернуть людям технологии и надежду.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4483445/8c4aef76-eae3-4d13-a0e4-044fd980a22b/1920x",
    },
    {
        "title": "МОЯ ГЕРОЙСКАЯ АКАДЕМИЯ",
        "description": "Изуку Мидория — обычный мальчик без суперспособностей в мире, где они есть у всех, который мечтает стать героем и, получив силу «Плюс Ультра», поступает в Академию героев, чтобы защищать людей и воплотить свои идеалы.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/9784475/26f8c07b-31a0-49c9-82c4-360dd5e64fb0/1920x",
    },
    {
        "title": "ТВОЕ ИМЯ",
        "description": "Таки и Мицуха — два незнакомца, чьи тела и жизни внезапно начинают меняться местами, и через эту загадочную связь они ищут друг друга, преодолевая время, расстояния и судьбу.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1777765/bb567391-9e94-4fa9-b926-2538f292a13a/1920x",
    },
    {
        "title": "УНЕСЕННЫЕ ПРИЗРАКАМИ",
        "description": "Тихиро — обычная девочка, которая попадает в волшебный мир духов, где должна найти смелость и находчивость, чтобы спасти своих родителей и вернуться домой.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1900788/6c61384e-41b6-4bc5-b5d7-856d75d99146/1920x",
    },
    {
        "title": "ВАН-ПИС",
        "description": "Монки Д. Луффи — мальчик с резиновым телом, который мечтает стать Королём пиратов, собирая команду, исследуя опасные моря и сражаясь с могущественными врагами.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/6201401/3f0fbf88-6f11-4307-b169-8474d1acbdfa/1920x",
    },
    {
        "title": "КЛИНОК РАССЕКАЮЩИЙ ДЕМОНОВ",
        "description": "Танжиро Камадо — добрый юноша, ставший охотником на демонов после трагедии в семье, который вместе с друзьями сражается с чудовищами, защищая людей и ищет способ вернуть сестру к человеческому облику.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4716873/277f9057-1833-444b-9b13-bb0446472ec7/1920x",
    },
    {
        "title": "БЕЗДОМНЫЙ БОГ",
        "description": "Кудзё Ками и Фурутори — бог без дома, который вместе с маленькой помощницей путешествует по миру, сталкиваясь с людьми и странностями, открывая ценность дружбы, заботы и простых радостей.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/4774061/8d10d66a-2b2c-4f18-92d1-3198500ca166/1920x",
    },
    {
        "title": "ЗОЛОТАЯ ПОРА",
        "description": "Такаэ Окудэра и её друзья — группа школьников, чья жизнь проходит на пороге взросления, любви и выбора пути, где каждый день наполнен мечтами, романтикой и маленькими жизненными откровениями",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/10671298/f990f9f7-7a18-4f84-922f-d161e8a48dce/1920x",
    },
    {
        "title": "ЭТОТ ГЛУПЫЙ СВИН НЕ ПОНИМАЕТ МЕЧТУ ДЕВОЧКИ-ЗАЙКИ",
        "description": "История о настойчивой девочке-зайке и её непонимающем спутнике, где через комичные ситуации, недопонимания и простую заботу раскрывается дружба, поддержка и стремление к мечте.",
        "photo_url": "https://avatars.mds.yandex.net/get-kinopoisk-image/1629390/1bbdd343-6620-483f-8ce3-95438da543f4/1920x",
    },
   
]

def main_reply_markup() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("Aiky"), KeyboardButton("Help")],
        [KeyboardButton("Anime"), KeyboardButton("Game")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def emoji_game_reply_markup(options: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(options[0]), KeyboardButton(options[1])],
        [KeyboardButton(options[2]), KeyboardButton(options[3])],
        [KeyboardButton("🔄 Новая загадка"), KeyboardButton("⛔ Выход")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def emoji_game_next_round(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    titles = [item.get("title") for item in anime_list if item.get("title")]
    if len(titles) < 4 or not emoji_game_list:
        await update.effective_message.reply_text("Список для игры пока не готов.", reply_markup=main_reply_markup())
        return

    state = context.chat_data.get("emoji_game")
    if not state:
        await update.effective_message.reply_text("Игра не запущена.", reply_markup=main_reply_markup())
        return

    total = int(state.get("total", 5))
    current_round = int(state.get("round", 0))
    score = int(state.get("score", 0))
    used_answers = state.get("used_answers", [])

    if current_round >= total:
        context.chat_data.pop("emoji_game", None)
        await update.effective_message.reply_text(f"Игра окончена! Счёт: {score}/{total}", reply_markup=main_reply_markup())
        return

    current_round += 1
    state["round"] = current_round

    candidates = [item for item in emoji_game_list if item.get("answer") in titles and item.get("answer") not in used_answers]
    if not candidates:
        candidates = [item for item in emoji_game_list if item.get("answer") in titles]
    if not candidates:
        await update.effective_message.reply_text("Список для игры пока не готов.", reply_markup=main_reply_markup())
        return

    round_item = random.choice(candidates)
    answer = round_item["answer"]
    distractors = [t for t in titles if t != answer]
    if len(distractors) < 3:
        await update.effective_message.reply_text("Список для игры пока не готов.", reply_markup=main_reply_markup())
        return

    options = random.sample(distractors, k=3) + [answer]
    random.shuffle(options)
    used_answers.append(answer)
    state["used_answers"] = used_answers
    state["answer"] = answer
    state["options"] = options

    await update.effective_message.reply_text(
        f"Раунд {current_round}/{total} • Счёт {score}/{current_round - 1}\n\nУгадай аниме по эмодзи:\n\n{round_item['emoji']}\n\nВыбери вариант ниже:",
        reply_markup=emoji_game_reply_markup(options),
    )


async def start_emoji_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["emoji_game"] = {"round": 0, "score": 0, "total": 5, "used_answers": []}
    await emoji_game_next_round(update, context)


async def emoji_game_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not getattr(message, "text", None):
        return

    state = context.chat_data.get("emoji_game")
    if not state:
        return

    text = message.text.strip()
    if text == "🔄 Новая загадка":
        await emoji_game_next_round(update, context)
        return

    if text == "⛔ Выход":
        context.chat_data.pop("emoji_game", None)
        await message.reply_text("Ок, выходим из игры.", reply_markup=main_reply_markup())
        return

    options = state.get("options", [])
    if text not in options:
        return

    if text == state.get("answer"):
        state["score"] = int(state.get("score", 0)) + 1
        await message.reply_text("Верно! 🎉")
        await emoji_game_next_round(update, context)
    else:
        await message.reply_text("Неа 🙈 Попробуй ещё раз или нажми «🔄 Новая загадка».")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_markup = main_reply_markup()
    await update.effective_message.reply_text(
        "Привет! Я Айко🌸\n\n"
        "Чем могу помочь:\n"
        "• Подобрать аниме на вечер\n"
        "• Подсказать по сайту\n"
        "• Поиграть в мини-игру\n\n"
        "Нажми кнопку ниже 👇",
        reply_markup=reply_markup
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("Список доступных команд:\n"
                                    " /start - Запустить бота\n"
                                    " /help - Показать это сообщение\n"
                                    " /anime - Получить рекомендацию аниме\n"
                                    " /game - Играть в увлекательную игру с аниме")

async def aiky(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(random.choice(aiky_messages))

async def anime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not anime_list:
        await update.effective_message.reply_text("В списке пока нет аниме.")
        return

    state = context.chat_data.get("anime_cycle")
    if not state or not isinstance(state, dict) or int(state.get("size", 0)) != len(anime_list):
        order = list(range(len(anime_list)))
        random.shuffle(order)
        state = {"order": order, "pos": 0, "size": len(anime_list)}
        context.chat_data["anime_cycle"] = state

    order = state.get("order")
    if not isinstance(order, list) or len(order) != len(anime_list):
        order = list(range(len(anime_list)))
        random.shuffle(order)
        state["order"] = order
        state["pos"] = 0
        state["size"] = len(anime_list)

    pos = int(state.get("pos", 0))
    if pos >= len(order):
        random.shuffle(order)
        pos = 0

    idx = int(order[pos])
    state["pos"] = pos + 1

    random_anime = anime_list[idx]
    title = random_anime.get("title", "Аниме")
    description = random_anime.get("description", "")
    caption = f"Вот это аниме я советую посмотреть сегодня вечером:\n\n{title}\n\n{description}".strip()

    photo_url = random_anime.get("photo_url")
    if not photo_url and title:
        photo_url = await asyncio.to_thread(_fetch_anilist_cover_url, title)

    if photo_url:
        try:
            if len(caption) <= 1024:
                await update.effective_message.reply_photo(photo=photo_url, caption=caption)
                return

            short_caption = caption[:1024]
            await update.effective_message.reply_photo(photo=photo_url, caption=short_caption)
            await update.effective_message.reply_text(caption[1024:])
            return
        except Exception:
            pass

    await update.effective_message.reply_text(caption)

async def photoid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not getattr(message, "photo", None):
        await update.effective_message.reply_text("Пришли фото с подписью /photoid")
        return

    photo = message.photo[-1]
    await update.effective_message.reply_text(
        f"file_id:\n{photo.file_id}\n\nМожешь вставить это значение в поле photo_url у нужного аниме."
    )

async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start_emoji_game(update, context)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("anime", anime))
app.add_handler(CommandHandler("game", game))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Start$"), start))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Aiky$"), aiky))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Help$"), help))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Anime$"), anime))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Game$"), game))
app.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r"^/photoid(@\\w+)?$"), photoid))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, emoji_game_message), group=1)


app.run_polling()
