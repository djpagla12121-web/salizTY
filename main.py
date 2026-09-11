import asyncio
import io
import re
import json
import html
import os
import httpx
import pyotp
import random
import string
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
# ==================== CONFIG SECTION ====================

BOT_TOKEN = "8367123815:AAFtCqKasWjJG3hk3ReAGEvQnW0K2hEqbLM"
API_KEY = "MURAD_094E0E1256ED2ABD852A4C49"
BASE_URL = "https://2eee7.com/@Access/@Bot/2eee7/@public"           # আপনার প্যানেল ডোমেন (trailing slash ছাড়া)
USER_DATA_FILE = "users.json"
PAID_SMS_FILE = "paid_sms.json"
STATS_FILE = "user_stats.json"
REFERRAL_DATA_FILE = "referral_data.json"
BANNED_USERS_FILE = "banned_users.json"
WITHDRAW_DATA_FILE = "withdraw_requests.json"
ACTIVITY_LOGS_FILE = "activity_logs.json"
DATA_RANGE_FILE = "datarange.json"
SETTINGS_FILE = "settings.json"
# ==================== MULTIPLE ADMINS CONFIGURATION ====================
ADMINS = [8982457554]

OTP_GROUP_ID = -100356677172

# ==================== PREMIUM EMOJI SETUP ====================
PREMIUM_EMOJIS = {
    "fire": "6158872240768160988",
    "rocket": "5382194935057372936",
    "phone": "6158892349805040268",
    "search": "5303138782004924588",
    "zap": "6156703243628975744",
    "money": "5303214794336125778",
    "gift": "5411233191765759009",
    "profile": "5310278924616356636",
    "trophy": "5197288647275071607",
    "support": "6156640760444752831",
    "config": "5330320040883411678",
    "cancel": "5195033767969839232",
    "users": "6159105672240697584",
    "back": "6158802623643260292",
    "broadcast": "6156448083916887235",
    "id": "6156729881016147164",
    "ban_list": "6159107733824999752",
    "chart": "5264713049637409446",
    "user_check": "5267102644886853973",
    "ban": "5445221832074483553",
    "unban": "5312441427764989435",
    "minus": "5274055917766202507",
    "plus": "5262517101578443800",
    "success": "5197288647275071607",
    "warning": "5195033767969839232",
    "globe": "5264713049637409446",
    "signal": "6156923364997862692",
    "key": "6158950306093732016",
    "mail": "6158821233736553062",
    "wait": "6158728556932239412",
    "sparkle": "6156543226032428672",
    "medal1": "6158701271005008955",
    "medal2": "6156599554528515952",
    "medal3": "6156624216230729210",
    "calendar": "6156906412761946453",
    "cash": "5291914649481007565",
    "bank": "5400362079783770689",
    "whatsapp": "5334998226636390258",
    "telegram": "5330237710655306682",
    "facebook": "5323261730283863478",
    "instagram": "5319160079465857105",
    
    # নতুন ৪টি স্পেশাল প্রিমিয়াম ইমোজি (এখানে যোগ করুন)
    "add_new": "4956507094124594921",
    "rem_new": "4958534924278694938",
    "tick_new": "5206607081334906820",
    "dot_new": "5947099588224620513"
}

def p_emj(key, fallback=""):
    emoji_id = PREMIUM_EMOJIS.get(key)
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'
    return fallback

def e_id(key, fallback="5382194935057372936"):
    return PREMIUM_EMOJIS.get(key, fallback)

def get_service_emoji_id(service_name):
    s_lower = service_name.lower()
    
    # আপনার দেওয়া রিয়েল প্রিমিয়াম ইমোজি আইডিগুলো
    if "whatsapp" in s_lower or "wa" in s_lower: return "6158872240768160988"
    if "instagram" in s_lower or "ig" in s_lower: return "6158808005237281009"
    if "facebook" in s_lower or "fb" in s_lower: return "6156703243628975744"
    if "telegram" in s_lower or "tg" in s_lower: return "6156640760444752831"
    
    # লিস্ট থেকে খুঁজে পাওয়া আরও কিছু স্পেশাল সার্ভিস
    if "twitter" in s_lower or "x.com" in s_lower: return "5294081808374179122"
    if "discord" in s_lower: return "5296722032145210532"
    if "messenger" in s_lower: return "5294203433258068405"
    if "google" in s_lower or "gmail" in s_lower: return "5294467243034288512"
    if "youtube" in s_lower or "yt" in s_lower: return "5294502539075527358"
    if "twitch" in s_lower: return "5296760592361594230"
    if "skype" in s_lower: return "5293999121663795750"
    
    # বাকি অন্যান্য অচেনা সার্ভিসের জন্য ডিফল্ট কিউট ইমোজি (আপনার লিস্টের ৯ নং আইডি)
    return "6156729881016147164"

# ==================== WELCOME MESSAGE CONFIGURATION ====================
WELCOME_MESSAGE = f"""{p_emj('sparkle', '✨')} 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗙𝗔𝗦𝗧 𝗫 𝗦𝗠𝗦 {p_emj('sparkle', '✨')} 
━━━━━━━━━━━━━━━━━━━━━━
{p_emj('rocket', '🚀')} Enjoy Premium Quality Service {p_emj('rocket', '🚀')}"""

# ==================== OTP RATE CONFIGURATION ====================
OTP_RATE = 0.20
REFERRAL_PRICE = 0
MIN_WITHDRAW = 50
MAX_WITHDRAW = 10000

# ==================== SUPPORT & DEVELOPER LINKS ====================
SUPPORT_LINK = "https://t.me/salizTY"      
DEVELOPER_LINK = "https://t.me/salizTY"          

request_queue = asyncio.Queue()
MAX_WORKERS = 5000

client_async = httpx.AsyncClient(
    timeout=httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0),
    headers={"X-API-Key": API_KEY},
    limits=httpx.Limits(max_connections=2000, max_keepalive_connections=500)
)

active_numbers = {}
last_range = {}
CHECK_INTERVAL = 1.5

# ==================== LIVEACCESS CACHE ====================
_liveaccess_cache = {"services": []}
LIVEACCESS_REFRESH_INTERVAL = 25

async def _do_liveaccess_fetch():
    global _liveaccess_cache
    try:
        r = await client_async.get(f"{BASE_URL}/api/liveaccess")
        data = r.json()
        if data.get("status") == "ok":
            svcs = data.get("services", [])
            if svcs:
                _liveaccess_cache["services"] = svcs
                print(f"[liveaccess] cache updated — {len(svcs)} service(s)")
    except Exception as e:
        print(f"[liveaccess] fetch error: {e}")

async def liveaccess_refresh_loop():
    while True:
        await _do_liveaccess_fetch()
        await asyncio.sleep(LIVEACCESS_REFRESH_INTERVAL)

def get_cached_services():
    return _liveaccess_cache.get("services", [])

# ==================== CHECK IF USER IS ADMIN ====================
# ==================== CHECK IF USER IS ADMIN ====================
def is_full_admin(uid):
    uid_int = int(uid)
    settings = load_settings()
    # যারা মেইন স্ক্রিপ্টে আছে বা সেটিংসে ফুল অ্যাডমিন হিসেবে অ্যাড হয়েছে
    return uid_int in ADMINS or uid_int in settings.get("full_admins", [])

def is_sub_admin(uid):
    uid_int = int(uid)
    settings = load_settings()
    return uid_int in settings.get("sub_admins", [])

def is_admin(uid):
    return is_full_admin(uid) or is_sub_admin(uid)

