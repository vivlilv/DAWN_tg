SETTINGS = {
    'DB_NAME': 'dawn_profiles',
    'COLLECTION_NAME': 'user_entries',
    'CHECK_INTERVAL': 600,  # 10 хвилин
    'BASE_URL': 'https://www.aeropres.in/chromeapi/dawn/v1',
    'VERSION': '1.0.7',
    'EXTENSION_ID': 'fpdkjdnhkakefebpekbdhillbhonfjjp',
    'GET_POINT_URL':'https://www.aeropres.in/api/atom/v1/userreferral/getpoint',
    
    'DEFAULT_HEADERS': {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Linux\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
    },
    
    'VERIFICATION_HEADERS': {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Linux\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    },
    
    'LOGIN_HEADERS': {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Linux\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
    },
    
    'MAX_LOGIN_RETRIES': 10,
    'MAX_KEEP_ALIVE_RETRIES': 5,
    'SLEEP_BETWEEN_RETRIES': 10,  # секунд
    'FARM_INTERVAL': 110,  # секунд
}