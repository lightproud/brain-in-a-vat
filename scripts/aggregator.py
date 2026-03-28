#!/usr/bin/env python3
"""
忘却前夜 Morimens - 社区热点聚合器
从各社区平台抓取24小时内的热门话题并生成 data/news.json

数据源:
  - Reddit (r/Morimens)
  - Twitter/X (@MorimensGlobal, 相关hashtag)
  - Bilibili (忘却前夜相关)
  - TapTap (忘却前夜社区)
  - NGA (忘却前夜版块)
  - Discord (官方服务器摘要)
  - YouTube (官方频道及热门视频)

使用方式:
  1. 安装依赖: pip install -r requirements.txt
  2. 配置环境变量 (见 .env.example)
  3. 运行: python scripts/aggregator.py
  4. 输出: data/news.json
"""

import json
import os
import re
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_PATH = Path(__file__).parent.parent / 'data' / 'news.json'
SEARCH_KEYWORDS = ['忘却前夜', '忘卻前夜', 'Morimens', 'morimens']
HOURS_LOOKBACK = 24

# Valid source identifiers
VALID_SOURCES = {'reddit', 'bilibili', 'twitter', 'taptap', 'nga', 'discord', 'youtube', 'official'}

# Required fields for each news item
REQUIRED_FIELDS = {'title', 'source', 'time', 'engagement'}


# ============================================================
# Data Validation & Sanitization
# ============================================================

def strip_html_tags(text):
    """Remove any HTML tags from text to prevent XSS."""
    if not text:
        return ''
    return re.sub(r'<[^>]+>', '', text)


def sanitize_url(url):
    """Validate and normalize URL scheme."""
    if not url:
        return ''
    url = url.strip()
    # Normalize http to https for known platforms
    if url.startswith('http://www.bilibili.com') or url.startswith('http://bilibili.com'):
        url = url.replace('http://', 'https://', 1)
    # Basic URL validation
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https', ''):
        return ''
    return url


def sanitize_summary(summary):
    """Clean up summary text, removing placeholder values."""
    if not summary:
        return ''
    summary = summary.strip()
    # Filter out placeholder/empty summaries
    if summary in ('-', '--', '无', 'N/A', 'null', 'none', '暂无'):
        return ''
    return strip_html_tags(summary)


def validate_news_item(item):
    """
    Validate a single news item. Returns (is_valid, cleaned_item).
    Checks required fields, sanitizes text, normalizes URLs.
    """
    if not isinstance(item, dict):
        return False, None

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in item or not item[field]:
            logger.warning(f'Validation: missing required field "{field}" in item: {item.get("title", "unknown")[:50]}')
            return False, None

    # Validate source
    if item['source'] not in VALID_SOURCES:
        logger.warning(f'Validation: unknown source "{item["source"]}" for: {item["title"][:50]}')
        return False, None

    # Validate engagement is a non-negative number
    try:
        engagement = int(item['engagement'])
        if engagement < 0:
            engagement = 0
    except (ValueError, TypeError):
        engagement = 0

    # Validate time format (ISO 8601)
    try:
        if isinstance(item['time'], str):
            datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
    except (ValueError, TypeError):
        logger.warning(f'Validation: invalid time format for: {item["title"][:50]}')
        return False, None

    # Build cleaned item
    cleaned = {
        'title': strip_html_tags(str(item['title']).strip()),
        'summary': sanitize_summary(item.get('summary', '')),
        'source': item['source'],
        'time': item['time'],
        'url': sanitize_url(item.get('url', '')),
        'engagement': engagement,
        'is_hot': bool(item.get('is_hot', False)),
        'author': strip_html_tags(str(item.get('author', '')).strip()),
        'tags': [strip_html_tags(str(t).strip()) for t in item.get('tags', []) if t and str(t).strip()],
    }

    # Title must not be empty after sanitization
    if not cleaned['title']:
        return False, None

    return True, cleaned