# ==================== WITHDRAW DATA FUNCTIONS ====================
def load_withdraw_requests():
    if not os.path.exists(WITHDRAW_DATA_FILE):
        with open(WITHDRAW_DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(WITHDRAW_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_withdraw_requests(data):
    with open(WITHDRAW_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_payment_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

# ==================== BANNED USERS FUNCTIONS ====================
def load_banned_users():
    if not os.path.exists(BANNED_USERS_FILE):
        with open(BANNED_USERS_FILE, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(BANNED_USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_banned_users(banned_list):
    with open(BANNED_USERS_FILE, "w") as f:
        json.dump(banned_list, f, indent=4)

def is_user_banned(uid):
    banned_list = load_banned_users()
    return str(uid) in banned_list

def ban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str not in banned_list:
        banned_list.append(uid_str)
        save_banned_users(banned_list)
        return True
    return False

def unban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str in banned_list:
        banned_list.remove(uid_str)
        save_banned_users(banned_list)
        return True
    return False

# ==================== REFERRAL DATA FUNCTIONS ====================
def load_referral_data():
    if not os.path.exists(REFERRAL_DATA_FILE):
        with open(REFERRAL_DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(REFERRAL_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_referral_data(data):
    with open(REFERRAL_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def update_referral_count(uid, count):
    referral_data = load_referral_data()
    uid_str = str(uid)
    if uid_str not in referral_data:
        referral_data[uid_str] = {"referral_count": 0}
    referral_data[uid_str]["referral_count"] = count
    save_referral_data(referral_data)

def get_referral_count(uid):
    referral_data = load_referral_data()
    uid_str = str(uid)
    return referral_data.get(uid_str, {}).get("referral_count", 0)

# ==================== DATA RANGE FILE ====================
def load_range_db():
    if not os.path.exists(DATA_RANGE_FILE):
        return {}
    try:
        with open(DATA_RANGE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_range_db(data):
    with open(DATA_RANGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_number_range_info(uid, number, range_text):
    db = load_range_db()
    flag, name = get_country_info(number)
    db[normalize_number(number)] = {
        "user_id": str(uid),
        "number": f"+{normalize_number(number)}",
        "range": range_text,
        "country": f"{flag} {name}"
    }
    save_range_db(db)

# ==================== COUNTRY MAPPING SECTION ====================

CUSTOM_FLAG_IDS = {
    '🇺🇦': '5222250679371839695', '🇺🇸': '5224321781321442532', '🇵🇱': '5224670399521892983',
    '🇰🇿': '5222276376161171525', '🇦🇿': '5224426544163728284', '🇪🇺': '5222108911091331711',
    '🇺🇳': '5451772687993031127', '🇦🇲': '5224369957969603463', '🇷🇺': '5280582975270963511',
    '🇨🇳': '5224435456220868088', '🇺🇿': '5222404546575219535', '🇩🇪': '5222165617544542414',
    '🇯🇵': '5222390089715299207', '🇹🇷': '5224601903383457698', '🇧🇾': '5280820319458707404',
    '🇬🇧': '5222398507851199882', '🇮🇳': '5224518800061245598', '🇧🇷': '5222300011366200403',
    '🇿🇲': '5224646626877911277', '🇾🇪': '5222300655611294950', '🏴󠁧󠁢󠁷󠁬󠁳󠁿': '5224431333052264232',
    '🇻🇮': '5224395882392201810', '🇻🇳': '5222359651282071925', '🇻🇦': '5222420266155520507',
    '🇻🇺': '5222126748090512778', '🇺🇾': '5222466849370813232', '🇦🇪': '5224565851427976312',
    '🇺🇬': '5222464040462200940', '🇹🇲': '5224256935905208951', '🇹🇳': '5221991375016310330',
    '🇹🇹': '5224391883777651050', '🇹🇬': '5222408051268532030', '🇹🇭': '5224638530864556281',
    '🇹🇿': '5224397364155923150', '🇹🇯': '5222217865821696536', '🇨🇭': '5224707263226194753',
    '🇸🇪': '5222201098269373561', '🇸🇿': '5224269666188274723', '🇸🇷': '5224567367551428669',
    '🇸🇩': '5224372990216514135', '🇪🇸': '5222024776976970940', '🇱🇰': '5224277294050192388',
    '🇸🇸': '5224618146949773268', '🇰🇷': '5222345550904439270', '🇿🇦': '5224696216570309138',
    '🇸🇴': '5222370504664428325', '🇸🇧': '5222290588207954120', '🇸🇮': '5224660718665607511',
    '🇸🇰': '5222401879400528047', '🇸🇬': '5224194023224257181', '🇸🇱': '5224420995065983217',
    '🇸🇨': '5224467496676896871', '🇷🇸': '5222145396838512729', '🇸🇳': '5224358988623130949',
    '🏴󠁧󠁢󠁳󠁣󠁴󠁿': '5224580312582861623', '🇸🇦': '5224698145010624573', '🇸🇹': '5221953304426198315',
    '🇼🇸': '5224660353593387686', '🇻🇨': '5224541228380467535', '🇱🇨': '5222000927023577045',
    '🇵🇸': '5222041677673282461', '🇷🇼': '5222449197055227754', '🇷🇴': '5222273794885826118',
    '🇶🇦': '5222225596762830469', '🇵🇷': '5224220115150582423', '🇵🇹': '5224404094369672274',
    '🇵🇭': '5222065042295376892', '🇵🇪': '5224482026551258766', '🇵🇾': '5222152565138929235',
    '🇵🇬': '5224500164198149905', '🇵🇦': '5222111719999945107', '🇵🇰': '5222370620628546719',
    '🇴🇲': '5224637061985742245', '🇳🇴': '5222396686785066306', '🇳🇬': '5224465228934163949',
    '🇳🇪': '5224723614166691638', '🇳🇿': '5224573595254009705', '🇳🇱': '5224516489368841614',
    '🇳🇵': '5222444378101925267', '🇳🇦': '5224690826386351746', '🇲🇿': '5222470388423864826',
    '🇲🇦': '5224530035695693965', '🇲🇪': '5224463399278096980', '🇲🇳': '5224192257992701543',
    '🇲🇨': '5221937224068640464', '🇲🇩': '5224216473018314447', '🇫🇲': '5222280486444873367',
    '🇲🇽': '5221971386238514431', '🇲🇺': '5224238347286752315', '🇲🇭': '5224538449536624503',
    '🏁': '5222206157740847357', '🇧🇲': '5222482143749353810', '🇲🇹': '5224731388057497620',
    '🇲🇱': '5224322352552096671', '🇲🇻': '5224393700548814960', '🇲🇾': '5224312886444174057',
    '🇰🇪': '5222089648163009103', '🇲🇬': '5222042605386217334', '🇲кин': '5222470435668505656',
    '🇱🇺': '5224499567197700690', '🇱🇹': '5224245902134226386', '🇱🇾': '5222194286451242896',
    '🇱🇷': '5221998371518034740', '🇱🇸': '5224245850594619415', '🇱🇧': '5222244425899455269',
    '🇱🇻': '5224401229626484931', '🇱🇦': '5224200843632324642', '🇰🇬': '5224388147156102493',
    '🇰🇼': '5221949726718442491', '🇽🇰': '5222197129719592160', '🇰🇮': '5224652244695134610',
    '🇯🇴': '5222292177345853436', '🇯🇲': '5222007034467074185', '🇮🇪': '5224257017509588818',
    '🇮🇹': '5222460101977190141', '🇮🇱': '5224720599099648709', '🇮🇶': '5221980268230882832',
    '🇮🇷': '5224374154152653367', '🇮🇩': '5224405893960969756', '🇮🇸': '5222063229819172521',
    '🇭🇺': '5224691998912427164', '🇭🇳': '5222229234600130045', '🇭🇹': '5224683146984831315',
    '🇬🇾': '5224570532942329532', '🇬🇼': '5224705704153066489', '🇬🇳': '5222337588035073000',
    '🇬🇹': '5222128302868672826', '🇬🇩': '5222234560359577687', '🇬🇷': '5222463490706389920',
    '🇬🇭': '5224511339703056124', '🇬🇪': '5222152195771742239', '🇬🇲': '5221949872747330159',
    '🇬🇦': '5224669733801963467', '🇫🇷': '5222029789203804982', '🇫🇮': '5224282903277482188',
    '🇫🇯': '5221962676044838178', '🇪🇹': '5224467805914542024', '🇪🇪': '5222195463272281351',
    '🇬🇶': '5222172811614762423', '🏴󠁧󠁢󠁥󠁮󠁧󠁿': '5224402728570071579', '🇸🇻': '5222434624231191289',
    '🇪🇬': '5224337131534559907', '🇪🇨': '5294034005388180164', '🇹🇱': '5224191188545840926',
    '🇩🇴': '5224515905253291409', '🇩🇲': '5224286412265763450', '🇩жих': '5222337489250824921',
    '🇩🇰': '5224203012590810589', '🇨🇾': '5222297215342490217', '🇭🇷': '5222431454545327055',
    '🇨🇷': '5221967765581085099', '🇨🇬': '5222453801260168022', '🇨🇩': '5224398158724871677',
    '🇰🇲': '5222398735484466247', '🇨🇴': '5224455152940886669', '🇨🇱': '5222350726340032308',
    '🇨🇿': '5222073533445714675', '🇹🇩': '5222060468155204001', '🇨🇫': '5222073662294733523',
    '🇨🇻': '5222347737042792258', '🇨🇦': '5222001124592071204', '🇨🇲': '5222270788408717651',
    '🇰🇭': '5224189882875785448', '🇧🇮': '5224490444687158452', '🇧🇫': '5222356541725749790',
    '🇧🇬': '5222092074819530668', '🇧🇳': '5224435958732042406', '🇧🇼': '5224288456670196085',
    '🇧🇦': '5224496092569155254', '🇧🇴': '5224675484763170798', '🇧🇹': '5224541065171710147',
    '🇧🇯': '5222024115552009151', '🇧🇿': '5224316292353241916', '🇧🇪': '5224513182244024630',
    '🇧🇧': '5222156533688712094', '🇧🇩': '5224407289825340729', '🇧 Bahrain': '5224492892818518587',
    '🇧🇸': '5224504167107668172', '🇦🇹': '5224520754271366661', '🇦🇺': '5224659803837574114',
    '🇦🇷': '5221980461504411710', '🇦🇬': '5224544866217765554', '🇦🇴': '5224379767674907895',
    '🇦🇩': '5221987861733061751', '🇩🇿': '5224260376174015500', '🇦🇱': '5224312057515486246',
    '🇦🇫': '5222096009009575868', '🇿🇼': '5222060442385397848', '🇫🇴': '5280985770188885026',
    '🇲🇶': '5281027792148909351', '🇨🇮':
  '5293991322003200135', '🇲🇷':
  '5294429743674840973', 
}

def get_country_info(number):
    number = str(number).strip()

    country_map = {
        "2376": ("🇨🇲", "Cameroon"), "2250": ("🇨🇮", "Ivory Coast"), "2613": ("🇲🇬", "Madagascar"),
        "4077": ("🇷🇴", "Romania"), "237": ("🇨🇲", "Cameroon"), "225": ("🇨🇮", "Ivory Coast"),
        "261": ("🇲🇬", "Madagascar"), "20": ("🇪🇬", "Egypt"), "27": ("🇿🇦", "South Africa"),
        "234": ("🇳🇬", "Nigeria"), "254": ("🇰🇪", "Kenya"), "233": ("🇬🇭", "Ghana"),
        "212": ("🇲🇦", "Morocco"), "213": ("🇩🇿", "Algeria"), "216": ("🇹🇳", "Tunisia"),
        "218": ("🇱🇾", "Libya"), "249": ("🇸🇩", "Sudan"), "251": ("🇪🇹", "Ethiopia"),
        "252": ("🇸🇴", "Somalia"), "253": ("🇩🇯", "Djibouti"), "255": ("🇹🇿", "Tanzania"),
        "256": ("🇺🇬", "Uganda"), "257": ("🇧🇮", "Burundi"), "258": ("🇲🇿", "Mozambique"),
        "260": ("🇿🇲", "Zambia"), "263": ("🇿🇼", "Zimbabwe"), "264": ("🇳🇦", "Namibia"),
        "265": ("🇲🇼", "Malawi"), "266": ("🇱🇸", "Lesotho"), "267": ("🇧🇼", "Botswana"),
        "268": ("🇸🇿", "Swaziland"), "269": ("🇰🇲", "Comoros"), "220": ("🇬🇲", "Gambia"),
        "221": ("🇸🇳", "Senegal"), "222": ("🇲🇷", "Mauritania"), "223": ("🇲🇱", "Mali"),
        "224": ("🇬🇳", "Guinea"), "226": ("🇧🇫", "Burkina Faso"), "227": ("🇳🇪", "Niger"),
        "228": ("🇹🇬", "Togo"), "229": ("🇧🇯", "Benin"), "230": ("🇲🇺", "Mauritius"),
        "231": ("🇱🇷", "Liberia"), "232": ("🇸🇱", "Sierra Leone"), "235": ("🇹🇩", "Chad"),
        "236": ("🇨🇫", "Central African Republic"), "238": ("🇨🇻", "Cape Verde"),
        "239": ("🇸🇹", "Sao Tome and Principe"), "240": ("🇬🇶", "Equatorial Guinea"),
        "241": ("🇬🇦", "Gabon"), "242": ("🇨🇬", "Congo"), "243": ("🇨🇩", "DR Congo"),
        "244": ("🇦🇴", "Angola"), "245": ("🇬🇼", "Guinea-Bissau"), "247": ("🇸🇭", "Saint Helena"),
        "248": ("🇸🇨", "Seychelles"), "250": ("🇷🇼", "Rwanda"), "290": ("🇸🇭", "Saint Helena"),
        "291": ("🇪🇷", "Eritrea"), "40": ("🇷🇴", "Romania"), "44": ("🇬🇧", "United Kingdom"),
        "33": ("🇫🇷", "France"), "49": ("🇩🇪", "Germany"), "39": ("🇮🇹", "Italy"),
        "34": ("🇪🇸", "Spain"), "31": ("🇳🇱", "Netherlands"), "32": ("🇧🇪", "Belgium"),
        "41": ("🇨🇭", "Switzerland"), "43": ("🇦🇹", "Austria"), "46": ("🇸🇪", "Sweden"),
        "47": ("🇳🇴", "Norway"), "45": ("🇩🇰", "Denmark"), "358": ("🇫🇮", "Finland"),
        "351": ("🇵🇹", "Portugal"), "353": ("🇮🇪", "Ireland"), "36": ("🇭🇺", "Hungary"),
        "48": ("🇵🇱", "Poland"), "380": ("🇺🇦", "Ukraine"), "370": ("🇱🇹", "Lithuania"),
        "371": ("🇱🇻", "Latvia"), "372": ("🇪🇪", "Estonia"), "373": ("🇲🇩", "Moldova"),
        "374": ("🇦🇲", "Armenia"), "375": ("🇧🇾", "Belarus"), "376": ("🇦🇩", "Andorra"),
        "377": ("🇲🇨", "Monaco"), "381": ("🇷🇸", "Serbia"), "382": ("🇲🇪", "Montenegro"),
        "385": ("🇭🇷", "Croatia"), "386": ("🇸🇮", "Slovenia"), "387": ("🇧🇦", "Bosnia and Herzegovina"),
        "389": ("🇲🇰", "North Macedonia"), "350": ("🇬🇮", "Gibraltar"), "352": ("🇱🇺", "Luxembourg"),
        "354": ("🇮🇸", "Iceland"), "355": ("🇦🇱", "Albania"), "356": ("🇲🇹", "Malta"),
        "357": ("🇨🇾", "Cyprus"), "359": ("🇧🇬", "Bulgaria"), "421": ("🇸🇰", "Slovakia"),
        "420": ("🇨🇿", "Czech Republic"), "298": ("🇫🇴", "Faroe Islands"), "299": ("🇬🇱", "Greenland"),
        "1": ("🇺🇸", "United States"), "7": ("🇷🇺", "Russia"), "91": ("🇮🇳", "India"),
        "92": ("🇵🇰", "Pakistan"), "880": ("🇧🇩", "Bangladesh"), "86": ("🇨🇳", "China"),
        "81": ("🇯🇵", "Japan"), "82": ("🇰🇷", "South Korea"), "84": ("🇻🇳", "Vietnam"),
        "66": ("🇹🇭", "Thailand"), "62": ("🇮🇩", "Indonesia"), "60": ("🇲🇾", "Malaysia"),
        "65": ("🇸🇬", "Singapore"), "63": ("🇵🇭", "Philippines"), "95": ("🇲🇲", "Myanmar"),
        "94": ("🇱🇰", "Sri Lanka"), "977": ("🇳🇵", "Nepal"), "93": ("🇦🇫", "Afghanistan"),
        "98": ("🇮🇷", "Iran"), "90": ("🇹🇷", "Turkey"), "964": ("🇮🇶", "Iraq"),
        "963": ("🇸🇾", "Syria"), "961": ("🇱🇧", "Lebanon"), "962": ("🇯🇴", "Jordan"),
        "965": ("🇰🇼", "Kuwait"), "966": ("🇸🇦", "Saudi Arabia"), "967": ("🇾🇲", "Yemen"),
        "968": ("🇴🇲", "Oman"), "971": ("🇦🇪", "United Arab Emirates"), "972": ("🇮🇱", "Israel"),
        "973": ("🇧🇭", "Bahrain"), "974": ("🇶🇦", "Qatar"), "994": ("🇦🇿", "Azerbaijan"),
        "995": ("🇬🇪", "Georgia"), "996": ("🇰🇬", "Kyrgyzstan"), "992": ("🇹🇯", "Tajikistan"),
        "993": ("🇹🇲", "Turkmenistan"), "998": ("🇺🇿", "Uzbekistan"), "855": ("🇰🇭", "Cambodia"),
        "856": ("🇱🇦", "Laos"), "976": ("🇲🇳", "Mongolia"), "850": ("🇰🇵", "North Korea"),
        "55": ("🇧🇷", "Brazil"), "52": ("🇲🇽", "Mexico"), "54": ("🇦🇷", "Argentina"),
        "57": ("🇨🇴", "Colombia"), "51": ("🇵🇪", "Peru"), "58": ("🇻🇪", "Venezuela"),
        "56": ("🇨🇱", "Chile"), "593": ("🇪🇨", "Ecuador"), "591": ("🇧🇴", "Bolivia"),
        "595": ("🇵🇾", "Paraguay"), "598": ("🇺🇾", "Uruguay"), "502": ("🇬🇹", "Guatemala"),
        "503": ("🇸🇻", "El Salvador"), "504": ("🇭🇳", "Honduras"), "506": ("🇨🇷", "Costa Rica"),
        "507": ("🇵🇦", "Panama"), "509": ("🇭🇹", "Haiti"), "501": ("🇧🇿", "Belize"),
        "61": ("🇦🇺", "Australia"), "64": ("🇳🇿", "New Zealand"), "675": ("🇵🇬", "Papua New Guinea"),
        "679": ("🇫🇯", "Fiji"), "1246": ("🇧🇧", "Barbados"), "1876": ("🇯🇲", "Jamaica"),
        "53": ("🇨🇺", "Cuba"), "592": ("🇬🇾", "Guyana")
    }

    clean_num = str(number).replace('+', '').replace(' ', '').replace('-', '').strip()
    sorted_prefixes = sorted(country_map.keys(), key=len, reverse=True)

    for prefix in sorted_prefixes:
        if clean_num.startswith(prefix):
            return country_map[prefix]

    return ("🌍", "Unknown")

# ==================== SERVICE DETECTION SECTION ====================

def detect_service(full_sms):
    if not full_sms:
        return "SMS SERVICE"

    sms_lower = full_sms.lower()

    service_keywords = {
        "facebook": "FACEBOOK", "fb": "FACEBOOK",
        "instagram": "INSTAGRAM", "insta": "INSTAGRAM",
        "tiktok": "TIKTOK",
        "twitter": "TWITTER", "x.com": "TWITTER",
        "snapchat": "SNAPCHAT", "snap": "SNAPCHAT",
        "whatsapp": "WHATSAPP",
        "telegram": "TELEGRAM",
        "discord": "DISCORD",
        "messenger": "MESSENGER",
        "linkedin": "LINKEDIN",
        "google": "GOOGLE", "gmail": "GOOGLE",
        "amazon": "AMAZON",
        "microsoft": "MICROSOFT", "outlook": "MICROSOFT",
        "yahoo": "YAHOO",
        "paypal": "PAYPAL",
        "binance": "BINANCE",
        "coinbase": "COINBASE",
        "spotify": "SPOTIFY",
        "netflix": "NETFLIX",
        "uber": "UBER",
        "apple": "APPLE", "icloud": "APPLE",
        "bkash": "BKASH",
        "nagad": "NAGAD",
        "stripe": "STRIPE",
        "line": "LINE",
        "wechat": "WECHAT",
        "viber": "VIBER",
        "signal": "SIGNAL",
        "pubg": "PUBG",
        "free fire": "FREE FIRE",
    }

    for keyword, service_name in sorted(service_keywords.items(), key=lambda x: len(x[0]), reverse=True):
        if keyword in sms_lower:
            return service_name

    return "SMS SERVICE"

# ==================== KEYBOARDS SECTION ====================
from telegram import KeyboardButton, ReplyKeyboardMarkup

def main_keyboard(user_id):
    keyboard = [
        [
            KeyboardButton(
                text="GET NUMBER",
                api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("phone")}
            )
        ],
        [
            KeyboardButton(
                text="SEARCH OTP",
                api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("search")}
            )
        ],
        [
            KeyboardButton(
                text="GET 2FA",
                api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("zap")}
            ),
            KeyboardButton(
                text="BALANCE",
                api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("money")}
            )
        ],
        [
            KeyboardButton(
                text="REFER AND EARN",
                api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("gift")}
            ),
            KeyboardButton(
                text="PROFILE",
                api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("profile")}
            )
        ],
        [
            KeyboardButton(
                text="LEADERBOARD",
                api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("trophy")}
            )
        ],
        [
            KeyboardButton(
                text="SUPPORT",
                api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("support")}
            )
        ]
    ]

    if is_admin(user_id):
        keyboard.append([
            KeyboardButton(
                text="ADMIN PANEL",
                api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("config")}
            )
        ])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

def cancel_keyboard():
    keyboard = [[
        KeyboardButton(
            text="CANCEL", 
            api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("cancel")}
        )
    ]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_main_keyboard(user_id):
    keyboard = []
    
    if is_full_admin(user_id):
        keyboard.append([
            KeyboardButton(text="CHANNEL CONTROL", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("config")}),
            KeyboardButton(text="SERVICE CONTROL", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("search")})
        ])
        keyboard.append([
            KeyboardButton(text="ADMIN MANAGE", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("profile")})
        ])
    else:
        # সাব-অ্যাডমিনের জন্য শুধু সার্ভিস কন্ট্রোল
        keyboard.append([KeyboardButton(text="SERVICE CONTROL", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("search")})])

    keyboard.extend([
        [KeyboardButton(text="USER MANAGEMENT", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("users")})],
        [KeyboardButton(text="SYSTEM CONFIGURATION", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("config")})],
        [KeyboardButton(text="BACK TO MAIN", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("back")})]
    ])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def user_management_keyboard():
    keyboard = [
        [KeyboardButton(text="SEND MESSAGE TO ALL USERS", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("broadcast")})],
        [KeyboardButton(text="ALL USER ID", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("id")})],
        [KeyboardButton(text="BAN USER LIST", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("ban_list")})],
        [KeyboardButton(text="ALL USER BALANCE", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("money")})],
        [KeyboardButton(text="BACK TO ADMIN", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("back")})]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def system_config_keyboard():
    keyboard = [
        [KeyboardButton(text="TODAY ALL STATUS", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("chart")}), 
         KeyboardButton(text="USER STATUS CHECK", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("user_check")})],
        [KeyboardButton(text="BAN USER", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("ban")}), 
         KeyboardButton(text="UNBAN USER", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("unban")})],
        [KeyboardButton(text="BAN USER LIST", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("ban_list")})],
        [KeyboardButton(text="REMOVE BALANCE", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("minus")}), 
         KeyboardButton(text="ADD BALANCE", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("plus")})],
        [KeyboardButton(text="BACK TO ADMIN", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("back")})]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def withdraw_method_keyboard():
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton(text="BKASH", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("cash")}), 
         KeyboardButton(text="NAGAD", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("money")})],
        [KeyboardButton(text="ROCKET", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': PREMIUM_EMOJIS.get("rocket_pay", "5377535110289576661")}), 
         KeyboardButton(text="BINANCE", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("bank")})],
        [KeyboardButton(text="CANCEL", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("cancel")})]
    ], resize_keyboard=True)
    return keyboard

# ==================== HELPER FUNCTIONS SECTION ====================

def format_balance(balance):
    return f"{balance:.2f}"

def extract_otp(text):
    if not text or text == "No Content":
        return "N/A"
    spaced_otp = re.search(r'\b(\d{3}\s\d{3})\b', text)
    if spaced_otp:
        return spaced_otp.group(1).replace(" ", "")
    match = re.search(r'\b(\d{4,8})\b', text)
    return match.group(1) if match else "N/A"

def normalize_number(num):
    return re.sub(r'\D', '', str(num))

def mask_number(num):
    if len(num) > 6:
        return f"{num[:4]}****{num[-6:]}"
    return num

def get_date_reset_time():
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day, 0, 0, 0)
    return today_midnight
# ==================== LANGUAGE & SHORTCODE HELPERS ====================
def detect_language(text):
    if not text: return "English"
    if re.search(r'[\u0980-\u09FF]', text): return "Bengali"
    if re.search(r'[\u0900-\u097F]', text): return "Hindi"
    return "English"

def get_country_shortcode(country_flag):
    try:
        if len(country_flag) == 2:
            return chr(ord(country_flag[0]) - 127397) + chr(ord(country_flag[1]) - 127397)
    except:
        pass
    return "XX"

def custom_mask_number(num, mask="••"):
    if len(num) > 6:
        return f"{num[:4]}{mask}{num[-4:]}"
    return num
# ======================================================================
def is_valid_bangladesh_number(number):
    number = re.sub(r'\D', '', str(number))
    return len(number) == 11 and number.startswith('01')

def is_range_request(param):
    return 'X' in param.upper()

def is_referral_request(param):
    return param.isdigit()
async def get_unjoined_channels(user_id, bot):
    settings = load_settings()
    channels = settings.get("force_channels", [])
    unjoined = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status in ['left', 'kicked', 'banned']:
                unjoined.append(ch)
        except Exception as e:
            print(f"Force Join Check Error for {ch}: {e}")
            unjoined.append(ch) # যদি চেক করতে না পারে, তারমানে জয়েন নেই
    return unjoined
# ==================== DATABASE FUNCTIONS SECTION ====================

def load_data(filename=USER_DATA_FILE):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data, filename=USER_DATA_FILE):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def get_user(uid):
    uid = str(uid)
    data = load_data()
    if uid not in data:
        data[uid] = {"user_id": uid, "balance": 0.0, "total_numbers": 0, "referral_count": 0}
        save_data(data)
    return data[uid]

async def update_db_balance(uid, amount):
    uid = str(uid)
    data = load_data()
    if uid in data:
        data[uid]["balance"] = round(data[uid].get("balance", 0.0) + amount, 2)
        save_data(data)
        return data[uid]["balance"]
    return 0.0

