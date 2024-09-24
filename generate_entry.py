import random
import json

# Sample emails, passwords, and proxies provided
emails = [
    ("stachowic_josephine.1967@outlook.com", "X3p2hdoZn6G"),
    ("kristinahalx5dc@outlook.com", "rbjhfd9bC"),
    ("kaleywooden048@outlook.com", "inFa6qbj"),
    ("tuccijohna@outlook.com", "239letSdiID"),
    ("beatrizleto9494@outlook.com", "23LETOleto"),
    ("refugiaafebr@outlook.com", "pu237voq5T"),
    ("tierrawhiir4i@outlook.com", "e3re2SCe4"),
    ("lynseymoates91716@outlook.com", "624Moates624"),
    ("necolet5b@outlook.com", "C8FzPiI7Tv"),
    ("deeannzu0ofe@outlook.com", "iw6cK2u70p"),
    ("joya2qevlucas@outlook.com", "eunxY7hs0"),
    ("sunnij6cmoten@outlook.com", "yvrzQc1i"),
    ("arajbrower@outlook.com", "eF2tw9tif"),
    ("gefrancen8@outlook.com", "hf7Rcdh2"),
]

proxies = [
    "38.154.204.150:8191:tbtvmzii:2qcqv4hp8yqm",
    "198.154.89.220:6311:tbtvmzii:2qcqv4hp8yqm",
    "102.212.90.128:5822:tbtvmzii:2qcqv4hp8yqm",
    "104.239.76.100:6759:tbtvmzii:2qcqv4hp8yqm",
    "45.43.178.49:5756:tbtvmzii:2qcqv4hp8yqm",
    "64.137.37.172:6762:tbtvmzii:2qcqv4hp8yqm",
    "104.239.22.79:6457:tbtvmzii:2qcqv4hp8yqm",
    "172.84.183.100:5660:tbtvmzii:2qcqv4hp8yqm",
    "109.196.163.55:6153:tbtvmzii:2qcqv4hp8yqm",
    "154.73.249.211:6790:tbtvmzii:2qcqv4hp8yqm",
    "103.99.33.186:6181:tbtvmzii:2qcqv4hp8yqm",
    "38.154.204.112:8153:tbtvmzii:2qcqv4hp8yqm",
    "198.46.246.128:6752:tbtvmzii:2qcqv4hp8yqm",
    "104.238.50.116:6662:tbtvmzii:2qcqv4hp8yqm"
]


user_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.0.0 Safari/537.36"
]


# Function to create entries
def create_entries(emails, proxies, user_agents):
    entries = []
    
    for i, (email, password) in enumerate(emails):
        name = f"User_{random.randint(1000, 9999)}"
        proxy_parts = proxies[i].split(":")
        proxy = f"http://{proxy_parts[2]}:{proxy_parts[3]}@{proxy_parts[0]}:{proxy_parts[1]}"
        user_agent = random.choice(user_agents)
        
        entry = {
            "name": name,
            "mail": email,
            "mail_pass": password,
            "referralCode": "",
            "user_agent": user_agent,
            "proxy": proxy
        }
        
        entries.append(entry)
    
    return entries

# Generate the entries
entries = create_entries(emails, proxies, user_agents)

# Write to a JSON file
with open("user_entries.json", "w") as f:
    json.dump(entries, f, indent=4)

print("Entries have been written to 'user_entries.json'")