def validate_all_news(items):
    """Validate and clean a list of news items. Returns list of valid items."""
    valid_items = []
    invalid_count = 0

    for item in items:
        is_valid, cleaned = validate_news_item(item)
        if is_valid:
            valid_items.append(cleaned)
        else:
            invalid_count += 1

    if invalid_count > 0:
        logger.warning(f'Validation: {invalid_count} invalid items filtered out of {len(items)} total')

    logger.info(f'Validation: {len(valid_items)} valid items out of {len(items)} total')
    return valid_items


def normalize_title(title):
    """Normalize a title for deduplication comparison."""
    t = title.lower().strip()
    # Remove common brackets and their contents like【】[]「」
    t = re.sub(r'[【\[「（(][^】\]」）)]*[】\]」）)]', '', t)
    # Remove punctuation and whitespace
    t = re.sub(r'[\s\-_·:：|｜,.，。!！?？…]+', '', t)
    return t


def title_similarity(a, b):
    """Simple character-level similarity ratio between two strings."""
    if not a or not b:
        return 0.0
    # Use length of common characters / max length
    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
    if len(longer) == 0:
        return 1.0
    # Count common characters (order-independent, bag-of-chars)
    from collections import Counter
    ca, cb = Counter(shorter), Counter(longer)
    common = sum((ca & cb).values())
    return common / len(longer)


def deduplicate_news(items, similarity_threshold=0.75):
    """Deduplicate news items using normalized title similarity.
    When duplicates are found, keep the one with higher engagement."""
    unique = []
    norm_titles = []

    for item in items:
        norm = normalize_title(item['title'])
        is_dup = False
        for i, existing_norm in enumerate(norm_titles):
            # Exact normalized match or high similarity
            if norm == existing_norm or (len(norm) > 5 and title_similarity(norm, existing_norm) > similarity_threshold):
                # Keep higher engagement version
                if item.get('engagement', 0) > unique[i].get('engagement', 0):
                    unique[i] = item
                    norm_titles[i] = norm
                is_dup = True
                break
        if not is_dup:
            unique.append(item)
            norm_titles.append(norm)

    logger.info(f'Deduplication: {len(unique)} unique items from {len(items)} total')
    return unique


# ============================================================
# HTTP Helpers
# ============================================================

def request_with_retry(method, url, max_retries=3, backoff_base=2, **kwargs):
    """Make an HTTP request with exponential backoff retry on transient failures."""
    import requests

    kwargs.setdefault('timeout', 15)
    last_exc = None

    for attempt in range(max_retries + 1):
        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.exceptions.ConnectionError as e:
            last_exc = e
            logger.warning(f'Connection error (attempt {attempt + 1}/{max_retries + 1}): {e}')
        except requests.exceptions.Timeout as e:
            last_exc = e
            logger.warning(f'Timeout (attempt {attempt + 1}/{max_retries + 1}): {e}')
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            if status in (429, 500, 502, 503, 504):
                last_exc = e
                logger.warning(f'HTTP {status} (attempt {attempt + 1}/{max_retries + 1}): {e}')
            else:
                raise
        except requests.exceptions.RequestException:
            raise

        if attempt < max_retries:
            wait = backoff_base ** attempt
            logger.info(f'Retrying in {wait}s...')
            time.sleep(wait)

    raise last_exc


# ============================================================
# Source Fetchers - each returns a list of news item dicts
# ============================================================