def get_all_users():
    data = load_data(USER_DATA_FILE)
    return list(data.keys()) if data else []

def user_exists(uid):
    data = load_data(USER_DATA_FILE)
    return str(uid) in data
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "force_channels": [], "otp_group": "Not Set", "log_forward": True, "main_channel": "Not Set", "hidden_services": [],
            "show_full_sms": False, "custom_mask": "••", "channel_url": "https://t.me/TG_FORGE0", "get_number_url": "https://t.me/Fastotpsuperbot",
            "full_admins": [], "sub_admins": [], "fetch_count": 3
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default_settings, f)
        return default_settings
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            if "hidden_services" not in data: data["hidden_services"] = []
            if "show_full_sms" not in data: data["show_full_sms"] = False
            if "custom_mask" not in data: data["custom_mask"] = "••"
            if "channel_url" not in data: data["channel_url"] = "https://t.me/TG_FORGE0"
            if "get_number_url" not in data: data["get_number_url"] = "https://t.me/Fastotpsuperbot"
            if "full_admins" not in data: data["full_admins"] = []
            if "sub_admins" not in data: data["sub_admins"] = []
            if "fetch_count" not in data: data["fetch_count"] = 3
            return data
    except:
        return {"force_channels": [], "otp_group": "Not Set", "log_forward": True, "main_channel": "Not Set", "hidden_services": [], "show_full_sms": False, "custom_mask": "••", "channel_url": "https://t.me/TG_FORGE0", "get_number_url": "https://t.me/Fastotpsuperbot", "full_admins": [], "sub_admins": [], "fetch_count": 3}

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_channel_control_panel():
    settings = load_settings()
    
    # ডাটাবেস থেকে বর্তমান ভ্যালুগুলো নেওয়া হচ্ছে
    fc = settings.get("force_channels", [])
    otp_g = settings.get("otp_group", "Not Set")
    main_ch = settings.get("main_channel", "Not Set")
    log_f_bool = settings.get("log_forward", True)
    sms_show_bool = settings.get("show_full_sms", False)
    mask = settings.get("custom_mask", "••")
    ch_url = settings.get("channel_url", "https://t.me/TG_FORGE0")
    bot_url = settings.get("get_number_url", "https://t.me/Fastotpsuperbot")
    f_count = settings.get("fetch_count", 3)

    log_f = "ON" if log_f_bool else "OFF"
    sms_show = "ON" if sms_show_bool else "OFF"

    text = (
        f"{p_emj('config', '⚙️')} <b>CHANNEL & BOT CONTROL</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{p_emj('dot_new', '🟢')} Force Join: {len(fc)}\n"
        f"{p_emj('dot_new', '🟢')} OTP Group: {otp_g}\n"
        f"{p_emj('dot_new', '🟢')} Main Channel: {main_ch}\n"
        f"{p_emj('dot_new', '🟢')} Log Forward: {log_f}\n"
        f"{p_emj('dot_new', '🟢')} Full SMS Show: {sms_show}\n"
        f"{p_emj('dot_new', '🟢')} Number Mask: {mask}\n"
        f"{p_emj('dot_new', '🟢')} Fetch Count: {f_count}"
    )

    # ডাইনামিক স্টাইল ফাংশন: সেট থাকলে সবুজ+টিক, না থাকলে নীল+প্লাস
    def btn_style(is_set):
        return ('success', e_id("tick_new")) if is_set else ('primary', e_id("add_new"))

    # বাটনগুলোর স্ট্যাটাস চেক
    style_fc, emj_fc = btn_style(len(fc) > 0)
    style_otp, emj_otp = btn_style(otp_g != "Not Set")
    style_ch_url, emj_ch_url = btn_style(ch_url != "https://t.me/TG_FORGE0")
    style_bot_url, emj_bot_url = btn_style(bot_url != "https://t.me/Fastotpsuperbot")
    style_sms, emj_sms = btn_style(sms_show_bool)
    style_mask, emj_mask = btn_style(mask != "••")
    style_main, emj_main = btn_style(main_ch != "Not Set")
    style_log, emj_log = btn_style(log_f_bool)
    style_num, emj_num = btn_style(f_count != 3) # 3 ডিফল্ট, চেঞ্জ হলে সবুজ হবে

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Add Force Join", callback_data="admin_add_fc", api_kwargs={'style': style_fc, 'icon_custom_emoji_id': emj_fc}),
            InlineKeyboardButton("Rem Force Join", callback_data="admin_rem_fc_list", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("rem_new")})
        ],
        [
            InlineKeyboardButton("Set OTP Group", callback_data="admin_set_otp", api_kwargs={'style': style_otp, 'icon_custom_emoji_id': emj_otp}),
            InlineKeyboardButton("Rem OTP Group", callback_data="admin_rem_otp", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("rem_new")})
        ],
        [
            InlineKeyboardButton("Channel URL", callback_data="admin_set_ch_url", api_kwargs={'style': style_ch_url, 'icon_custom_emoji_id': emj_ch_url}),
            InlineKeyboardButton("Bot URL", callback_data="admin_set_bot_url", api_kwargs={'style': style_bot_url, 'icon_custom_emoji_id': emj_bot_url})
        ],
        [
            InlineKeyboardButton("Toggle Full SMS", callback_data="admin_toggle_sms", api_kwargs={'style': style_sms, 'icon_custom_emoji_id': emj_sms}),
            InlineKeyboardButton("Set Custom Mask", callback_data="admin_set_mask", api_kwargs={'style': style_mask, 'icon_custom_emoji_id': emj_mask})
        ],
        [
            InlineKeyboardButton("Set Main Channel", callback_data="admin_set_main", api_kwargs={'style': style_main, 'icon_custom_emoji_id': emj_main}), 
            InlineKeyboardButton("Toggle Log", callback_data="admin_toggle_log", api_kwargs={'style': style_log, 'icon_custom_emoji_id': emj_log})
        ],
        [
            InlineKeyboardButton("Set Num Count", callback_data="admin_set_fetch_count", api_kwargs={'style': style_num, 'icon_custom_emoji_id': emj_num})
        ],
        [InlineKeyboardButton("Back", callback_data="admin_panel_back", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("back")})]
    ])
    return text, keyboard
def get_service_control_panel(page=0):
    settings = load_settings()
    hidden_svcs = settings.get("hidden_services", [])
    services = get_cached_services()
    
    if not services:
        return f"{p_emj('cancel', '❌')} No services found in cache. Please click GET NUMBER first to load services.", None
        
    items_per_page = 20
    total_pages = (len(services) - 1) // items_per_page + 1
    
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    current_services = services[start_idx:end_idx]
    
    keyboard = []
    for i in range(0, len(current_services), 2):
        row = []
        for j in range(2):
            if i + j < len(current_services):
                svc = current_services[i + j]
                sid = svc.get("sid", "")
                
                if sid in hidden_svcs:
                    btn_text = f"{sid} (Hidden)"
                    color = 'danger'
                    btn_emoji = e_id("cancel")
                else:
                    btn_text = f"{sid} (Shown)"
                    color = 'success'
                    btn_emoji = e_id("dot_new")  # <--- এখানে টিক মার্কের বদলে গোল জ্বলা ইমোজি দেওয়া হলো
                    
                row.append(InlineKeyboardButton(
                    text=btn_text, 
                    callback_data=f"togglesvc_{page}_{sid}",
                    api_kwargs={'style': color, 'icon_custom_emoji_id': btn_emoji}
                ))
        keyboard.append(row)
        
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("Prev", callback_data=f"svcpage_{page-1}", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("back")}))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Next", callback_data=f"svcpage_{page+1}", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("signal")}))
        
    if nav_row:
        keyboard.append(nav_row)
        
    keyboard.append([InlineKeyboardButton("Back", callback_data="admin_panel_back", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("back")})])
    
    text = (
        f"{p_emj('config', '⚙️')} <b>SERVICE CONTROL (Page {page+1}/{total_pages})</b>\n\n"
        f"<i>Click on a service to Hide {p_emj('cancel', '❌')} or Show {p_emj('dot_new', '🟢')} it to users.</i>"
    )
    return text, InlineKeyboardMarkup(keyboard)
        
# ==================== STATS FUNCTIONS SECTION ====================

def load_stats():
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

def add_number_taken(uid, count=1):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats:
        stats[uid] = {"numbers_taken": [], "otps_received": []}
    now = datetime.now().isoformat()
    for _ in range(count):
        stats[uid]["numbers_taken"].append(now)
    log_global_activity(uid, "NUMBER_TAKEN", {"count": count})
    save_stats(stats)

def add_otp_received(uid):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats:
        stats[uid] = {"numbers_taken": [], "otps_received": []}
    stats[uid]["otps_received"].append(datetime.now().isoformat())
    save_stats(stats)

def get_user_stats(uid):
    uid = str(uid)
    stats = load_stats()
    user_stats = stats.get(uid, {"numbers_taken": [], "otps_received": []})

    now = datetime.now()
    today_midnight = get_date_reset_time()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    numbers_taken = user_stats.get("numbers_taken", [])
    otps_received = user_stats.get("otps_received", [])

    today_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) >= today_midnight)
    today_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) >= today_midnight)
    last24h_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_24h)
    last24h_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) > last_24h)
    last7d_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_7d)
    last7d_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) > last7d)
    total_numbers = len(numbers_taken)
    total_otps = len(otps_received)

    return {
        "total_numbers": total_numbers, "total_otps": total_otps,
        "today_numbers": today_numbers, "today_otps": today_otps,
        "last24h_numbers": last24h_numbers, "last24h_otps": last24h_otps,
        "last7d_numbers": last7d_numbers, "last7d_otps": last7d_otps
    }

def log_global_activity(uid, action, details):
    if not os.path.exists(ACTIVITY_LOGS_FILE):
        with open(ACTIVITY_LOGS_FILE, "w") as f:
            json.dump([], f)
    try:
        with open(ACTIVITY_LOGS_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    now = datetime.now()
    logs.append({
        "uid": str(uid), "action": action, "details": details,
        "timestamp": now.isoformat(),
        "date": now.strftime("%d/%m/%Y"),
        "time": now.strftime("%H:%M:%S")
    })
    with open(ACTIVITY_LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def get_global_system_stats():
    stats = load_stats()
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day)
    last_7d = now - timedelta(days=7)
    total_n = total_o = today_n = today_o = seven_n = seven_o = 0
    for uid in stats:
        u = stats[uid]
        n_list = u.get("numbers_taken", [])
        o_list = u.get("otps_received", [])
        total_n += len(n_list)
        total_o += len(o_list)
        for t in n_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_n += 1
            if dt >= last_7d: seven_n += 1
        for t in o_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_o += 1
            if dt >= last_7d: seven_o += 1
    return today_n, today_o, seven_n, seven_o, total_n, total_o

# ==================== LEADERBOARD SECTION ====================

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    stats_data = load_stats()
    today_midnight = get_date_reset_time()
    user_data_all = load_data(USER_DATA_FILE)

    user_today_counts = []

    for uid_str, user_stats in stats_data.items():
        otps_received = user_stats.get("otps_received", [])
        today_count = 0
        for ts in otps_received:
            try:
                dt = datetime.fromisoformat(ts)
                if dt >= today_midnight:
                    today_count += 1
            except:
                continue
        if today_count > 0:
            name = user_data_all.get(uid_str, {}).get("full_name")
            if not name:
                name = user_data_all.get(uid_str, {}).get("username")
            if not name:
                name = f"User {uid_str}"
            user_today_counts.append((uid_str, today_count, html.escape(name)))

    user_today_counts.sort(key=lambda x: x[1], reverse=True)
    top10 = user_today_counts[:10]

    if not top10:
        msg = (
            f"<b>{p_emj('trophy', '🏆')} TOP 10 OTP LEADERBOARD {p_emj('trophy', '🏆')}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{p_emj('cancel', '❌')} আজ পর্যন্ত কেউ OTP পায়নি।\n"
        )
    else:
        msg = (
            f"<b>{p_emj('trophy', '🏆')} TOP 10 OTP RECEIVERS (TODAY) {p_emj('trophy', '🏆')}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        for idx, (uid_str, count, name) in enumerate(top10, 1):
            if idx == 1:
                medal = p_emj('medal1', '🥇')
            elif idx == 2:
                medal = p_emj('medal2', '🥈')
            elif idx == 3:
                medal = p_emj('medal3', '🥉')
            else:
                medal = f"{idx}️⃣"
            msg += f"{medal} <b>{name}</b>\n   {p_emj('key', '🔑')} <code>{count}</code> OTPs\n\n"
        msg += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{p_emj('chart', '📊')} <i>প্রতিদিন রাত ১২টায় রিসেট হয়</i>"
        )

    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=main_keyboard(uid))

# ==================== 2FA CODE GENERATOR SECTION ====================

def generate_2fa_code(secret_key):
    try:
        clean_secret = secret_key.replace(" ", "").strip()
        totp = pyotp.TOTP(clean_secret)
        otp = totp.now()
        return otp, clean_secret
    except:
        return None, None

async def get_2fa_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return
    context.user_data["mode"] = "get_2fa"
    await update.message.reply_text(
        f"{p_emj('zap', '⚡')} <b>GET 2FA CODE</b> {p_emj('zap', '⚡')}\n\n"
        f"<blockquote>{p_emj('key', '🔑')} ENTER YOUR 2FA SECRET KEY:</blockquote>",
        parse_mode="HTML"
    )

async def process_2fa_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    secret_key = update.message.text.strip()
    context.user_data["mode"] = None

    otp_code, clean_key = generate_2fa_code(secret_key)

    if otp_code is None:
        await update.message.reply_text(
            f"{p_emj('cancel', '❌')} <b>INVALID 2FA SECRET KEY</b>\n\n⚠️ Please send a valid base32 key.",
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )
        return

    now = datetime.now()
    final_msg = (
        f"{p_emj('success', '✅')} <b>2FA CODE GENERATED!</b>\n\n"
        f"<blockquote>{p_emj('key', '🔑')} KEY: <code>{clean_key}</code></blockquote>\n"
        f"<blockquote>{p_emj('user_check', '🔢')} CODE: <code>{otp_code}</code></blockquote>\n"
        f"<blockquote>{p_emj('wait', '⏳')} EXPIRES IN: 30 SECONDS</blockquote>\n"
        f"{p_emj('calendar', '📅')} {now.strftime('%d %B, %Y')} | {now.strftime('%I:%M %p')}"
    )
    await update.message.reply_text(final_msg, parse_mode="HTML")

# ==================== UI BUILDERS (2 COLUMNS & 1 COLUMN) ====================
def _build_services_keyboard(services):
    settings = load_settings()
    hidden_svcs = settings.get("hidden_services", [])
    
    # শুধু ভিজিবল সার্ভিসগুলো আলাদা করে নিচ্ছি (যাতে হাইড করাগুলো শো না হয়)
    visible_items = [(idx, svc) for idx, svc in enumerate(services) if svc.get("sid", "") not in hidden_svcs]
    
    buttons = []
    for i in range(0, len(visible_items), 2):
        row = []
        for j in range(2):
            if i + j < len(visible_items):
                orig_idx, svc = visible_items[i + j]
                sid = svc.get("sid", f"Service {orig_idx+1}")
                ranges = svc.get("ranges", [])
                
                emoji_id = get_service_emoji_id(sid)
                label = f"{sid} ({len(ranges)})"
                color = 'primary' if (i+j) % 2 == 0 else 'success'
                
                row.append(InlineKeyboardButton(
                    text=label, 
                    callback_data=f"svc_{orig_idx}", 
                    api_kwargs={'style': color, 'icon_custom_emoji_id': emoji_id}
                ))
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(
        text="CUSTOM RANGE", 
        callback_data="custom_range", 
        api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("config")}
    )])
    return InlineKeyboardMarkup(buttons)
def _build_countries_keyboard(ranges, service_idx):
    btns = []
    seen = {}
    clrs = ["success", "primary"]
    ci   = 0
    for i, r in enumerate(ranges):
        prefix = re.sub(r'[xX]+$', '', str(r)).strip()
        prefix_clean = re.sub(r'\D', '', prefix)
        flag_html, cname = get_country_info(prefix_clean)
        
        flag_emoji_id = CUSTOM_FLAG_IDS.get(flag_html, e_id("globe"))
        
        if cname not in seen:
            seen[cname] = True
            color = clrs[ci % len(clrs)]
            ci += 1
            btns.append([InlineKeyboardButton(
                text=cname, 
                callback_data=f"cty_{service_idx}_{cname[:15]}", 
                api_kwargs={'style': color, 'icon_custom_emoji_id': flag_emoji_id}
            )])
            if len(seen) >= 90:
                break
    
    btns.append([InlineKeyboardButton(
        text="BACK", 
        callback_data="back_services", 
        api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("back")}
    )])
    return InlineKeyboardMarkup(btns)

def _build_ranges_keyboard(ranges, service_idx, target_cname):
    btns = []
    clrs = ["success", "primary"]
    ci   = 0
    for i, r in enumerate(ranges):
        prefix = re.sub(r'[xX]+$', '', str(r)).strip()
        prefix_clean = re.sub(r'\D', '', prefix)
        flag_html, cname = get_country_info(prefix_clean)
        
        if cname[:15] == target_cname:
            color = clrs[ci % len(clrs)]
            ci += 1
            btns.append([InlineKeyboardButton(
                text=str(r), 
                callback_data=f"rng_{service_idx}_{i}", 
                api_kwargs={'style': color, 'icon_custom_emoji_id': e_id("signal")}
            )])
            if ci >= 90:
                break
    
    btns.append([InlineKeyboardButton(
        text="BACK", 
        callback_data=f"svc_{service_idx}", 
        api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("back")}
    )])
    return InlineKeyboardMarkup(btns)

