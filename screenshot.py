import re
import os
import time
import asyncio

import dateparser
from feedgenerator import Rss201rev2Feed
from playwright.async_api import async_playwright, Playwright
from dotenv import load_dotenv
from datetime import datetime
import pytz

load_dotenv()

#WWW_ROOT = "/var/www/rss/"
WWW_ROOT = "./"
SCROLLS = 3
save_tweets = []

async def run(playwright: Playwright):

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()
    context = await browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0',
    )
    twitter_cookies = [{
        'name': 'auth_token',
        'value': os.getenv("TWITTER_COOKIE"),
        'domain': ".twitter.com",
        'path': "/",
    }]
    await context.add_cookies(twitter_cookies)
    page = await context.new_page()
    await page.goto("https://twitter.com/mattyglesias")
    await page.wait_for_selector('[data-testid="tweet"]')

    # Try to remove banner cruft
    await page.evaluate("""
() => {
    document.querySelector('[data-testid=\"BottomBar\"]').remove()
    try {
        document.querySelector('[aria-label=\"sheetDialog\"]').parentNode.remove()
    } catch(err) {
    }
}
""")
    # await page.screenshot(path="page.png")
    seen_tweets = set()
    for i in range(SCROLLS):
        tweets = page.locator('[data-testid="tweet"]')
        count = await tweets.count()

        for i in range(count):
            tweet = tweets.nth(i)
            tweet_html = await tweet.inner_html()
            url_regex_pattern = r'href=\"(/[a-zA-Z0-9_]+/status/\d+)\"'
            url_match = re.search(url_regex_pattern, tweet_html)
            if not url_match:
                continue
            url = "https://twitter.com" + url_match.group(1)
            
            tweet_id = url.split("/")[-1]

            if tweet_id in seen_tweets:
                continue
            else:
                seen_tweets.add(tweet_id)

                all_t = await tweet.all_inner_texts()
                contents = all_t[0].split("\n")

                # Skip pinned tweets
                if contents[0].startswith("Pinned"):
                    print("Skipped pinned tweet")
                    continue

                if not contents[0].endswith("reposted"):
                    user = contents[0]
                    handle = contents[1]
                    t_delta = contents[3]
                    contents = contents[4:]
                else:
                    user = contents[0]
                    handle = contents[2]
                    t_delta = contents[4]
                    contents = contents[5:]

                try:
                    quote = contents[:-4].index("Quote")
                    tweet_txt = "\n".join(contents[:4 + quote])
                except ValueError:
                    tweet_txt = "\n".join(contents[:-4])

                datetime_regex_pattern = r'<time datetime="([^"]+)"'
                datetime_match = re.search(datetime_regex_pattern, tweet_html)
                if not datetime_match:
                    print("Skipped ad")
                    continue
                datetime_part = datetime_match.group(1)
                parsed_datetime = dateparser.parse(datetime_part)

                img_path = f"img/{handle[1:]}-{tweet_id}.png"
                await tweet.screenshot(path=WWW_ROOT + img_path)
                
                save_tweets.append({
                    'user': user,
                    'handle': handle,
                    'datetime': parsed_datetime,
                    'tweet_txt': tweet_txt,
                    'img': "https://rpi4.duckbill-woodpecker.ts.net/rss/" + img_path,
                    'link': url,
                })
                contents = all_t[0].split("\n")

        await page.mouse.wheel(0, 600)
        time.sleep(1)

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

def parse_time_string(time_str):
    return parsed_date

def gen_feed(save_tweets):
    # Initialize RSS feed
    feed = Rss201rev2Feed(
        title="Web-to-RSS",
        description="Capture infinite feeds to RSS",
        link="https://rpi4.duckbill-woodpecker.ts.net/rss",
        language="en",
    )
    for t in save_tweets:
        desc = f"<img src=\"{t['img']}\", title=\"{t['tweet_txt']}\", alt=\"{t['tweet_txt']}\"/>"
        feed.add_item(
            title=f"Tweet from {t['user']}",
            link=t["link"],
            description=desc,
            pubdate=t["datetime"],
        )
    return feed.writeString('utf-8')

if __name__ == "__main__":
    asyncio.run(main())
    with open(WWW_ROOT + "feed.xml", "w") as f:
        f.write(gen_feed(save_tweets))