def fetch_reddit(subreddits=None):
    """Fetch posts from Reddit: hot/new/rising per subreddit + cross-subreddit keyword search."""

    subreddits = subreddits or ['Morimens', 'MorimensGame']
    items = []
    seen_ids = set()
    headers = {'User-Agent': 'MorimensAggregator/1.0'}

    def _parse_post(d):
        post_id = d.get('id', '')
        if post_id in seen_ids:
            return None
        seen_ids.add(post_id)
        created = datetime.fromtimestamp(d['created_utc'], tz=timezone.utc)
        if datetime.now(timezone.utc) - created > timedelta(hours=HOURS_LOOKBACK):
            return None
        return {
            'title': d['title'],
            'summary': (d.get('selftext', '') or '')[:200],
            'source': 'reddit',
            'time': created.isoformat(),
            'url': f"https://reddit.com{d['permalink']}",
            'engagement': d.get('score', 0) + d.get('num_comments', 0),
            'is_hot': d.get('score', 0) > 100,
            'author': f"u/{d.get('author', 'unknown')}",
            'tags': list({f.get('text', '') for f in d.get('link_flair_richtext', []) if f.get('text')}),
        }

    # Fetch hot, new, rising for each subreddit
    for sub in subreddits:
        for feed in ['hot', 'new', 'rising']:
            url = f'https://www.reddit.com/r/{sub}/{feed}.json?limit=25'
            try:
                resp = request_with_retry('GET', url, headers=headers)
                posts = resp.json().get('data', {}).get('children', [])
                for post in posts:
                    item = _parse_post(post['data'])
                    if item:
                        items.append(item)
            except Exception as e:
                logger.warning(f'Reddit r/{sub}/{feed} failed: {e}')
            time.sleep(0.3)  # Rate limiting

    # Cross-subreddit keyword search
    for keyword in ['Morimens', '忘却前夜']:
        url = 'https://www.reddit.com/search.json'
        params = {'q': keyword, 'sort': 'new', 'limit': 25, 't': 'day'}
        try:
            resp = request_with_retry('GET', url, headers=headers, params=params)
            posts = resp.json().get('data', {}).get('children', [])
            for post in posts:
                item = _parse_post(post['data'])
                if item:
                    items.append(item)
        except Exception as e:
            logger.warning(f'Reddit search "{keyword}" failed: {e}')
        time.sleep(0.3)

    logger.info(f'Reddit: fetched {len(items)} posts total')
    return items


def fetch_bilibili(max_pages=3):
    """Fetch Bilibili search results for Morimens keywords (multi-page)."""

    items = []
    seen_bvids = set()

    for keyword in ['忘却前夜', '忘卻前夜']:
        for page in range(1, max_pages + 1):
            url = 'https://api.bilibili.com/x/web-interface/search/type'
            params = {
                'search_type': 'video',
                'keyword': keyword,
                'order': 'pubdate',
                'duration': 0,
                'page': page,
            }
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://www.bilibili.com',
            }
            try:
                resp = request_with_retry('GET', url, params=params, headers=headers)
                results = resp.json().get('data', {}).get('result', []) or []
                if not results:
                    break

                found_old = False
                for v in results[:20]:
                    pubdate = v.get('pubdate', 0)
                    created = datetime.fromtimestamp(pubdate, tz=timezone.utc) if pubdate else None
                    if created and datetime.now(timezone.utc) - created > timedelta(hours=HOURS_LOOKBACK):
                        found_old = True
                        continue

                    # Deduplicate across keywords by bvid
                    bvid = v.get('bvid', '')
                    if bvid and bvid in seen_bvids:
                        continue
                    if bvid:
                        seen_bvids.add(bvid)

                    title = strip_html_tags(v.get('title', ''))
                    # Weighted engagement: play + danmaku*2 + favorites*3 + review*2
                    play = v.get('play', 0) if isinstance(v.get('play'), int) else 0
                    danmaku = v.get('danmaku', 0) if isinstance(v.get('danmaku'), int) else 0
                    favorites = v.get('favorites', 0) if isinstance(v.get('favorites'), int) else 0
                    review = v.get('review', 0) if isinstance(v.get('review'), int) else 0
                    engagement = play + danmaku * 2 + favorites * 3 + review * 2

                    items.append({
                        'title': title,
                        'summary': v.get('description', '')[:200],
                        'source': 'bilibili',
                        'time': created.isoformat() if created else datetime.now(timezone.utc).isoformat(),
                        'url': v.get('arcurl', ''),
                        'engagement': engagement,
                        'is_hot': play > 10000,
                        'author': v.get('author', ''),
                        'tags': [v.get('typename', '')] if v.get('typename') else [],
                    })

                logger.info(f'Bilibili "{keyword}" page {page}: fetched {len(results)} videos')

                # Stop paging if we hit old content
                if found_old:
                    break

                # Rate limiting between pages
                if page < max_pages:
                    time.sleep(0.5)

            except Exception as e:
                logger.warning(f'Bilibili "{keyword}" page {page} failed: {e}')
                break

    return items