def _build_ranges_keyboard(ranges, service_idx, target_cname):
    btns = []
    clrs = ["success", "primary"]
    ci   = 0
    for i, r in enumerate(ranges):
        prefix = re.sub(r'[xX]+$', '', str(r)).strip()
        prefix_clean = re.sub(r'\D', '', prefix)
        flag_html, cname = get_country_info(prefix_clean)
        
        if cname[:15] == target_cname:
            color = clrs[ci % len(clrs)]
            ci += 1
            btns.append([InlineKeyboardButton(
                text=str(r), 
                callback_data=f"rng_{service_idx}_{i}", 
                api_kwargs={'style': color, 'icon_custom_emoji_id': e_id("signal")}
            )])
            if ci >= 90: # টেলিগ্রামের বাটন লিমিট ক্রস হওয়া ঠেকাতে
                break
    
    btns.append([InlineKeyboardButton(
        text="BACK", 
        callback_data=f"svc_{service_idx}", 
        api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("back")}
    )])
    return InlineKeyboardMarkup(btns)

async def show_app_selection(update, context):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML")
        return

    services = get_cached_services()
    if not services:
        await _do_liveaccess_fetch()
        services = get_cached_services()

    if not services:
        await update.message.reply_text(f"{p_emj('warning', '⚠️')} সার্ভিস পাওয়া যাচ্ছে না!", parse_mode="HTML")
        return

    context.user_data["la_services"] = services
    keyboard = _build_services_keyboard(services)
    
    msg_text = (
        f"<blockquote>{p_emj('success', '☑️')} <b>FAST X OTP PANEL</b></blockquote>\n\n"
        f"Select a service below:"
    )
    
    await update.message.reply_text(
        msg_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )

# ==================== AUTO OTP MONITOR SECTION ====================

async def monitor_loop(app):
    while True:
        try:
            r = await client_async.get(f"{BASE_URL}/api/success-otp-info")
            try:
                res = r.json()
            except Exception:
                await asyncio.sleep(CHECK_INTERVAL)
                continue

            if "data" in res and "otps" in res["data"]:
                otps = res["data"]["otps"]
                paid_data = load_data(PAID_SMS_FILE)
                range_db = load_data(DATA_RANGE_FILE)
                paid_keys_set = set(paid_data.keys())
                processed_in_session = set()

                for otp in otps:
                    num = normalize_number(otp.get("number", ""))
                    full_sms = otp.get('message') or otp.get('otp') or otp.get('sms') or "No SMS Content"
                    otp_code = extract_otp(full_sms)
                    otp_id = str(otp.get("otp_id", ""))
                    sms_key = otp_id if otp_id else f"{num}_{full_sms}"

                    if (num in active_numbers and
                            sms_key not in paid_keys_set and
                            sms_key not in processed_in_session):

                        details = active_numbers[num]
                        paid_keys_set.add(sms_key)
                        processed_in_session.add(sms_key)
                        paid_data[sms_key] = {"uid": details["uid"], "otp": otp_code}

                        await update_db_balance(details["uid"], OTP_RATE)
                        add_otp_received(details["uid"])
                        log_global_activity(details["uid"], "OTP_RECEIVED", {"number": num, "otp": otp_code, "sms": full_sms})

                        country_flag, country_name = get_country_info(num)
                        service_name = details.get("sid", detect_service(full_sms)) 
                        clean_num = num.replace('+', '').strip()
                        full_number = f"+{clean_num}"
                        safe_otp_code = html.escape(str(otp_code))

                        flag_raw_id = CUSTOM_FLAG_IDS.get(country_flag, e_id("globe"))
                        premium_flag_html = f'<tg-emoji emoji-id="{flag_raw_id}">{country_flag}</tg-emoji>'
                        svc_emoji_id = get_service_emoji_id(service_name)
                        svc_emoji_html = f'<tg-emoji emoji-id="{svc_emoji_id}">📱</tg-emoji>'

                        # ==================== DYNAMIC URL & SETTINGS FIX ====================
                        settings = load_settings()
                        show_full_sms = settings.get("show_full_sms", False)
                        custom_mask = settings.get("custom_mask", "••")
                        
                        raw_ch_url = settings.get("channel_url", "https://t.me/TG_FORGE0")
                        ch_url = f"https://t.me/{raw_ch_url.replace('@', '')}" if "@" in raw_ch_url else raw_ch_url
                        if not ch_url.startswith("http"): ch_url = "https://t.me/TG_FORGE0"
                        
                        raw_bot_url = settings.get("get_number_url", "https://t.me/Fastotpsuperbot")
                        bot_url = f"https://t.me/{raw_bot_url.replace('@', '')}" if "@" in raw_bot_url else raw_bot_url
                        if not bot_url.startswith("http"): bot_url = "https://t.me/Fastotpsuperbot"

                        c_short = get_country_shortcode(country_flag)
                        lang = detect_language(full_sms)
                        custom_masked_num = f"+{custom_mask_number(clean_num, custom_mask)}"

                        # ==================== FULL SMS LOGIC FIX ====================
                        if show_full_sms:
                            display_sms = f"💬 {html.escape(full_sms)}"
                        else:
                            display_sms = f"💬 Code: <b>{safe_otp_code}</b>"

                        # ==================== চ্যাট ফরম্যাট ====================
                        user_msg = (
                            f"{premium_flag_html} <b>{c_short}</b> | {svc_emoji_html} <b>{service_name}</b>\n"
                            f"<code>{full_number}</code> | {p_emj('cash', '💵')} <b>{OTP_RATE:.2f} BDT</b>\n\n"
                            f"{display_sms}"
                        )
                        
                        user_buttons = InlineKeyboardMarkup([
                            [InlineKeyboardButton(
                                text=f"{safe_otp_code}",
                                copy_text=CopyTextButton(text=safe_otp_code),
                                api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("key")}
                            )]
                        ])

                        group_msg = (
                            f"{premium_flag_html} <b>{c_short}</b> | {svc_emoji_html} <b>{service_name}</b>\n"
                            f"<code>{custom_masked_num}</code> | {p_emj('search', '🔊')} <b>{lang}</b>\n\n"
                            f"{display_sms}"
                        )
                        
                        group_buttons = InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton(text="Channel", url=ch_url, api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("broadcast")}),
                                InlineKeyboardButton(text=f"{safe_otp_code}", copy_text=CopyTextButton(text=safe_otp_code), api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("key")})
                            ],
                            [
                                InlineKeyboardButton(text="Get Number", url=bot_url, api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("phone")})
                            ]
                        ])

                        try:
                            await app.bot.send_message(details["uid"], user_msg, parse_mode="HTML", reply_markup=user_buttons)
                        except Exception as e:
                            pass

                        otp_group_id = settings.get("otp_group", "Not Set")
                        if otp_group_id != "Not Set":
                            try:
                                target_chat = int(otp_group_id) if str(otp_group_id).lstrip('-').isdigit() else otp_group_id
                                await app.bot.send_message(target_chat, group_msg, parse_mode="HTML", reply_markup=group_buttons)
                            except Exception as e:
                                pass

                        save_data(paid_data, PAID_SMS_FILE)

                current_time = datetime.now()
                for num_key in list(active_numbers.keys()):
                    entry = active_numbers[num_key]
                    if 'timestamp' not in entry:
                        entry['timestamp'] = current_time
                    elif (current_time - entry['timestamp']).total_seconds() > 3600:
                        del active_numbers[num_key]

        except Exception as e:
            pass
        
        await asyncio.sleep(CHECK_INTERVAL)

# ==================== WORKER & API SECTION ====================

async def fetch_number_async(range_str):
    try:
        r = await client_async.post(
            f"{BASE_URL}/api/getnum",
            json={"range": range_str, "is_national": False}
        )
        data = r.json()
        d = data.get("data", {})
        if "full_number" in d:
            return {
                "number":  d["full_number"],
                "otp_now": bool(d.get("otp_now", False)),
                "otp":     d.get("otp"),
                "sms":     d.get("sms"),
            }
    except Exception as e:
        pass
    return None

async def fast_allocate_number(update, context, range_text, sid):
    # CallbackQuery থেকে সরাসরি ইউজার আইডি বের করা
    await process_numbers(update, context, range_text, count=3)

async def worker():
    while True:
        task = await request_queue.get()
        try:
            if task['type'] == 'process_numbers':
                await process_numbers(task['update'], task['context'], task['range_text'], task['count'])
            elif task['type'] == 'search_otp':
                await perform_otp_search(task['update'], task['context'], task['target_num'])
            elif task['type'] == 'auto_number':
                await process_auto_number(task['update'], task['context'], task['range_text'])
        except Exception as e:
            pass
        finally:
            request_queue.task_done()

# ==================== AUTO NUMBER FROM LINK / DEEP LINK ====================

async def process_auto_number(update, context, range_text):
    await process_numbers(update, context, range_text, count=3)
    
# ==================== USER PANEL — PROCESS NUMBERS ====================

async def process_numbers(update_or_query, context, range_text, count=3):
    # 1. Update/Query চেক ফিক্স (যেন বাটন ও টেক্সট দুটোতেই কাজ করে):
    try:
        if hasattr(update_or_query, 'effective_user') and update_or_query.effective_user:
            uid = update_or_query.effective_user.id
            chat_id = update_or_query.effective_chat.id
            msg_obj = update_or_query.effective_message
            is_query = False
        else:
            uid = update_or_query.from_user.id
            chat_id = update_or_query.message.chat_id
            msg_obj = update_or_query.message
            is_query = True
    except Exception as e:
        print(f"Error in process_numbers input: {e}")
        return

    if is_user_banned(uid):
        await context.bot.send_message(chat_id=chat_id, text=f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    search_text = f"{p_emj('search', '🔍')} SEARCHING . . ."
    if is_query and msg_obj:
        try:
            status_msg = await msg_obj.edit_text(search_text, parse_mode="HTML")
        except:
            status_msg = await context.bot.send_message(chat_id=chat_id, text=search_text, parse_mode="HTML")
    else:
        status_msg = await context.bot.send_message(chat_id=chat_id, text=search_text, parse_mode="HTML")

    try:
        # === FETCH DYNAMIC NUMBER COUNT ===
        settings = load_settings()
        actual_count = settings.get("fetch_count", 3)

        add_number_taken(uid, actual_count)
        last_range[uid] = range_text

        tasks = [fetch_number_async(range_text) for _ in range(actual_count)]
        results = await asyncio.gather(*tasks)
        valid_results = [r for r in results if r and r.get("number")]

        if not valid_results:
            await status_msg.edit_text(f"{p_emj('cancel', '❌')} NO NUMBERS FOUND. TRY A VALID RANGE.", parse_mode="HTML")
            return

        sid = context.user_data.get("la_sid", "Service") 

        num_entries = []
        for r in valid_results:
            clean_num = normalize_number(r["number"])
            if clean_num:
                active_numbers[clean_num] = {"uid": uid, "range": range_text, "timestamp": datetime.now(), "sid": sid}
                save_number_range_info(uid, clean_num, range_text)
                num_entries.append({
                    "num":     clean_num,
                    "otp_now": r.get("otp_now", False),
                    "otp":     r.get("otp"),
                    "sms":     r.get("sms"),
                })

        if not num_entries:
            await status_msg.edit_text(f"{p_emj('cancel', '❌')} NO NUMBERS FOUND. TRY A VALID RANGE.", parse_mode="HTML")
            return

        country_flag, country_name = get_country_info(num_entries[0]["num"])
        svc_emoji_id = get_service_emoji_id(sid)
        flag_raw_id = CUSTOM_FLAG_IDS.get(country_flag, e_id("globe"))

        keyboard_buttons = []
        for entry in num_entries:
            display_text = f"+{entry['num']}"
            keyboard_buttons.append([InlineKeyboardButton(
                text=display_text, 
                copy_text=CopyTextButton(text=display_text),
                api_kwargs={'style': 'success', 'icon_custom_emoji_id': svc_emoji_id}
            )])

        svc_idx = context.user_data.get("la_svc_idx", 0)
        action_row = [
            InlineKeyboardButton(text="Change Number", callback_data="same_range", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("config")}),
            InlineKeyboardButton(text="Change Country", callback_data=f"svc_{svc_idx}", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("globe")})
        ]
        keyboard_buttons.append(action_row)
        
        # === GET NUMBER DYNAMIC URL FIX ===
        raw_ch_url = settings.get("channel_url", "https://t.me/TG_FORGE0")
        ch_url = f"https://t.me/{raw_ch_url.replace('@', '')}" if str(raw_ch_url).startswith("@") else raw_ch_url
        if not ch_url.startswith("http"): ch_url = "https://t.me/TG_FORGE0"

        keyboard_buttons.append([
            InlineKeyboardButton(text="OTP View / OTP Group", url=ch_url, api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("broadcast")})
        ])

        final_text = (
            f"<blockquote><tg-emoji emoji-id=\"{svc_emoji_id}\">📱</tg-emoji> <b>Service : {html.escape(sid)}</b></blockquote>\n"
            f"<blockquote><tg-emoji emoji-id=\"{flag_raw_id}\">🌍</tg-emoji> <b>Country : {country_name} {country_flag}</b></blockquote>"
        )

        await status_msg.edit_text(final_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard_buttons))

    except Exception as e:
        print(f"Process Number Error: {e}")
        await status_msg.edit_text(f"{p_emj('cancel', '❌')} System Error: {str(e)}", parse_mode="HTML")

async def perform_otp_search(update, context, target_num):
    uid = str(update.effective_user.id)

    if is_user_banned(int(uid)):
        await update.message.reply_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML", reply_markup=main_keyboard(int(uid)))
        return

    status_msg = await update.message.reply_text(f"{p_emj('search', '🔍')} SEARCHING IN SERVER...", parse_mode="HTML")

    try:
        r = await client_async.get(f"{BASE_URL}/api/success-otp-info")
        res = r.json()

        if "data" in res and "otps" in res["data"]:
            all_otps = res["data"]["otps"]
            found_otps = [o for o in all_otps if normalize_number(o.get("number", "")) == target_num]

            if not found_otps:
                error_msg = (
                    f"━━━━━━━━━━━━━━━━━━\n{p_emj('cancel', '❌')} NO OTP FOUND\n━━━━━━━━━━━━━━━━━━\n\n"
                    f"{p_emj('phone', '📞')} NUMBER:\n`+{target_num}`\n\n{p_emj('wait', '⏳')} PLEASE TRY AGAIN LATER\n━━━━━━━━━━━━━━━━━━"
                )
                await status_msg.edit_text(error_msg, parse_mode="HTML")
                await update.message.reply_text(f"{p_emj('back', '🔙')} RETURNING TO MAIN MENU...", parse_mode="HTML", reply_markup=main_keyboard(int(uid)))
            else:
                await status_msg.delete()
                paid_data = load_data(PAID_SMS_FILE)

                for o in found_otps:
                    full_sms = o.get('message') or o.get('otp') or o.get('sms') or "No Content Found"
                    otp_code = extract_otp(full_sms)
                    otp_id = str(o.get("otp_id", ""))
                    sms_key = otp_id if otp_id else f"{target_num}_{full_sms}"

                    if sms_key in paid_data:
                        payment_status = f"{p_emj('cancel', '❌')} ALREADY PAID"
                    else:
                        await update_db_balance(uid, OTP_RATE)
                        add_otp_received(uid)
                        paid_data[sms_key] = {"uid": uid, "otp": otp_code}
                        payment_status = f"{p_emj('money', '💵')} ADD BALANCE FOR {OTP_RATE:.2f} BDT"

                    save_data(paid_data, PAID_SMS_FILE)
                    country_flag, country_name = get_country_info(target_num)
                    service_name = detect_service(full_sms)

                    msg = (
                        f"{p_emj('success', '✅')} <b>OTP FOUND!</b>\n\n"
                        f"<blockquote>{p_emj('globe', '🌍')} COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
                        f"<blockquote>{p_emj('phone', '📱')} SERVICE: <code>{service_name}</code></blockquote>\n"
                        f"<blockquote>{p_emj('phone', '📞')} NUMBER: <code>+{target_num}</code></blockquote>\n"
                        f"<blockquote>{p_emj('key', '🔑')} OTP: <code>{html.escape(otp_code)}</code></blockquote>\n\n"
                        f"<blockquote>{p_emj('mail', '📩')} FULL SMS:\n<code>{html.escape(str(full_sms))}</code></blockquote>\n\n"
                        f"<b>{payment_status}</b>"
                    )
                    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=main_keyboard(int(uid)))
        else:
            await status_msg.edit_text(f"{p_emj('cancel', '❌')} SERVER RETURNED AN ERROR.", parse_mode="HTML")
            await update.message.reply_text(f"{p_emj('back', '🔙')} Returning to Main Menu...", parse_mode="HTML", reply_markup=main_keyboard(int(uid)))

    except Exception as e:
        try:
            await status_msg.edit_text(f"{p_emj('cancel', '❌')} Error: {str(e)}", parse_mode="HTML")
        except:
            await update.message.reply_text(f"{p_emj('cancel', '❌')} Error: {str(e)}", parse_mode="HTML")
        await update.message.reply_text(f"{p_emj('back', '🔙')} Returning to Main Menu...", parse_mode="HTML", reply_markup=main_keyboard(int(uid)))

