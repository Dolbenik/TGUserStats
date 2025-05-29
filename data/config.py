api_id = 2
api_hash = 'f'

proxy = None # proxy = ("socks5", '127.0.0.1', 4444)
             # proxy = {'proxy_type': 'socks5', 'addr': '1.1.1.1', 'port': 5555, 'username': 'foo', 'password': 'bar', 'rdns': True}

top_n = 30  # how many words should be in the top
SAVE_EVERY = 100  # after how many messages to save progress
session = 'data/anon'
folder_export = "data/exports"

#here are the words the script should skip during sorting the statistics
# 'and', 'in', 'on', 'but', 'i', 'this', 'how', 'what', 'not', 'that', 'with',
# 'by', 'for', 'from', 'at', 'of', 'the', 'a', 'an', 'to', 'is', 'it', 'are',
# 'was', 'be', 'you', 'he', 'she', 'we', 'they'
stop_words = {'1111870','https', 'com', 'track', 'tiktok'}