def fetch_bilibili_articles(max_pages=2):
    """Fetch Bilibili article (专栏) search results for Morimens keywords."""

    items = []
    seen_ids = set()

    for keyword in ['忘却前夜', '忘卻前夜']:
        for page in range(1, max_pages + 1):
            url = 'https://api.bilibili.com/x/web-interface/search/type'
            params = {
                'search_type': 'article',
                'keyword': keyword,
                'order': 'pubdate',
                'page': page,
            }
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://www.bilibili.com',
            }
            try:
                resp = request_with_retry('GET', url, params=params, headers=headers)
                results = resp.json().get('data', {}).get('result', []) or []
                if not results:
                    break

                found_old = False
                for a in results[:20]:
                    pub_time = a.get('pub_time', '')
                    try:
                        created = datetime.fromisoformat(pub_time.replace('Z', '+00:00')) if pub_time else None
                    except (ValueError, TypeError):
                        created = None
                    if created and datetime.now(timezone.utc) - created > timedelta(hours=HOURS_LOOKBACK):
                        found_old = True
                        continue

                    article_id = a.get('id', '')
                    if article_id in seen_ids:
                        continue
                    seen_ids.add(article_id)

                    title = strip_html_tags(a.get('title', ''))
                    view = a.get('view', 0) if isinstance(a.get('view'), int) else 0
                    like = a.get('like', 0) if isinstance(a.get('like'), int) else 0
                    reply = a.get('reply', 0) if isinstance(a.get('reply'), int) else 0
                    engagement = view + like * 3 + reply * 2

                    items.append({
                        'title': title,
                        'summary': strip_html_tags(a.get('desc', ''))[:200],
                        'source': 'bilibili',
                        'time': created.isoformat() if created else datetime.now(timezone.utc).isoformat(),
                        'url': f"https://www.bilibili.com/read/cv{article_id}" if article_id else '',
                        'engagement': engagement,
                        'is_hot': view > 10000,
                        'author': a.get('author', {}).get('name', '') if isinstance(a.get('author'), dict) else str(a.get('author', '')),
                        'tags': [c.get('name', '') for c in a.get('categories', []) if c.get('name')] if isinstance(a.get('categories'), list) else ['专栏'],
                    })

                logger.info(f'Bilibili articles "{keyword}" page {page}: {len(results)} articles')
                if found_old:
                    break
                if page < max_pages:
                    time.sleep(0.5)

            except Exception as e:
                logger.warning(f'Bilibili articles "{keyword}" page {page} failed: {e}')
                break

    logger.info(f'Bilibili articles: {len(items)} total')
    return items


def fetch_twitter():
    """
    Fetch tweets using Twitter/X API v2.
    Requires TWITTER_BEARER_TOKEN environment variable.
    """

    bearer = os.environ.get('TWITTER_BEARER_TOKEN')
    if not bearer:
        logger.warning('Twitter: TWITTER_BEARER_TOKEN not set, skipping')
        return []

    items = []
    query = '(忘却前夜 OR 忘卻前夜 OR Morimens) -is:retweet'
    url = 'https://api.twitter.com/2/tweets/search/recent'
    params = {
        'query': query,
        'max_results': 50,
        'tweet.fields': 'created_at,public_metrics,author_id,entities',
        'expansions': 'author_id',
        'user.fields': 'username',
    }
    headers = {'Authorization': f'Bearer {bearer}'}

    try:
        resp = request_with_retry('GET', url, params=params, headers=headers)
        data = resp.json()
        users = {u['id']: u['username'] for u in data.get('includes', {}).get('users', [])}
        for tweet in data.get('data', []):
            metrics = tweet.get('public_metrics', {})
            engagement = metrics.get('like_count', 0) + metrics.get('reply_count', 0) + metrics.get('retweet_count', 0)

            # Extract hashtags from entities
            entities = tweet.get('entities', {})
            hashtags = [f"#{h['tag']}" for h in entities.get('hashtags', [])] if entities.get('hashtags') else []

            # Detect media type for tags
            if entities.get('urls'):
                for u in entities['urls']:
                    if 'pic.twitter.com' in u.get('expanded_url', '') or 'pbs.twimg.com' in u.get('expanded_url', ''):
                        if '图片' not in hashtags:
                            hashtags.append('图片')
                        break

            items.append({
                'title': tweet['text'][:100],
                'summary': tweet['text'][:200],
                'source': 'twitter',
                'time': tweet['created_at'],
                'url': f"https://twitter.com/i/status/{tweet['id']}",
                'engagement': engagement,
                'is_hot': engagement > 500,
                'author': f"@{users.get(tweet['author_id'], 'unknown')}",
                'tags': hashtags[:5],
            })
        logger.info(f'Twitter: fetched {len(items)} tweets')
    except Exception as e:
        logger.warning(f'Twitter failed: {e}')

    return items