# ==================== REFER AND EARN SECTION ====================

async def refer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if is_user_banned(uid):
        await update.message.reply_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    user_data = get_user(uid)
    bot_info = await context.bot.get_me()

    referral_link = f"https://t.me/{bot_info.username}?start={uid}"
    successful_refers = get_referral_count(uid)
    total_reward = float(successful_refers) * REFERRAL_PRICE

    refer_msg = (
        f"{p_emj('gift', '🎁')} <b>REFER AND EARN SYSTEM</b> {p_emj('gift', '🎁')}\n\n"
        f"<blockquote>{p_emj('rocket', '🚀')} INVITE FRIENDS &amp; EARN {int(REFERRAL_PRICE)} BDT EACH! {p_emj('cash', '💸')}</blockquote>\n\n"
        f"<b>{p_emj('key', '🔗')} YOUR REFERRAL LINK:</b>\n"
        f"<blockquote><code>{referral_link}</code></blockquote>\n\n"
        f"<b>{p_emj('chart', '📊')} YOUR STATS:</b>\n"
        f"<blockquote>{p_emj('users', '👥')} TOTAL REFERS: {successful_refers}\n"
        f"{p_emj('money', '💰')} TOTAL EARNED: {format_balance(total_reward)} BDT</blockquote>\n\n"
        f"{p_emj('sparkle', '✨')} <b>SHARE LINK &amp; EARN MONEY!</b> {p_emj('sparkle', '✨')}"
    )

    await update.message.reply_text(
        refer_msg,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text="YOUR REFERRAL", callback_data=f"my_ref_{uid}", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("users")})
        ]])
    )

# ==================== WITHDRAW FUNCTIONS ====================

async def withdraw_method_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id

    if "CANCEL" in text.upper():
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text(f"{p_emj('cancel', '❌')} WITHDRAW CANCELLED", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    method_map = {"BKASH": "BKASH", "NAGAD": "NAGAD", "ROCKET": "ROCKET", "BINANCE": "BINANCE"}
    matched_method = None
    for key in method_map:
        if key in text.upper():
            matched_method = method_map[key]
            break

    if matched_method:
        balance = get_user(uid)['balance']
        context.user_data["withdraw_method"] = matched_method
        context.user_data["withdraw_mode"] = "amount"
        msg = (
            f"<blockquote>{p_emj('cash', '💸')} SEND YOUR AMOUNT!\n"
            f"{p_emj('money', '💵')} TOTAL BALANCE: {format_balance(balance)} BDT</blockquote>\n\n"
            f"<blockquote>{p_emj('chart', '📉')} MINIMUM WITHDRAW {MIN_WITHDRAW} BDT</blockquote>"
        )
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=cancel_keyboard())
    else:
        await update.message.reply_text(f"{p_emj('warning', '⚠️')} PLEASE SELECT A VALID PAYMENT METHOD!", parse_mode="HTML", reply_markup=withdraw_method_keyboard())

async def withdraw_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id

    if "CANCEL" in text.upper():
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text(f"{p_emj('cancel', '❌')} WITHDRAW CANCELLED", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    try:
        amount = float(text)
    except:
        await update.message.reply_text(f"{p_emj('warning', '⚠️')} PLEASE SEND A VALID AMOUNT!", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    balance = get_user(uid)['balance']
    if amount < MIN_WITHDRAW or amount > MAX_WITHDRAW:
        await update.message.reply_text(f"{p_emj('chart', '📉')} MIN: {MIN_WITHDRAW} BDT | MAX: {MAX_WITHDRAW} BDT", parse_mode="HTML", reply_markup=cancel_keyboard())
        return
    if amount > balance:
        await update.message.reply_text(f"{p_emj('ban', '🚫')} INSUFFICIENT BALANCE!", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    context.user_data["withdraw_amount"] = amount
    context.user_data["withdraw_mode"] = "number"
    await update.message.reply_text(
        f"{p_emj('phone', '📞')} PLEASE SEND YOUR PAYMENT NUMBER!\n\n<blockquote>{p_emj('user_check', '🔢')} EXAMPLE: 017XXXXXXXX</blockquote>",
        parse_mode="HTML", reply_markup=cancel_keyboard()
    )

async def withdraw_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id

    if "CANCEL" in text.upper():
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text(f"{p_emj('cancel', '❌')} WITHDRAW CANCELLED", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    if not is_valid_bangladesh_number(text):
        await update.message.reply_text(f"{p_emj('warning', '⚠️')} PLEASE SEND VALID NUMBER! 017XXXXXXXX", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    method = context.user_data.get("withdraw_method")
    amount = context.user_data.get("withdraw_amount")
    payment_number = text
    payment_id = generate_payment_id()

    context.user_data["temp_withdraw"] = {
        "method": method, "amount": amount,
        "number": payment_number, "payment_id": payment_id
    }

    msg = (
        f"{p_emj('sparkle', '✨')} <b>YOUR PAYMENT DETAILS!</b> {p_emj('sparkle', '✨')}\n\n"
        f"<blockquote>{p_emj('config', '📝')} METHOD: {method}\n"
        f"{p_emj('phone', '📞')} NUMBER: {payment_number}\n\n"
        f"{p_emj('success', '✅')} CORRECT → CONFIRM\n{p_emj('cancel', '❌')} WRONG → CANCEL</blockquote>"
    )
    await update.message.reply_text(
        msg, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text="CANCEL", callback_data="withdraw_cancel", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("cancel")}),
            InlineKeyboardButton(text="CONFIRM", callback_data="withdraw_confirm", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("success")})
        ]])
    )

async def process_withdraw_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()

    temp_data = context.user_data.get("temp_withdraw")
    if not temp_data:
        await query.message.reply_text(f"{p_emj('warning', '⚠️')} SESSION EXPIRED.", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    method = temp_data["method"]
    amount = temp_data["amount"]
    payment_number = temp_data["number"]
    payment_id = temp_data["payment_id"]

    new_balance = await update_db_balance(uid, -amount)
    wr = load_withdraw_requests()
    wr[str(payment_id)] = {
        "user_id": uid, "method": method, "amount": amount,
        "number": payment_number, "payment_id": payment_id,
        "status": "pending", "timestamp": datetime.now().isoformat()
    }
    save_withdraw_requests(wr)

    await query.message.edit_text(
        f"{p_emj('success', '✅')} <b>WITHDRAWAL REQUEST SUBMITTED</b> {p_emj('success', '✅')}\n\n"
        f"<blockquote>{p_emj('config', '📝')} METHOD: <code>{method}</code>\n"
        f"{p_emj('phone', '📞')} NUMBER: <code>{payment_number}</code>\n"
        f"{p_emj('money', '💰')} AMOUNT: <code>{format_balance(amount)} BDT</code>\n"
        f"{p_emj('id', '🆔')} ID: <code>{payment_id}</code></blockquote>",
        parse_mode="HTML"
    )
    await context.bot.send_message(uid, f"{p_emj('gift', '🎉')} <b>WITHDRAW REQUEST SUBMITTED!</b>", parse_mode="HTML", reply_markup=main_keyboard(uid))

    admin_msg = (
        f"{p_emj('success', '✅')} <b>NEW WITHDRAWAL REQUEST</b>\n\n"
        f"<blockquote>{p_emj('id', '🆔')} USER: <code>{uid}</code>\n"
        f"{p_emj('config', '📝')} METHOD: <code>{method}</code>\n"
        f"{p_emj('phone', '📞')} NUMBER: <code>{payment_number}</code>\n"
        f"{p_emj('money', '💰')} AMOUNT: <code>{format_balance(amount)} BDT</code>\n"
        f"{p_emj('id', '🆔')} ID: <code>{payment_id}</code></blockquote>"
    )
    admin_kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(text="REJECT", callback_data=f"admin_reject_{payment_id}", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("cancel")}),
        InlineKeyboardButton(text="APPROVE", callback_data=f"admin_approve_{payment_id}", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("success")})
    ]])
    for admin_id in ADMINS:
        try:
            await context.bot.send_message(admin_id, admin_msg, parse_mode="HTML", reply_markup=admin_kb)
        except Exception as e:
            print(f"Admin notify fail {admin_id}: {e}")

    context.user_data["temp_withdraw"] = None
    context.user_data["withdraw_mode"] = None

async def process_withdraw_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    context.user_data["temp_withdraw"] = None
    context.user_data["withdraw_mode"] = None
    await query.message.edit_text(f"{p_emj('cancel', '❌')} WITHDRAW CANCELLED", parse_mode="HTML")
    await context.bot.send_message(uid, f"{p_emj('sparkle', '🔹')} PLEASE USE THE BUTTONS BELOW:", parse_mode="HTML", reply_markup=main_keyboard(uid))

# ==================== ADMIN PANEL - WITHDRAW APPROVAL ====================

async def admin_approve_withdraw(update, context, payment_id):
    query = update.callback_query
    await query.answer()
    wr = load_withdraw_requests()
    if payment_id not in wr:
        await query.message.reply_text(f"{p_emj('warning', '⚠️')} REQUEST NOT FOUND!", parse_mode="HTML")
        return
    rd = wr[payment_id]
    uid = rd["user_id"]
    method = rd["method"]
    amount = rd["amount"]
    payment_number = rd["number"]
    wr[payment_id]["status"] = "approved"
    save_withdraw_requests(wr)

    try:
        await context.bot.send_message(
            uid,
            f"{p_emj('gift', '🎉')} <b>WITHDRAWAL APPROVED!</b>\n\n"
            f"<blockquote>{p_emj('config', '📝')} METHOD: <code>{method}</code>\n"
            f"{p_emj('phone', '📞')} NUMBER: <code>{payment_number}</code>\n"
            f"{p_emj('money', '💰')} AMOUNT: <code>{format_balance(amount)} BDT</code></blockquote>",
            parse_mode="HTML"
        )
    except:
        pass
    await query.message.edit_text(f"{p_emj('success', '✅')} APPROVED | User: {uid} | Amount: {format_balance(amount)} BDT", parse_mode="HTML")

async def admin_reject_withdraw(update, context, payment_id):
    query = update.callback_query
    await query.answer()
    wr = load_withdraw_requests()
    if payment_id not in wr:
        await query.message.reply_text(f"{p_emj('warning', '⚠️')} REQUEST NOT FOUND!", parse_mode="HTML")
        return
    rd = wr[payment_id]
    uid = rd["user_id"]
    amount = rd["amount"]
    wr[payment_id]["status"] = "rejected"
    save_withdraw_requests(wr)

    try:
        await context.bot.send_message(uid, f"{p_emj('cancel', '❌')} <b>WITHDRAWAL REQUEST REJECTED</b>\n\nContact admin for more info.", parse_mode="HTML")
    except:
        pass
    await query.message.edit_text(f"{p_emj('cancel', '❌')} REJECTED | User: {uid} | Amount: {format_balance(amount)} BDT", parse_mode="HTML")

# ==================== ADMIN PANEL - BALANCE MANAGEMENT ====================

async def admin_add_balance_start(update, context):
    context.user_data["add_balance_mode"] = True
    context.user_data["remove_balance_mode"] = False
    await update.message.reply_text(f"{p_emj('money', '💰')} SEND USER ID TO ADD BALANCE:", parse_mode="HTML")

async def admin_remove_balance_start(update, context):
    context.user_data["remove_balance_mode"] = True
    context.user_data["add_balance_mode"] = False
    await update.message.reply_text(f"{p_emj('cash', '💸')} SEND USER ID TO REMOVE BALANCE:", parse_mode="HTML")

async def process_add_balance_user(update, context):
    uid_to_add = update.message.text.strip()
    if not uid_to_add.isdigit():
        await update.message.reply_text(f"{p_emj('cancel', '❌')} INVALID USER ID!", parse_mode="HTML")
        return
    uid_to_add_int = int(uid_to_add)
    if not user_exists(uid_to_add_int):
        await update.message.reply_text(f"{p_emj('cancel', '❌')} USER NOT FOUND!", parse_mode="HTML")
        context.user_data["add_balance_mode"] = False
        return
    context.user_data["pending_add_user"] = uid_to_add_int
    await update.message.reply_text(f"{p_emj('cash', '💵')} SEND AMOUNT TO ADD:", parse_mode="HTML")

async def process_remove_balance_user(update, context):
    uid_to_remove = update.message.text.strip()
    if not uid_to_remove.isdigit():
        await update.message.reply_text(f"{p_emj('cancel', '❌')} INVALID USER ID!", parse_mode="HTML")
        return
    uid_to_remove_int = int(uid_to_remove)
    if not user_exists(uid_to_remove_int):
        await update.message.reply_text(f"{p_emj('cancel', '❌')} USER NOT FOUND!", parse_mode="HTML")
        context.user_data["remove_balance_mode"] = False
        return
    context.user_data["pending_remove_user"] = uid_to_remove_int
    await update.message.reply_text(f"{p_emj('cash', '💸')} SEND AMOUNT TO REMOVE:", parse_mode="HTML")

async def process_add_balance_amount(update, context):
    try:
        amount = float(update.message.text.strip())
        if amount <= 0: raise ValueError
    except:
        await update.message.reply_text(f"{p_emj('cancel', '❌')} INVALID AMOUNT!", parse_mode="HTML")
        return
    uid = context.user_data.get("pending_add_user")
    if not uid:
        context.user_data["add_balance_mode"] = False
        await update.message.reply_text(f"{p_emj('warning', '⚠️')} SESSION EXPIRED.", parse_mode="HTML")
        return
    old_balance = get_user(uid).get("balance", 0)
    new_balance = await update_db_balance(uid, amount)
    await update.message.reply_text(
        f"{p_emj('success', '✅')} <b>ADD BALANCE SUCCESSFUL</b>\n{p_emj('id', '🆔')} USER: <code>{uid}</code>\n"
        f"{p_emj('money', '💰')} ADDED: <code>{format_balance(amount)} BDT</code>\n"
        f"{p_emj('chart', '📈')} NEW BALANCE: <code>{format_balance(new_balance)} BDT</code>",
        parse_mode="HTML"
    )
    try:
        await context.bot.send_message(uid, f"{p_emj('gift', '🎉')} ADMIN ADDED <code>{format_balance(amount)} BDT</code> TO YOUR ACCOUNT!\n{p_emj('cash', '💵')} NEW BALANCE: <code>{format_balance(new_balance)} BDT</code>", parse_mode="HTML")
    except:
        pass
    context.user_data["add_balance_mode"] = False
    context.user_data["pending_add_user"] = None

async def process_remove_balance_amount(update, context):
    try:
        amount = float(update.message.text.strip())
        if amount <= 0: raise ValueError
    except:
        await update.message.reply_text(f"{p_emj('cancel', '❌')} INVALID AMOUNT!", parse_mode="HTML")
        return
    uid = context.user_data.get("pending_remove_user")
    if not uid:
        context.user_data["remove_balance_mode"] = False
        await update.message.reply_text(f"{p_emj('warning', '⚠️')} SESSION EXPIRED.", parse_mode="HTML")
        return
    old_balance = get_user(uid).get("balance", 0)
    if amount > old_balance:
        await update.message.reply_text(f"{p_emj('cancel', '❌')} INSUFFICIENT BALANCE! Current: {format_balance(old_balance)} BDT", parse_mode="HTML")
        context.user_data["remove_balance_mode"] = False
        context.user_data["pending_remove_user"] = None
        return
    new_balance = await update_db_balance(uid, -amount)
    await update.message.reply_text(
        f"{p_emj('success', '✅')} <b>REMOVE BALANCE SUCCESSFUL</b>\n{p_emj('id', '🆔')} USER: <code>{uid}</code>\n"
        f"{p_emj('cash', '💸')} REMOVED: <code>{format_balance(amount)} BDT</code>\n"
        f"{p_emj('chart', '📉')} NEW BALANCE: <code>{format_balance(new_balance)} BDT</code>",
        parse_mode="HTML"
    )
    try:
        await context.bot.send_message(uid, f"{p_emj('warning', '⚠️')} ADMIN REMOVED <code>{format_balance(amount)} BDT</code> FROM YOUR ACCOUNT!\n{p_emj('cash', '💵')} NEW BALANCE: <code>{format_balance(new_balance)} BDT</code>", parse_mode="HTML")
    except:
        pass
    context.user_data["remove_balance_mode"] = False
    context.user_data["pending_remove_user"] = None

# ==================== ADMIN PANEL - BAN/UNBAN ====================

async def admin_ban_user_start(update, context):
    context.user_data["admin_ban_mode"] = True
    context.user_data["admin_unban_mode"] = False
    await update.message.reply_text(f"{p_emj('ban', '🚫')} SEND TELEGRAM ID TO BAN USER:", parse_mode="HTML")

async def admin_unban_user_start(update, context):
    context.user_data["admin_unban_mode"] = True
    context.user_data["admin_ban_mode"] = False
    await update.message.reply_text(f"{p_emj('unban', '🔓')} SEND TELEGRAM ID TO UNBAN USER:", parse_mode="HTML")

async def process_ban_user(update, context):
    uid_to_ban = update.message.text.strip()
    if not uid_to_ban.isdigit():
        await update.message.reply_text(f"{p_emj('cancel', '❌')} INVALID USER ID!", parse_mode="HTML")
        return
    uid_to_ban_int = int(uid_to_ban)
    if not user_exists(uid_to_ban_int):
        await update.message.reply_text(f"{p_emj('cancel', '❌')} USER NOT FOUND!", parse_mode="HTML")
        context.user_data["admin_ban_mode"] = False
        return
    if is_user_banned(uid_to_ban_int):
        await update.message.reply_text(f"{p_emj('warning', '⚠️')} USER IS ALREADY BANNED!", parse_mode="HTML")
        context.user_data["admin_ban_mode"] = False
        return
    ban_user(uid_to_ban_int)
    try:
        await context.bot.send_message(uid_to_ban_int, f"{p_emj('ban', '🚫')} <b>YOU HAVE BEEN BANNED</b>\n{p_emj('phone', '📞')} Contact support.", parse_mode="HTML")
    except:
        pass
    await update.message.reply_text(f"{p_emj('success', '✅')} USER <code>{uid_to_ban}</code> BANNED!", parse_mode="HTML", reply_markup=system_config_keyboard())
    context.user_data["admin_ban_mode"] = False

async def process_unban_user(update, context):
    uid_to_unban = update.message.text.strip()
    if not uid_to_unban.isdigit():
        await update.message.reply_text(f"{p_emj('cancel', '❌')} INVALID USER ID!", parse_mode="HTML")
        return
    uid_to_unban_int = int(uid_to_unban)
    if not is_user_banned(uid_to_unban_int):
        await update.message.reply_text(f"{p_emj('warning', '⚠️')} THIS USER IS NOT BANNED!", parse_mode="HTML")
        context.user_data["admin_unban_mode"] = False
        return
    unban_user(uid_to_unban_int)
    try:
        await context.bot.send_message(uid_to_unban_int, f"{p_emj('success', '✅')} <b>YOU HAVE BEEN UNBANNED!</b> Use /start", parse_mode="HTML")
    except:
        pass
    await update.message.reply_text(f"{p_emj('success', '✅')} USER <code>{uid_to_unban}</code> UNBANNED!", parse_mode="HTML", reply_markup=system_config_keyboard())
    context.user_data["admin_unban_mode"] = False

async def show_banned_users_list(update, context):
    banned_list = load_banned_users()
    if not banned_list:
        await update.message.reply_text(f"{p_emj('ban_list', '📜')} NO BANNED USERS.", parse_mode="HTML", reply_markup=system_config_keyboard())
        return
    text = f"{p_emj('ban_list', '📜')} <b>BANNED USER LIST</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, uid in enumerate(banned_list, 1):
        text += f"{i}. <code>{uid}</code>\n"
    text += f"\n{p_emj('chart', '📊')} Total: {len(banned_list)}"
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=system_config_keyboard())

# ==================== MESSAGE HANDLER SECTION ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    uid = update.effective_user.id
    
    # === NEW: CHAT SHARED (OTP GROUP SELECT) ===
    if update.message.chat_shared:
        if context.user_data.get("admin_state") == "wait_for_otp_group":
            chat_id = update.message.chat_shared.chat_id
            settings = load_settings()
            settings["otp_group"] = str(chat_id)
            save_settings(settings)
            
            context.user_data["admin_state"] = None
            
            await update.message.reply_text(
                f"✅ <b>OTP Group successfully set to:</b> <code>{chat_id}</code>", 
                parse_mode="HTML", 
                reply_markup=admin_main_keyboard(uid)
            )
            
            panel_text, kb = get_channel_control_panel()
            await update.message.reply_text(panel_text, parse_mode="HTML", reply_markup=kb)
        return

    text = update.message.text.strip() if update.message.text else ""
    
    # Cancel handling for group set
    if text == "❌ CANCEL" and context.user_data.get("admin_state") == "wait_for_otp_group":
        context.user_data["admin_state"] = None
        await update.message.reply_text("❌ Cancelled.", reply_markup=admin_main_keyboard(uid))
        panel_text, kb = get_channel_control_panel()
        await update.message.reply_text(panel_text, parse_mode="HTML", reply_markup=kb)
        return

    if not text:
        return
        
    # === FORCE JOIN CHECK FOR ALL TEXT MESSAGES ===
    if not is_admin(uid):
        unjoined_channels = await get_unjoined_channels(uid, context.bot)
        # ... (আপনার বাকি কোড যেমন ছিল তেমনই থাকবে)
        if unjoined_channels:
            await update.message.reply_text("❌ Please /start and verify your channel memberships first!")
            return

    # === ADMIN STATE HANDLING (CHANNEL CONTROL) ===
    if is_admin(uid) and context.user_data.get("admin_state"):
        state = context.user_data.pop("admin_state")
        settings = load_settings()
        
        if state == "add_fc":
            if not text.startswith("@"):
                await update.message.reply_text("❌ Username must start with @. Try again from Channel Control.")
            else:
                if text not in settings["force_channels"]:
                    settings["force_channels"].append(text)
                save_settings(settings)
                await update.message.reply_text(f"✅ Added {text} to Force Join.")
        
        elif state == "set_otp":
            settings["otp_group"] = text
            save_settings(settings)
            await update.message.reply_text(f"✅ OTP Group set to: {text}")
            
        elif state == "set_main":
            settings["main_channel"] = text
            save_settings(settings)
            await update.message.reply_text(f"✅ Main Channel set to: {text}")
            
        elif state == "set_ch_url":
            settings["channel_url"] = text
            save_settings(settings)
            await update.message.reply_text(f"✅ Channel URL set to: {text}")
            
        elif state == "set_bot_url":
            settings["get_number_url"] = text
            save_settings(settings)
            await update.message.reply_text(f"✅ Bot URL set to: {text}")
            
        elif state == "set_mask":
            settings["custom_mask"] = text
            save_settings(settings)
            await update.message.reply_text(f"✅ Custom Mask set to: {text}")
        elif state == "set_fetch_count":
            if not text.isdigit() or int(text) < 1 or int(text) > 10:
                await update.message.reply_text(f"{p_emj('cancel', '❌')} Invalid count! Enter between 1-10.", parse_mode="HTML")
                return
            settings["fetch_count"] = int(text)
            save_settings(settings)
            await update.message.reply_text(f"{p_emj('success', '✅')} Default number fetch count set to: {text}", parse_mode="HTML")            
        elif state == "wait_for_admin_id":
            if not text.isdigit():
                await update.message.reply_text(f"{p_emj('cancel', '❌')} Invalid ID! Numbers only.", parse_mode="HTML")
                return
            new_admin_id = int(text)
            admin_type = context.user_data.get("new_admin_type")
            settings = load_settings()
            if admin_type == "full":
                if new_admin_id not in settings["full_admins"]: settings["full_admins"].append(new_admin_id)
                msg = f"{p_emj('success', '✅')} Full Admin Added Successfully!"
            else:
                if new_admin_id not in settings["sub_admins"]: settings["sub_admins"].append(new_admin_id)
                msg = f"{p_emj('success', '✅')} Sub-Admin Added Successfully!"
            save_settings(settings)
            await update.message.reply_text(msg, parse_mode="HTML")
            return

        elif state == "remove_admin":
            if not text.isdigit():
                await update.message.reply_text(f"{p_emj('cancel', '❌')} Invalid ID! Numbers only.", parse_mode="HTML")
                return
            target_id = int(text)
            settings = load_settings()
            removed = False
            
            if target_id in settings.get("full_admins", []):
                settings["full_admins"].remove(target_id)
                removed = True
            if target_id in settings.get("sub_admins", []):
                settings["sub_admins"].remove(target_id)
                removed = True
                
            if removed:
                save_settings(settings)
                await update.message.reply_text(f"{p_emj('success', '✅')} Admin removed successfully!", parse_mode="HTML")
            else:
                await update.message.reply_text(f"{p_emj('warning', '⚠️')} ID not found in admin list.", parse_mode="HTML")
                
            context.user_data["admin_state"] = None
            return
# এখানেও রিটার্ন হচ্ছে তাই নিচের প্যানেল আর আসবে না
            
        # === নিচের টুকু শুধু চ্যানেল কন্ট্রোলের বাটনগুলোর জন্য ===
        # প্যানেল আবার শো করানোর জন্য
        panel_text, kb = get_channel_control_panel()
        await update.message.reply_text(panel_text, parse_mode="HTML", reply_markup=kb)
        return
    # === ADMIN REPLY KEYBOARD: CHANNEL CONTROL ===
    if text == "CHANNEL CONTROL" and is_admin(uid):
        panel_text, kb = get_channel_control_panel()
        await update.message.reply_text(panel_text, parse_mode="HTML", reply_markup=kb)
        return
    # === ADMIN REPLY KEYBOARD: SERVICE CONTROL ===
    if text == "SERVICE CONTROL" and is_admin(uid):
        text_msg, kb = get_service_control_panel(0)
        if kb:
            await update.message.reply_text(text_msg, parse_mode="HTML", reply_markup=kb)
        else:
            await update.message.reply_text(text_msg, parse_mode="HTML")
        return
    # Withdraw flow
    if context.user_data.get("withdraw_mode") == "select_method":
        await withdraw_method_selected(update, context)
        return
    if context.user_data.get("withdraw_mode") == "amount":
        await withdraw_amount_received(update, context)
        return
    if context.user_data.get("withdraw_mode") == "number":
        await withdraw_number_received(update, context)
        return

    # Admin balance
    if context.user_data.get("add_balance_mode") and is_admin(uid):
        if context.user_data.get("pending_add_user"):
            await process_add_balance_amount(update, context)
        else:
            await process_add_balance_user(update, context)
        return
    if context.user_data.get("remove_balance_mode") and is_admin(uid):
        if context.user_data.get("pending_remove_user"):
            await process_remove_balance_amount(update, context)
        else:
            await process_remove_balance_user(update, context)
        return

    # Admin ban/unban
    if context.user_data.get("admin_ban_mode") and is_admin(uid):
        await process_ban_user(update, context)
        return
    if context.user_data.get("admin_unban_mode") and is_admin(uid):
        await process_unban_user(update, context)
        return