def fetch_nga():
    """
    Fetch NGA forum posts for Morimens.
    NGA has rate limiting - be respectful.
    """

    items = []
    # NGA forum ID for 忘却前夜 - update this with the actual forum ID
    nga_fid = os.environ.get('NGA_FORUM_ID', '')
    if not nga_fid:
        logger.info('NGA: NGA_FORUM_ID not set, skipping')
        return []

    url = f'https://bbs.nga.cn/thread.php?fid={nga_fid}&ajax=1'
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
    }
    try:
        resp = request_with_retry('GET', url, headers=headers)
        data = resp.json()
        threads = data.get('data', {}).get('__T', {})
        for tid, thread in threads.items():
            postdate = thread.get('postdate', 0)
            if isinstance(postdate, str):
                continue
            created = datetime.fromtimestamp(postdate, tz=timezone.utc)
            if datetime.now(timezone.utc) - created > timedelta(hours=HOURS_LOOKBACK):
                continue
            replies = thread.get('replies', 0)
            items.append({
                'title': thread.get('subject', ''),
                'summary': '',
                'source': 'nga',
                'time': created.isoformat(),
                'url': f"https://bbs.nga.cn/read.php?tid={tid}",
                'engagement': replies,
                'is_hot': replies > 50,
                'author': thread.get('author', ''),
                'tags': [],
            })
        logger.info(f'NGA: fetched {len(items)} threads')
    except Exception as e:
        logger.warning(f'NGA failed: {e}')

    return items


def fetch_taptap():
    """Fetch TapTap community posts for Morimens."""

    app_id = os.environ.get('TAPTAP_APP_ID', '')
    if not app_id:
        logger.info('TapTap: TAPTAP_APP_ID not set, skipping')
        return []

    items = []
    url = f'https://api.taptap.cn/app/v2/app/{app_id}/topic/list'
    params = {'type': 'hot', 'limit': 20}
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        resp = request_with_retry('GET', url, params=params, headers=headers)
        topics = resp.json().get('data', {}).get('list', [])
        for topic in topics:
            created = datetime.fromtimestamp(topic.get('created_time', 0), tz=timezone.utc)
            if datetime.now(timezone.utc) - created > timedelta(hours=HOURS_LOOKBACK):
                continue
            items.append({
                'title': topic.get('title', ''),
                'summary': topic.get('summary', '')[:200],
                'source': 'taptap',
                'time': created.isoformat(),
                'url': topic.get('share_url', ''),
                'engagement': topic.get('comment_count', 0) + topic.get('like_count', 0),
                'is_hot': topic.get('like_count', 0) > 100,
                'author': topic.get('user', {}).get('name', ''),
                'tags': [],
            })
        logger.info(f'TapTap: fetched {len(items)} topics')
    except Exception as e:
        logger.warning(f'TapTap failed: {e}')

    return items