# CUSTOM RANGE — user sent a range text
    if context.user_data.get("mode") == "custom_range":
        context.user_data["mode"] = None
        range_text = text.strip() # .upper() Removed for correct API search
        
        # চেক করছি যে রেঞ্জের মধ্যে অন্তত একটা সংখ্যা আছে কি না
        if not re.search(r'\d', range_text):
            await update.message.reply_text(
                f"{p_emj('cancel', '❌')} <b>INVALID RANGE!</b>\n\n"
                f"<blockquote>সঠিক উদাহরণ: <code>234XXX</code> বা <code>234</code></blockquote>",
                parse_mode="HTML",
                reply_markup=main_keyboard(uid)
            )
            return
            
        # যদি ভ্যালিড রেঞ্জ হয়, তাহলে queue তে প্রসেস করার জন্য পাঠাচ্ছি
        await request_queue.put({
            'type': 'process_numbers',
            'update': update,
            'context': context,
            'range_text': range_text,
            'count': load_settings().get("fetch_count", 3) # অ্যাডমিন প্যানেল থেকে সেট করা কাউন্ট অনুযায়ী
        })
        return

    # Ban check
    if not is_admin(uid) and is_user_banned(uid):
        await update.message.reply_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    # Cancel
    if "CANCEL" in text.upper():
        context.user_data.clear()
        await update.message.reply_text(f"{p_emj('cancel', '❌')} CANCELLED", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    # Main menu buttons
    if "PROFILE" in text.upper():
        user_data = get_user(uid)
        stats = get_user_stats(uid)
        user = update.effective_user
        full_name = html.escape(user.full_name)
        username = html.escape(user.username or "No username")
        profile_text = (
            f"{p_emj('profile', '👤')} <b>YOUR PROFILE</b>\n\n"
            f"<blockquote>{p_emj('sparkle', '🏷️')} NAME: <b>{full_name}</b></blockquote>\n"
            f"<blockquote>{p_emj('id', '🆔')} USERNAME: @{username}</blockquote>\n"
            f"<blockquote>{p_emj('key', '🗝️')} TELEGRAM ID: <code>{uid}</code></blockquote>\n\n"
            f"<blockquote>{p_emj('money', '💵')} BALANCE: <b>{format_balance(user_data.get('balance', 0))} BDT</b></blockquote>\n\n"
            f"{p_emj('sparkle', '✨')} <b>TODAY</b>\n"
            f"<blockquote>{p_emj('phone', '📱')} NUMBERS: {stats['today_numbers']}\n{p_emj('key', '🔑')} OTPS: {stats['today_otps']}</blockquote>\n\n"
            f"{p_emj('fire', '🔥')} <b>LAST 7 DAYS</b>\n"
            f"<blockquote>{p_emj('phone', '📱')} NUMBERS: {stats['last7d_numbers']}\n{p_emj('key', '🔑')} OTPS: {stats['last7d_otps']}</blockquote>\n\n"
            f"{p_emj('globe', '🌐')} <b>ALL TIME</b>\n"
            f"<blockquote>{p_emj('phone', '📱')} NUMBERS: {stats['total_numbers']}\n{p_emj('key', '🔑')} OTPS: {stats['total_otps']}</blockquote>"
        )
        await update.message.reply_text(profile_text, parse_mode="HTML")
        return

    if "BALANCE" in text.upper() and "ADD" not in text.upper() and "REMOVE" not in text.upper() and "USER" not in text.upper():
        balance = get_user(uid)['balance']
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="WITHDRAW", callback_data="withdraw_start", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("money")})
        ]])
        await update.message.reply_text(
            f"{p_emj('money', '💰')} <b>YOUR CURRENT BALANCE</b>\n\n"
            f"<blockquote>{p_emj('cash', '💵')} TOTAL: <b>{format_balance(balance)} BDT</b></blockquote>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    if "REFER AND EARN" in text.upper():
        await refer_command(update, context)
        return

    # SEARCH OTP
    if "SEARCH OTP" in text.upper():
        context.user_data["mode"] = "search_otp"
        await update.message.reply_text(f"{p_emj('search', '🔍')} <b>ENTER THE NUMBER TO SEARCH OTP:</b>", parse_mode="HTML")
        return

    if context.user_data.get("mode") == "search_otp":
        context.user_data["mode"] = None
        await request_queue.put({'type': 'search_otp', 'update': update, 'context': context, 'target_num': normalize_number(text)})
        return

    # GET 2FA
    if "GET 2FA" in text.upper():
        await get_2fa_code(update, context)
        return

    # GET NUMBER
    if "GET NUMBER" in text.upper():
        await show_app_selection(update, context)
        return

    if context.user_data.get("mode") == "get_2fa":
        await process_2fa_key(update, context)
        return

    # LEADERBOARD
    if "LEADERBOARD" in text.upper():
        await leaderboard_command(update, context)
        return

    # SUPPORT BUTTON HANDLER
    if "SUPPORT" in text.upper() and "WORLD" not in text.upper():
        support_text = f"{p_emj('support', '💬')} <b>SUPPORT</b> 🎧\n\nCLICK THE BUTTON BELOW TO CONTACT SUPPORT {p_emj('mail', '📩')}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="SUPPORT", url=SUPPORT_LINK, api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("support")})],
            [InlineKeyboardButton(text="DEVELOPER BY", url=DEVELOPER_LINK, api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("config")})]
        ])
        await update.message.reply_text(support_text, reply_markup=keyboard, parse_mode="HTML")
        return

    # Admin panel
    if "ADMIN PANEL" in text.upper() and is_admin(uid):
        context.user_data["admin_mode"] = "main"
        await update.message.reply_text(
            f"⌬━━━━━━━━━━━━━━━━━━━━⌬\n   {p_emj('config', '⚙️')} <b>WELCOME ADMIN PANEL</b> {p_emj('config', '⚙️')}\n⌬━━━━━━━━━━━━━━━━━━━━⌬",
            parse_mode="HTML",
            reply_markup=admin_main_keyboard(uid)
        )
        return

    if "BACK TO MAIN" in text.upper() and context.user_data.get("admin_mode"):
        context.user_data["admin_mode"] = None
        await update.message.reply_text(f"{p_emj('back', '🔙')} Back to main menu.", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    if "BACK TO ADMIN" in text.upper():
        context.user_data["user_management_mode"] = None
        context.user_data["system_config_mode"] = None
        context.user_data["admin_mode"] = "main"
        await update.message.reply_text(f"{p_emj('back', '🔙')} Back to admin panel.", parse_mode="HTML", reply_markup=admin_main_keyboard(uid))
        return

    if "USER MANAGEMENT" in text.upper() and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["user_management_mode"] = "main"
        await update.message.reply_text(f"{p_emj('users', '👥')} User Management:", parse_mode="HTML", reply_markup=user_management_keyboard())
        return
    if "ADMIN MANAGE" in text.upper() and is_full_admin(uid):
        context.user_data["admin_state"] = None
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Add Full Admin", callback_data="set_full_admin", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("add_new")}),
             InlineKeyboardButton("Add Sub Admin", callback_data="set_sub_admin", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("add_new")})],
            [InlineKeyboardButton("View Admin List", callback_data="view_admin_list", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("users")})],
            [InlineKeyboardButton("Remove Admin", callback_data="rem_admin_start", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("rem_new")})],
            [InlineKeyboardButton("Cancel", callback_data="admin_manage_close", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("rem_new")})]
        ])
        await update.message.reply_text("👥 <b>ADMIN MANAGEMENT</b>\n\n<i>Select an option below:</i>", parse_mode="HTML", reply_markup=kb)
        return
        
    if "SYSTEM CONFIGURATION" in text.upper() and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["system_config_mode"] = "main"
        await update.message.reply_text(f"{p_emj('config', '⚙️')} System Configuration:", parse_mode="HTML", reply_markup=system_config_keyboard())
        return

    if "TODAY ALL STATUS" in text.upper() and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        t_n, t_o, s_n, s_o, tot_n, tot_o = get_global_system_stats()
        msg = (
            f"{p_emj('chart', '📊')} <b>SYSTEM STATUS</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{p_emj('sparkle', '✨')} <b>TODAY</b>\n{p_emj('phone', '📱')} NUMBERS: {t_n}\n{p_emj('key', '🔑')} OTPS: {t_o}\n\n"
            f"{p_emj('fire', '🔥')} <b>LAST 7 DAYS</b>\n{p_emj('phone', '📱')} NUMBERS: {s_n}\n{p_emj('key', '🔑')} OTPS: {s_o}\n\n"
            f"{p_emj('globe', '🌐')} <b>ALL TIME</b>\n{p_emj('phone', '📱')} NUMBERS: {tot_n}\n{p_emj('key', '🔑')} OTPS: {tot_o}"
        )
        await update.message.reply_text(msg, parse_mode="HTML")
        return

    if "USER STATUS CHECK" in text.upper() and is_admin(uid):
        context.user_data["mode"] = "input_user_id"
        await update.message.reply_text(f"{p_emj('search', '🔍')} ENTER TELEGRAM ID:", parse_mode="HTML", reply_markup=cancel_keyboard())
        return

    if context.user_data.get("mode") == "input_user_id" and is_admin(uid):
        target_uid = text.strip()
        if not target_uid.isdigit():
            await update.message.reply_text(f"{p_emj('cancel', '❌')} INVALID ID!", parse_mode="HTML")
            return
        context.user_data["mode"] = None
        stats = get_user_stats(target_uid)
        msg = (
            f"{p_emj('profile', '👤')} <b>USER STATUS</b> — <code>{target_uid}</code>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{p_emj('sparkle', '✨')} TODAY: {p_emj('phone', '📱')} {stats['today_numbers']} | {p_emj('key', '🔑')} {stats['today_otps']}\n"
            f"{p_emj('fire', '🔥')} 7 DAYS: {p_emj('phone', '📱')} {stats['last7d_numbers']} | {p_emj('key', '🔑')} {stats['last7d_otps']}\n"
            f"{p_emj('globe', '🌐')} ALL TIME: {p_emj('phone', '📱')} {stats['total_numbers']} | {p_emj('key', '🔑')} {stats['total_otps']}"
        )
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="CHECK ALL DATA", callback_data=f"full_logs_{target_uid}", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("chart")})
        ]])
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=keyboard)
        return

    if "ALL USER ID" in text.upper() and context.user_data.get("user_management_mode") == "main" and is_admin(uid):
        users = get_all_users()
        if users:
            content = "\n".join(f"{i}. {u}" for i, u in enumerate(users, 1))
            f = io.BytesIO(content.encode()); f.name = f"ALL_USERS_{len(users)}.txt"
            await update.message.reply_document(document=f, caption=f"{p_emj('users', '👥')} <b>Total Users: {len(users)}</b>", parse_mode="HTML", reply_markup=user_management_keyboard())
        else:
            await update.message.reply_text("No users found.", reply_markup=user_management_keyboard())
        return

    if "ALL USER BALANCE" in text.upper() and context.user_data.get("user_management_mode") == "main" and is_admin(uid):
        user_db = load_data(USER_DATA_FILE)
        if user_db:
            total_bal = sum(v.get("balance", 0) for v in user_db.values())
            lines = [f"{i}. {uid_}: {v.get('balance', 0):.2f} BDT" for i, (uid_, v) in enumerate(user_db.items(), 1)]
            content = f"💰 TOTAL BALANCE: {total_bal:.2f} BDT\n\n" + "\n".join(lines)
            f = io.BytesIO(content.encode()); f.name = f"BALANCES_{total_bal:.0f}.txt"
            await update.message.reply_document(document=f, caption=f"{p_emj('cash', '💵')} <b>Total Balance: {total_bal:.2f} BDT</b>", parse_mode="HTML", reply_markup=user_management_keyboard())
        else:
            await update.message.reply_text("No data.", reply_markup=user_management_keyboard())
        return

    if "BAN USER LIST" in text.upper() and is_admin(uid):
        await show_banned_users_list(update, context)
        return

    if "BAN USER" in text.upper() and "LIST" not in text.upper() and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_ban_user_start(update, context)
        return

    if "UNBAN USER" in text.upper() and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_unban_user_start(update, context)
        return

    if "ADD BALANCE" in text.upper() and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_add_balance_start(update, context)
        return

    if "REMOVE BALANCE" in text.upper() and context.user_data.get("system_config_mode") == "main" and is_admin(uid):
        await admin_remove_balance_start(update, context)
        return

    # ==================== FIXED BROADCAST (TEXT, PHOTO, VIDEO, FILE, ETC.) ====================
    if "SEND MESSAGE TO ALL USERS" in text.upper() and is_admin(uid):
        context.user_data["broadcast_mode"] = True
        await update.message.reply_text(
            f"{p_emj('broadcast', '📢')} <b>ADMIN BROADCAST SYSTEM (PRO)</b>\n\n"
            f"{p_emj('support', '💬')} আপনি এখন যা পাঠাবেন (Text, Photo, Video, Document, Voice, Audio, Animation, Sticker) – সকল ইউজারের কাছে প্রফেশনাল হেডারসহ চলে যাবে।\n\n"
            f"{p_emj('sparkle', '✨')} রেঞ্জ (যেমন: 237XXX) থাকলে তা অটোমেটিক ক্লিক-টু-কপি হয়ে যাবে।", 
            parse_mode="HTML", 
            reply_markup=cancel_keyboard()
        )
        return

    if context.user_data.get("broadcast_mode") and is_admin(uid):
        context.user_data["broadcast_mode"] = False
        
        user_db = load_data(USER_DATA_FILE)
        all_uids = list(user_db.keys())
        
        if not all_uids:
            await update.message.reply_text(f"{p_emj('cancel', '❌')} পাঠানোর জন্য কোনো ইউজার পাওয়া যায়নি!", parse_mode="HTML")
            return

        success_ids, fail_ids = [], []
        status_msg = await update.message.reply_text(f"{p_emj('rocket', '🚀')} <b>ব্রডকাস্ট শুরু হয়েছে...</b>\n{p_emj('sparkle', '🎯')} টার্গেট: {len(all_uids)} জন ইউজার।", parse_mode="HTML")

        def format_broadcast_caption(caption_text):
            if not caption_text:
                return f"<blockquote>{p_emj('broadcast', '📢')} <b>ADMIN NOTICE :</b></blockquote>"
            formatted = re.sub(r'(\d{3,}[xX]{3,})', r'<code>\1</code>', str(caption_text))
            return f"<blockquote>{p_emj('broadcast', '📢')} <b>ADMIN NOTICE :</b></blockquote>\n\n{formatted}"

        for user_id_str in all_uids:
            try:
                target_id = int(user_id_str)
                
                if update.message.text:
                    html_text = update.message.text_html
                    await context.bot.send_message(chat_id=target_id, text=format_broadcast_caption(html_text), parse_mode="HTML")
                elif update.message.photo:
                    html_caption = update.message.caption_html if update.message.caption else None
                    caption = format_broadcast_caption(html_caption) if html_caption else None
                    await context.bot.send_photo(chat_id=target_id, photo=update.message.photo[-1].file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.video:
                    html_caption = update.message.caption_html if update.message.caption else None
                    caption = format_broadcast_caption(html_caption) if html_caption else None
                    await context.bot.send_video(chat_id=target_id, video=update.message.video.file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.document:
                    html_caption = update.message.caption_html if update.message.caption else None
                    caption = format_broadcast_caption(html_caption) if html_caption else None
                    await context.bot.send_document(chat_id=target_id, document=update.message.document.file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.audio:
                    html_caption = update.message.caption_html if update.message.caption else None
                    caption = format_broadcast_caption(html_caption) if html_caption else None
                    await context.bot.send_audio(chat_id=target_id, audio=update.message.audio.file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.voice:
                    html_caption = update.message.caption_html if update.message.caption else None
                    caption = format_broadcast_caption(html_caption) if html_caption else None
                    await context.bot.send_voice(chat_id=target_id, voice=update.message.voice.file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.animation:
                    html_caption = update.message.caption_html if update.message.caption else None
                    caption = format_broadcast_caption(html_caption) if html_caption else None
                    await context.bot.send_animation(chat_id=target_id, animation=update.message.animation.file_id, caption=caption, parse_mode="HTML" if caption else None)
                elif update.message.sticker:
                    await context.bot.send_sticker(chat_id=target_id, sticker=update.message.sticker.file_id)
                else:
                    try:
                        await context.bot.copy_message(chat_id=target_id, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
                    except:
                        await context.bot.send_message(chat_id=target_id, text=f"{p_emj('broadcast', '📢')} <b>ADMIN NOTICE :</b>\n\nআপনার জন্য একটি নতুন বার্তা আছে, কিন্তু এটি প্রদর্শন করা সম্ভব হয়নি।", parse_mode="HTML")
                success_ids.append(user_id_str)
            except Exception as e:
                print(f"Broadcast fail to {user_id_str}: {e}")
                fail_ids.append(user_id_str)
            
            await asyncio.sleep(0.05)

        report_text = (
            f"{p_emj('success', '✅')} <b>ADMIN NOTICE COMPLETE !</b>\n\n"
            f"{p_emj('chart', '📊')} <b>BROADCAST REPORT:</b>\n\n"
            f"<blockquote>{p_emj('success', '✅')} SUCCESSFULLY SENT: {len(success_ids)} USERS !</blockquote>\n"
            f"<blockquote>{p_emj('cancel', '❌')} FAILED TO SEND: {len(fail_ids)} USERS !</blockquote>"
        )
        
        await status_msg.delete()
        await context.bot.send_message(chat_id=uid, text=report_text, parse_mode="HTML", reply_markup=main_keyboard(uid))

        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if success_ids:
            s_file = io.BytesIO(("\n".join(success_ids)).encode()); s_file.name = f"SUCCESS_{random_suffix}.txt"
            await context.bot.send_document(chat_id=uid, document=s_file, caption=f"{p_emj('success', '✅')} Success User List", parse_mode="HTML")
        if fail_ids:
            f_file = io.BytesIO(("\n".join(fail_ids)).encode()); f_file.name = f"FAILED_{random_suffix}.txt"
            await context.bot.send_document(chat_id=uid, document=f_file, caption=f"{p_emj('cancel', '❌')} Failed User List", parse_mode="HTML")
        
        return

    await update.message.reply_text(f"{p_emj('sparkle', '🔹')} PLEASE USE THE BUTTONS BELOW:", parse_mode="HTML", reply_markup=main_keyboard(uid))

# ==================== COMMAND HANDLERS SECTION ====================

async def get1number_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return
    await show_app_selection(update, context)

async def searchotp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return
    context.user_data["mode"] = "search_otp"
    await update.message.reply_text(f"{p_emj('search', '🔍')} <b>ENTER THE NUMBER TO SEARCH OTP:</b>", parse_mode="HTML")

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return
    balance = get_user(uid)['balance']
    await update.message.reply_text(f"{p_emj('money', '💰')} BALANCE: <code>{format_balance(balance)} BDT</code>", parse_mode="HTML", reply_markup=main_keyboard(uid))

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return
    user_data = get_user(uid)
    stats = get_user_stats(uid)
    user = update.effective_user
    profile_text = (
        f"{p_emj('profile', '👤')} <b>YOUR PROFILE</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{p_emj('sparkle', '🏷️')} NAME: <code>{html.escape(user.full_name)}</code>\n"
        f"{p_emj('id', '🆔')} USERNAME: @{html.escape(user.username or 'No username')}\n"
        f"{p_emj('key', '🗝️')} ID: <code>{uid}</code>\n\n"
        f"{p_emj('cash', '💵')} BALANCE: {format_balance(user_data.get('balance', 0))} BDT\n\n"
        f"{p_emj('sparkle', '✨')} TODAY: {p_emj('phone', '📱')} {stats['today_numbers']} | {p_emj('key', '🔑')} {stats['today_otps']}\n"
        f"{p_emj('fire', '🔥')} 7 DAYS: {p_emj('phone', '📱')} {stats['last7d_numbers']} | {p_emj('key', '🔑')} {stats['last7d_otps']}\n"
        f"{p_emj('globe', '🌐')} ALL TIME: {p_emj('phone', '📱')} {stats['total_numbers']} | {p_emj('key', '🔑')} {stats['total_otps']}"
    )
    await update.message.reply_text(profile_text, parse_mode="HTML")

async def refer_command_slash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return
    await refer_command(update, context)

async def leaderboard_command_slash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML", reply_markup=main_keyboard(uid))
        return
    await leaderboard_command(update, context)
async def clearkb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # এই কমান্ডটা কীবোর্ড ডিলিট করে দেবে
    await update.message.reply_text("✅ গ্রুপ থেকে বটের কীবোর্ড রিমুভ করা হয়েছে!", reply_markup=ReplyKeyboardRemove())
# ==================== START & CALLBACK SECTION ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uid_str = str(uid)

    existing_data = load_data(USER_DATA_FILE)
    is_new_user = uid_str not in existing_data
    if is_new_user:
        get_user(uid)

    # ==================== Dynamic Force Join Check ====================
    unjoined_channels = await get_unjoined_channels(uid, context.bot)
    
    if unjoined_channels:
        keyboard = []
        for ch in unjoined_channels:
            try:
                chat_info = await context.bot.get_chat(ch)
                ch_title = chat_info.title
            except:
                ch_title = ch
                
            ch_url = f"https://t.me/{ch.replace('@', '')}"
            keyboard.append([InlineKeyboardButton(
                text=ch_title, 
                url=ch_url,
                api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("broadcast")}
            )])
        
        keyboard.append([InlineKeyboardButton(
            text="Verify", 
            callback_data="verify_join",
            api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("success")}
        )])
        
        msg = (
            f"<b>《 {p_emj('success', '🛡️')} ACCESS REQUIRED 》</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"You must join all channels below to use this bot:\n"
            f"<i>Click the buttons to join, then click Verify.</i>"
        )
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # ==================== Referral Check (এর পরের কোড আগের মতই থাকবে) ====================

    args = context.args
    if args:
        param = args[0]
        if is_range_request(param):
            await request_queue.put({'type': 'auto_number', 'update': update, 'context': context, 'range_text': param})
            return
        elif is_referral_request(param) and is_new_user:
            try:
                referrer_id = int(param)
                if referrer_id != uid and str(referrer_id) in existing_data:
                    current_count = get_referral_count(referrer_id)
                    new_count = current_count + 1
                    update_referral_count(referrer_id, new_count)
                    await update_db_balance(referrer_id, REFERRAL_PRICE)
                    log_global_activity(referrer_id, "REFERRAL_JOINED", {"referred_user": uid})
                    try:
                        await context.bot.send_message(
                            referrer_id,
                            f"{p_emj('gift', '🎉')} <b>NEW REFERRAL!</b>\n\n<blockquote>{p_emj('key', '🗝️')} ID: <code>{uid}</code>\n{p_emj('money', '💰')} REWARD: {format_balance(REFERRAL_PRICE)} BDT\n{p_emj('users', '👥')} TOTAL REFERS: {new_count}</blockquote>",
                            parse_mode="HTML"
                        )
                    except:
                        pass
            except Exception as e:
                print(f"Referral error: {e}")

    context.user_data.clear()
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="HTML")
    await update.message.reply_text(f"{p_emj('sparkle', '🔹')} PLEASE USE THE BUTTONS BELOW:", parse_mode="HTML", reply_markup=main_keyboard(uid))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # ইনবক্স ছাড়া অন্য কোথাও বাটন চাপলে সোজা রিজেক্ট করে দেবে
    if query.message.chat.type != "private":
        await query.answer("❌ This bot only works in private chat (Inbox)!", show_alert=True)
        return

    uid = query.from_user.id
    data = query.data
    await query.answer()

    if not is_admin(uid) and is_user_banned(uid):
        await query.edit_message_text(f"{p_emj('ban', '🚫')} YOU ARE BANNED {p_emj('ban', '🚫')}", parse_mode="HTML")
        return

    if data == "set_full_admin" and is_full_admin(uid):
        context.user_data["admin_state"] = "wait_for_admin_id"
        context.user_data["new_admin_type"] = "full"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_cancel_state", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("cancel")})]])
        await query.message.edit_text("Send the Telegram User ID for FULL ADMIN:", reply_markup=kb)
        return

    if data == "set_sub_admin" and is_full_admin(uid):
        context.user_data["admin_state"] = "wait_for_admin_id"
        context.user_data["new_admin_type"] = "sub"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_cancel_state", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("cancel")})]])
        await query.message.edit_text("Send the Telegram User ID for SUB-ADMIN:", reply_markup=kb)
        return
    # LIVEACCESS — SERVICE SELECTION
    if data.startswith("svc_"):
        try:
            idx = int(data.replace("svc_", ""))
            services = context.user_data.get("la_services", [])
            if not services:
                services = get_cached_services()
                context.user_data["la_services"] = services
            if idx >= len(services):
                await query.answer("Service not found.", show_alert=True)
                return

            svc = services[idx]
            sid = svc.get("sid", "Service")
            ranges = svc.get("ranges", [])

            context.user_data["la_svc_idx"] = idx
            context.user_data["la_sid"] = sid
            context.user_data["la_ranges"] = ranges
            
            svc_emoji_id = get_service_emoji_id(sid)
            keyboard = _build_countries_keyboard(ranges, idx)
            await query.message.edit_text(
                f"<blockquote><tg-emoji emoji-id=\"{svc_emoji_id}\">📱</tg-emoji> <b>Service : {html.escape(sid)}</b></blockquote>\n\n"
                f"Select country below:",
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"SVC Error: {e}")
        return

    # LIVEACCESS — COUNTRY SELECTION (NEW)
    if data.startswith("cty_"):
        try:
            parts = data.split("_", 2)
            idx = int(parts[1])
            cname = parts[2]
            
            sid = context.user_data.get("la_sid", "Service")
            ranges = context.user_data.get("la_ranges", [])
            
            svc_emoji_id = get_service_emoji_id(sid)
            keyboard = _build_ranges_keyboard(ranges, idx, cname)
            
            await query.message.edit_text(
                f"<blockquote><tg-emoji emoji-id=\"{svc_emoji_id}\">📱</tg-emoji> <b>Service : {html.escape(sid)}</b></blockquote>\n"
                f"<blockquote><tg-emoji emoji-id=\"{e_id('globe')}\">🌍</tg-emoji> <b>Country : {cname}</b></blockquote>\n\n"
                f"Select Range below:",
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"CTY Error: {e}")
        return

    # LIVEACCESS — RANGE SELECTION
    if data.startswith("rng_"):
        try:
            parts = data.split("_")
            range_idx = int(parts[2])
            ranges = context.user_data.get("la_ranges", [])
            range_text = ranges[range_idx]
            
            # query পাস করছি যাতে মেসেজটা এডিট হয়
            asyncio.create_task(fast_allocate_number(query, context, range_text, sid=""))
        except Exception as e:
            print(f"RNG Error: {e}")
        return

    # CUSTOM RANGE
    if data == "custom_range":
        context.user_data["mode"] = "custom_range"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="BACK", callback_data="back_services", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("back")})
        ]])
        await query.message.edit_text(
            f"{p_emj('config', '⚙️')} <b>CUSTOM RANGE</b>\n\n"
            f"<blockquote>{p_emj('signal', '📶')} আপনার কাস্টম range টাইপ করুন।</blockquote>\n"
            f"<blockquote>{p_emj('config', '⌨️')} নিচে range লিখে Send করুন:</blockquote>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    # BACK TO SERVICES
    if data == "back_services":
        services = get_cached_services() or context.user_data.get("la_services", [])
        context.user_data["la_services"] = services
        keyboard = _build_services_keyboard(services)
        await query.message.edit_text(
            f"<blockquote>{p_emj('success', '☑️')} <b>FAST X OTP PANEL</b></blockquote>\n\nSelect a service below:",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return

    # SAME RANGE (CHANGE NUMBER)
    if data == "same_range":
        r_text = last_range.get(uid)
        if r_text:
            # query পাস করছি যাতে নতুন মেসেজ না আসে, এটাই এডিট হয়
            await process_numbers(query, context, r_text, 3)
        return

    # WITHDRAW
    if data == "withdraw_start":
        balance = get_user(uid)['balance']
        if balance < MIN_WITHDRAW:
            await query.message.reply_text(
                f"<blockquote>{p_emj('cash', '💵')} BALANCE: {format_balance(balance)} BDT\n{p_emj('chart', '📉')} MIN WITHDRAW: {MIN_WITHDRAW} BDT</blockquote>",
                parse_mode="HTML"
            )
            return
        context.user_data["withdraw_mode"] = "select_method"
        await query.message.reply_text(f"{p_emj('money', '💳')} SELECT YOUR PAYMENT METHOD!", parse_mode="HTML", reply_markup=withdraw_method_keyboard())
        return

    if data == "withdraw_confirm":
        await process_withdraw_confirm(update, context)
        return

    if data == "withdraw_cancel":
        await process_withdraw_cancel(update, context)
        return

    if data.startswith("admin_approve_"):
        await admin_approve_withdraw(update, context, data.replace("admin_approve_", ""))
        return

    if data.startswith("admin_reject_"):
        await admin_reject_withdraw(update, context, data.replace("admin_reject_", ""))
        return

    # COPY / MISC CALLBACKS
    if data.startswith("copy_id_"):
        await query.answer(f"✅ Copied ID: {data.replace('copy_id_', '')}", show_alert=True)
        return

    if data.startswith("copy_text_"):
        await query.answer(f"✅ Copied: {data.replace('copy_text_', '')}", show_alert=True)
        return

    if data.startswith("my_ref_"):
        target_uid = data.replace("my_ref_", "")
        all_logs = load_data(ACTIVITY_LOGS_FILE)
        my_referrals = [log for log in all_logs if str(log.get('uid')) == str(target_uid) and log.get('action') == "REFERRAL_JOINED"]
        content = f"👥 REFERRAL REPORT — {target_uid}\n━━━━━━━━━━━━\nTOTAL: {len(my_referrals)}\n\n"
        for i, log in enumerate(my_referrals, 1):
            try:
                dt_obj = datetime.fromisoformat(log['timestamp'])
                ref_id = log.get('details', {}).get('referred_user', 'N/A')
                content += f"{i}. ID: {ref_id} | {dt_obj.strftime('%d/%m/%Y %I:%M %p')}\n"
            except:
                continue
        f = io.BytesIO(content.encode())
        f.name = f"REF_{target_uid}.txt"
        await context.bot.send_document(chat_id=uid, document=f, caption=f"{p_emj('success', '✅')} **REFERRAL DATA**", parse_mode="Markdown")
        return

    if data.startswith("full_logs_"):
        target_uid = data.replace("full_logs_", "")
        stats = get_user_stats(target_uid)
        all_logs = load_data(ACTIVITY_LOGS_FILE)
        user_db = load_data(USER_DATA_FILE)
        user_info = user_db.get(str(target_uid), {})
        user_otps = [log for log in all_logs if str(log.get('uid')) == str(target_uid) and log.get('action') == "OTP_RECEIVED"]
        content = (
            f"📊 USER DATA REPORT — {target_uid}\n"
            f"💰 BALANCE: {user_info.get('balance', 0):.2f} BDT\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"TODAY NUMBERS: {stats['today_numbers']}\n"
            f"TODAY OTPS: {stats['today_otps']}\n"
            f"7D NUMBERS: {stats['last7d_numbers']}\n"
            f"7D OTPS: {stats['last7d_otps']}\n"
            f"TOTAL NUMBERS: {stats['total_numbers']}\n"
            f"TOTAL OTPS: {stats['total_otps']}\n"
            f"━━━━━━━━━━━━━━━━━━\n\nOTP LOGS:\n"
        )
        for i, log in enumerate(user_otps, 1):
            try:
                dt_obj = datetime.fromisoformat(log['timestamp'])
                d = log.get('details', {})
                content += f"{i}. {dt_obj.strftime('%d/%m/%Y %I:%M %p')}\n   📞 {d.get('number', 'N/A')}\n   🔑 {d.get('otp', 'N/A')}\n\n"
            except:
                continue
        f = io.BytesIO(content.encode())
        f.name = f"USER_{target_uid}.txt"
        
        await context.bot.send_document(
            chat_id=uid, document=f,
            caption=f"{p_emj('success', '✅')} <b>DATA FOR USER: <code>{target_uid}</code></b>",
            parse_mode="HTML"
        )
        return
    # === VERIFY JOIN BUTTON ===
    if data == "verify_join":
        unjoined_channels = await get_unjoined_channels(uid, context.bot)
        
        if not unjoined_channels:
            await query.message.delete()
            await context.bot.send_message(chat_id=uid, text=WELCOME_MESSAGE, parse_mode="HTML")
            await context.bot.send_message(chat_id=uid, text=f"{p_emj('sparkle', '🔹')} PLEASE USE THE BUTTONS BELOW:", parse_mode="HTML", reply_markup=main_keyboard(uid))
        else:
            # যেগুলোতে জয়েন করেনি, শুধু সেগুলো দিয়ে বাটন আপডেট করবে
            keyboard = []
            for ch in unjoined_channels:
                try:
                    chat_info = await context.bot.get_chat(ch)
                    ch_title = chat_info.title
                except:
                    ch_title = ch
                    
                ch_url = f"https://t.me/{ch.replace('@', '')}"
                keyboard.append([InlineKeyboardButton(
                    text=ch_title, 
                    url=ch_url,
                    api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("broadcast")}
                )])
            
            keyboard.append([InlineKeyboardButton(
                text="Verify", 
                callback_data="verify_join",
                api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("success")}
            )])
            
            try:
                await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass # মেসেজ যদি আগে থেকেই সেম থাকে
                
            await query.answer("❌ You haven't joined all channels yet!", show_alert=True)
        return

    # === ADMIN CHANNEL CONTROL CALLBACKS ===
    if data == "admin_panel_back":
        await query.message.delete()
        return

    if data == "admin_add_fc":
        context.user_data["admin_state"] = "add_fc"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_cancel_state")]])
        await query.message.edit_text("📢 <i>Send channel username (starting with @):</i>", parse_mode="HTML", reply_markup=kb)
        return
        
    if data == "admin_rem_fc_list":
        settings = load_settings()
        channels = settings.get("force_channels", [])
        if not channels:
            await query.answer("No Force Join channels set!", show_alert=True)
            return
        kb = []
        for ch in channels:
            kb.append([InlineKeyboardButton(f"🗑️ {ch}", callback_data=f"remfc_{ch}")])
        kb.append([InlineKeyboardButton("◀️ Back", callback_data="admin_cc_refresh")])
        await query.message.edit_text("<i>Select channel to remove:</i>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data.startswith("remfc_"):
        ch_to_rem = data.replace("remfc_", "")
        settings = load_settings()
        if ch_to_rem in settings["force_channels"]:
            settings["force_channels"].remove(ch_to_rem)
            save_settings(settings)
        text, kb = get_channel_control_panel()
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        return

    if data == "admin_cc_refresh":
        text, kb = get_channel_control_panel()
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        return

    if data == "admin_set_otp":
        from telegram import KeyboardButtonRequestChat
        context.user_data["admin_state"] = "wait_for_otp_group"
        
        # নিচে রিপ্লাই কীবোর্ড তৈরি করা হচ্ছে যাতে গ্রুপ পিকার ওপেন হয়
        btn_req = KeyboardButton(
            text="✅ SELECT GROUP",
            request_chat=KeyboardButtonRequestChat(request_id=1, chat_is_channel=False)
        )
        cancel_btn = KeyboardButton(text="❌ CANCEL")
        
        kb = ReplyKeyboardMarkup([[btn_req], [cancel_btn]], resize_keyboard=True, one_time_keyboard=True)
        
        await query.message.delete()
        await context.bot.send_message(
            chat_id=uid,
            text="👇 <b>Please click the button below to choose the OTP Group from your chats:</b>",
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    if data == "admin_rem_otp":
        settings = load_settings()
        settings["otp_group"] = "Not Set"
        save_settings(settings)
        text, kb = get_channel_control_panel()
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        return

    if data == "admin_set_main":
        context.user_data["admin_state"] = "set_main"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_cancel_state")]])
        await query.message.edit_text("🎓 <i>Send Main Channel username/link:</i>", parse_mode="HTML", reply_markup=kb)
        return

    if data == "admin_toggle_log":
        settings = load_settings()
        settings["log_forward"] = not settings.get("log_forward", True)
        save_settings(settings)
        text, kb = get_channel_control_panel()
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        return

    if data == "admin_cancel_state":
        context.user_data.pop("admin_state", None)
        text, kb = get_channel_control_panel()
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        return
           # === ADMIN SERVICE CONTROL CALLBACKS ===
    if data.startswith("togglesvc_"):
        parts = data.split("_", 2)
        page = int(parts[1])
        sid = parts[2]
        
        settings = load_settings()
        hidden = settings.get("hidden_services", [])
        
        if sid in hidden:
            hidden.remove(sid)
        else:
            hidden.append(sid)
            
        settings["hidden_services"] = hidden
        save_settings(settings)
        
        text_msg, kb = get_service_control_panel(page)
        await query.message.edit_text(text_msg, parse_mode="HTML", reply_markup=kb)
        return

    if data.startswith("svcpage_"):
        page = int(data.split("_")[1])
        text_msg, kb = get_service_control_panel(page)
        await query.message.edit_text(text_msg, parse_mode="HTML", reply_markup=kb)
        return 
    if data == "admin_toggle_sms":
        settings = load_settings()
        settings["show_full_sms"] = not settings.get("show_full_sms", False)
        save_settings(settings)
        text, kb = get_channel_control_panel()
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        return

    if data == "admin_set_ch_url":
        context.user_data["admin_state"] = "set_ch_url"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_cancel_state")]])
        await query.message.edit_text("🔗 <i>Send new Channel URL:</i>", parse_mode="HTML", reply_markup=kb)
        return
        
    if data == "admin_set_bot_url":
        context.user_data["admin_state"] = "set_bot_url"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_cancel_state")]])
        await query.message.edit_text("🔗 <i>Send new Get Number Bot URL:</i>", parse_mode="HTML", reply_markup=kb)
        return

    if data == "admin_set_mask":
        context.user_data["admin_state"] = "set_mask"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_cancel_state", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("cancel")})]])
        await query.message.edit_text("🎭 <i>Send new Custom Mask (e.g. TWS or ••):</i>", parse_mode="HTML", reply_markup=kb)
        return
    if data == "admin_set_fetch_count":
        context.user_data["admin_state"] = "set_fetch_count"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_cancel_state", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("cancel")})]])
        await query.message.edit_text("📱 <i>Send how many numbers to fetch at once (e.g. 1, 2, or 3):</i>", parse_mode="HTML", reply_markup=kb)
        return                

    if data == "view_admin_list" and is_full_admin(uid):
        settings = load_settings()
        f_admins = settings.get("full_admins", [])
        s_admins = settings.get("sub_admins", [])
        
        msg = f"👥 <b>ADMIN LIST</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"<b>👑 Full Admins ({len(f_admins)}):</b>\n"
        for a in f_admins:
            msg += f"  ├ <code>{a}</code>\n"
        if not f_admins: msg += "  ├ None\n"
        
        msg += f"\n<b>🛡️ Sub Admins ({len(s_admins)}):</b>\n"
        for a in s_admins:
            msg += f"  ├ <code>{a}</code>\n"
        if not s_admins: msg += "  ├ None\n"
        
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="admin_manage_back", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("back")})]])
        await query.message.edit_text(msg, parse_mode="HTML", reply_markup=kb)
        return

    if data == "rem_admin_start" and is_full_admin(uid):
        context.user_data["admin_state"] = "remove_admin"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_manage_back", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("cancel")})]])
        await query.message.edit_text("🗑️ <i>Send the Telegram User ID to REMOVE from admin:</i>", parse_mode="HTML", reply_markup=kb)
        return
        
    if data == "admin_manage_back" and is_full_admin(uid):
        context.user_data["admin_state"] = None
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Add Full Admin", callback_data="set_full_admin", api_kwargs={'style': 'success', 'icon_custom_emoji_id': e_id("add_new")}),
             InlineKeyboardButton("Add Sub Admin", callback_data="set_sub_admin", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("add_new")})],
            [InlineKeyboardButton("View Admin List", callback_data="view_admin_list", api_kwargs={'style': 'primary', 'icon_custom_emoji_id': e_id("users")})],
            [InlineKeyboardButton("Remove Admin", callback_data="rem_admin_start", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("rem_new")})],
            [InlineKeyboardButton("Cancel", callback_data="admin_manage_close", api_kwargs={'style': 'danger', 'icon_custom_emoji_id': e_id("rem_new")})]
        ])
        await query.message.edit_text("👥 <b>ADMIN MANAGEMENT</b>\n\n<i>Select an option below:</i>", parse_mode="HTML", reply_markup=kb)
        return

    if data == "admin_manage_close":
        context.user_data["admin_state"] = None
        await query.message.delete()
        return

# ==================== MAIN & POST INIT SECTION ====================

async def post_init(application):
    for _ in range(20):
        asyncio.create_task(worker())
    asyncio.create_task(monitor_loop(application))
    asyncio.create_task(liveaccess_refresh_loop())

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).post_init(post_init).build()

    # সব কমান্ড শুধুমাত্র ইনবক্সের (PRIVATE) জন্য লক করা হলো
    app.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("get1number", get1number_command, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("searchotp", searchotp_command, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("balance", balance_command, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("profile", profile_command, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("refer", refer_command_slash, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command_slash, filters=filters.ChatType.PRIVATE))
    
    # কীবোর্ড রিমুভ কমান্ড (PRIVATE ফিল্টার ছাড়া, যাতে গ্রুপে কাজ করে)
    app.add_handler(CommandHandler("clearkb", clearkb_command))

    # বাটন এবং মেসেজ হ্যান্ডলার (বাটন সব জায়গায় কাজ করবে, কিন্তু মেসেজ শুধু ইনবক্সে)
    app.add_handler(CallbackQueryHandler(button_callback))
    # টেক্সট এবং চ্যাট শেয়ার ইভেন্ট রিসিভ করার জন্য ফিল্টার আপডেট করা হলো
    app.add_handler(MessageHandler((filters.TEXT | filters.StatusUpdate.CHAT_SHARED) & (~filters.COMMAND) & filters.ChatType.PRIVATE, handle_message))

    print("🚀 BOT RUNNING...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()