def fetch_youtube():
    """
    Fetch YouTube videos about Morimens.
    Uses YouTube Data API v3 if YOUTUBE_API_KEY is set,
    otherwise falls back to RSS feed from channel.
    """
    import xml.etree.ElementTree as ET

    api_key = os.environ.get('YOUTUBE_API_KEY', '')
    channel_id = os.environ.get('YOUTUBE_CHANNEL_ID', '')
    items = []

    if api_key:
        # YouTube Data API v3
        for keyword in ['Morimens', '忘却前夜']:
            url = 'https://www.googleapis.com/youtube/v3/search'
            params = {
                'part': 'snippet',
                'q': keyword,
                'type': 'video',
                'order': 'date',
                'publishedAfter': (datetime.now(timezone.utc) - timedelta(hours=HOURS_LOOKBACK)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'maxResults': 20,
                'key': api_key,
            }
            try:
                resp = request_with_retry('GET', url, params=params)
                data = resp.json()
                video_ids = [item['id']['videoId'] for item in data.get('items', []) if item.get('id', {}).get('videoId')]

                # Batch fetch statistics
                if video_ids:
                    stats_url = 'https://www.googleapis.com/youtube/v3/videos'
                    stats_params = {
                        'part': 'statistics',
                        'id': ','.join(video_ids),
                        'key': api_key,
                    }
                    stats_resp = request_with_retry('GET', stats_url, params=stats_params)
                    stats_map = {v['id']: v.get('statistics', {}) for v in stats_resp.json().get('items', [])}
                else:
                    stats_map = {}

                for item in data.get('items', []):
                    snippet = item.get('snippet', {})
                    vid = item.get('id', {}).get('videoId', '')
                    if not vid:
                        continue
                    published = snippet.get('publishedAt', '')
                    stats = stats_map.get(vid, {})
                    views = int(stats.get('viewCount', 0))
                    likes = int(stats.get('likeCount', 0))
                    comments = int(stats.get('commentCount', 0))

                    items.append({
                        'title': snippet.get('title', ''),
                        'summary': snippet.get('description', '')[:200],
                        'source': 'youtube',
                        'time': published,
                        'url': f'https://www.youtube.com/watch?v={vid}',
                        'engagement': views + likes * 5 + comments * 3,
                        'is_hot': views > 50000,
                        'author': snippet.get('channelTitle', ''),
                        'tags': [],
                    })
                logger.info(f'YouTube API "{keyword}": {len(data.get("items", []))} videos')
            except Exception as e:
                logger.warning(f'YouTube API "{keyword}" failed: {e}')
            time.sleep(0.2)

    elif channel_id:
        # RSS fallback - no API key needed, but limited to channel uploads
        rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
        try:
            resp = request_with_retry('GET', rss_url)
            root = ET.fromstring(resp.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'media': 'http://search.yahoo.com/mrss/'}

            for entry in root.findall('atom:entry', ns):
                title = entry.findtext('atom:title', '', ns)
                published = entry.findtext('atom:published', '', ns)
                link = entry.find('atom:link', ns)
                href = link.get('href', '') if link is not None else ''
                author = entry.findtext('atom:author/atom:name', '', ns)

                try:
                    pub_dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    if datetime.now(timezone.utc) - pub_dt > timedelta(hours=HOURS_LOOKBACK):
                        continue
                except (ValueError, TypeError):
                    continue

                media_stats = entry.find('media:group/media:community/media:statistics', ns)
                views = int(media_stats.get('views', 0)) if media_stats is not None else 0

                items.append({
                    'title': title,
                    'summary': '',
                    'source': 'youtube',
                    'time': pub_dt.isoformat(),
                    'url': href,
                    'engagement': views,
                    'is_hot': views > 50000,
                    'author': author,
                    'tags': [],
                })
            logger.info(f'YouTube RSS: {len(items)} videos from channel feed')
        except Exception as e:
            logger.warning(f'YouTube RSS failed: {e}')

    else:
        logger.info('YouTube: no YOUTUBE_API_KEY or YOUTUBE_CHANNEL_ID set, skipping')

    return items


def generate_summary(news_items):
    """
    Generate a daily summary. Uses OpenAI-compatible API if available,
    otherwise falls back to a simple extractive summary.
    """
    api_key = os.environ.get('LLM_API_KEY')
    api_url = os.environ.get('LLM_API_URL', 'https://api.anthropic.com/v1/messages')

    if not api_key or not news_items:
        # Fallback: simple extractive summary
        hot = [n for n in news_items if n.get('is_hot')]
        if not hot:
            hot = news_items[:5]
        titles = '；'.join(n['title'][:30] for n in hot[:5])
        return f"今日热门话题：{titles}。"

    # Use LLM for better summary
    import requests

    titles_text = '\n'.join(f"- [{n['source']}] {n['title']}" for n in news_items[:20])
    prompt = f"""以下是忘却前夜(Morimens)游戏社区24小时内的热点话题列表，请用中文生成一段简洁的今日总结(100-150字)，
突出最重要的2-3个话题，使用<span class='highlight'>标签</span>标记关键词：

{titles_text}"""

    try:
        resp = requests.post(
            api_url,
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'claude-haiku-4-5-20251001',
                'max_tokens': 300,
                'messages': [{'role': 'user', 'content': prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()['content'][0]['text']
    except Exception as e:
        logger.warning(f'LLM summary failed: {e}, using fallback')
        hot = [n for n in news_items if n.get('is_hot')][:5]
        titles = '；'.join(n['title'][:30] for n in hot)
        return f"今日热门话题：{titles}。"


def load_previous_news():
    """Load the previous news.json for rollback protection."""
    try:
        if OUTPUT_PATH.exists():
            with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('news', [])
    except Exception as e:
        logger.warning(f'Failed to load previous news.json: {e}')
    return []


def run():
    """Main aggregation pipeline with concurrent fetching and rollback protection."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    logger.info('Starting Morimens community news aggregation...')

    # All fetchers including new ones
    fetchers = [
        ('reddit', fetch_reddit),
        ('bilibili', fetch_bilibili),
        ('bilibili_articles', fetch_bilibili_articles),
        ('twitter', fetch_twitter),
        ('nga', fetch_nga),
        ('taptap', fetch_taptap),
        ('youtube', fetch_youtube),
    ]

    all_news = []
    source_stats = {}

    # Concurrent fetching
    def _run_fetcher(name, fetcher):
        fetch_start = time.time()
        try:
            items = fetcher()
            elapsed = int((time.time() - fetch_start) * 1000)
            return name, items, {
                'status': 'ok' if items else 'empty',
                'count': len(items),
                'time_ms': elapsed,
            }
        except Exception as e:
            elapsed = int((time.time() - fetch_start) * 1000)
            logger.error(f'{name} fetcher crashed: {e}')
            return name, [], {
                'status': 'error',
                'count': 0,
                'time_ms': elapsed,
                'error': str(e)[:100],
            }

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(_run_fetcher, name, fn): name
            for name, fn in fetchers
        }
        for future in as_completed(futures):
            name, items, stats = future.result()
            all_news.extend(items)
            source_stats[name] = stats
            logger.info(f'{name}: {stats["count"]} items ({stats["time_ms"]}ms)')

    # Validate and sanitize all items
    all_news = validate_all_news(all_news)

    # Deduplicate by normalized title similarity
    unique_news = deduplicate_news(all_news)

    # Rollback protection: if new fetch got significantly fewer items than before,
    # merge with previous data to avoid data loss
    previous_news = load_previous_news()
    if previous_news and len(unique_news) == 0:
        logger.warning('Rollback: all fetchers returned empty, preserving previous data')
        # Re-validate previous data (filter out items older than 48h)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
        preserved = []
        for item in previous_news:
            try:
                item_time = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
                if item_time > cutoff:
                    preserved.append(item)
            except (ValueError, KeyError):
                pass
        unique_news = preserved
        logger.info(f'Rollback: preserved {len(preserved)} items from previous run')

    # Sort by engagement
    unique_news.sort(key=lambda x: x.get('engagement', 0), reverse=True)

    # Mark top items as hot (only if engagement meets minimum threshold)
    HOT_MIN_ENGAGEMENT = 50
    for item in unique_news[:5]:
        if item.get('engagement', 0) >= HOT_MIN_ENGAGEMENT:
            item['is_hot'] = True

    # Generate summary
    summary = generate_summary(unique_news)

    # Write output
    output = {
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'summary': summary,
        'stats': {
            'total_fetched': sum(s['count'] for s in source_stats.values()),
            'total_after_validation': len(all_news),
            'total_after_dedup': len(unique_news),
            'sources': source_stats,
        },
        'news': unique_news,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.info(f'Done! {len(unique_news)} items written to {OUTPUT_PATH}')


if __name__ == '__main__':
    run()
