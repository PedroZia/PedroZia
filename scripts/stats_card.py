"""Gera stats.svg: ficha de personagem RPG com os números reais do GitHub.
Uso: GITHUB_TOKEN=... python scripts/stats_card.py <login> <saida.svg>"""
import base64, json, math, os, sys, urllib.request
from datetime import datetime, timezone
from html import escape

API = "https://api.github.com/graphql"


def gql(query, **variables):
    req = urllib.request.Request(API, json.dumps({"query": query, "variables": variables}).encode(),
                                 {"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]


def fetch(login):
    u = gql("""query($l:String!){user(login:$l){name createdAt avatarUrl(size:32) followers{totalCount}
      pullRequests{totalCount} issues{totalCount}
      repositories(ownerAffiliations:OWNER,first:100,isFork:false){totalCount
        nodes{stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}""",
            l=login)["user"]
    start = int(u["createdAt"][:4])
    now = datetime.now(timezone.utc)
    # contributionsCollection só cobre 1 ano por chamada: um alias por ano
    parts = " ".join(
        f'y{y}:contributionsCollection(from:"{y}-01-01T00:00:00Z",to:"{min(datetime(y, 12, 31, 23, 59, 59, tzinfo=timezone.utc), now).isoformat()}")'
        "{totalCommitContributions restrictedContributionsCount totalPullRequestReviewContributions"
        " contributionCalendar{weeks{contributionDays{contributionCount}}}}"
        for y in range(start, now.year + 1))
    years = gql(f'query($l:String!){{user(login:$l){{{parts}}}}}', l=login)["user"].values()
    days = [d["contributionCount"] for y in years for w in y["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    best = cur = 0
    for c in days:
        cur = cur + 1 if c else 0
        best = max(best, cur)
    langs = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    avatar = urllib.request.urlopen(u["avatarUrl"], timeout=30)
    return {
        "name": u["name"] or login,
        "avatar": f"data:{avatar.headers.get_content_type()};base64,{base64.b64encode(avatar.read()).decode()}",
        "lang": max(langs, key=langs.get) if langs else "Code",
        "years": (now - datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))).days // 365,
        "commits": sum(y["totalCommitContributions"] + y["restrictedContributionsCount"] for y in years),
        "prs": u["pullRequests"]["totalCount"],
        "reviews": sum(y["totalPullRequestReviewContributions"] for y in years),
        "issues": u["issues"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "streak": best,
    }


# fonte pixel 5x7: uma string de bits por linha
GLYPHS = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 10001 11001 10101 10011 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11111 00010 00100 00010 00001 10001 01110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    ">": "01000 00100 00010 00001 00010 00100 01000", "-": "00000 00000 00000 11111 00000 00000 00000",
    " ": "00000 00000 00000 00000 00000 00000 00000",
}


def pixel_text(text, x, y, cell, cls):
    """Texto em fonte pixel; pixels vizinhos na mesma linha viram um só <rect>."""
    out = []
    for i, ch in enumerate(text.upper()):
        for r, bits in enumerate(GLYPHS.get(ch, GLYPHS[" "]).split()):
            c = 0
            while c < 5:
                if bits[c] == "1":
                    n = len(bits[c:]) - len(bits[c:].lstrip("1"))
                    out.append(f'<rect x="{x + (i * 6 + c) * cell:g}" y="{y + r * cell:g}" width="{n * cell:g}" height="{cell:g}"/>')
                    c += n
                else:
                    c += 1
    return f'<g class="{cls}">{"".join(out)}</g>'


CLASSES = {"Java": "Knight", "Python": "Wizard", "JavaScript": "Rogue", "TypeScript": "Paladin", "C": "Barbarian",
           "C++": "Warlord", "Go": "Ranger", "Rust": "Artificer", "HTML": "Bard", "CSS": "Illusionist"}
# (atributo, chave, valor que dá 20, singular, plural)
ATTRS = [("STR", "commits", 3000, "commit", "commits"), ("DEX", "prs", 500, "pull request", "pull requests"),
         ("INT", "reviews", 300, "review", "reviews"), ("WIS", "years", 15, "year on GitHub", "years on GitHub"),
         ("CHA", "followers", 500, "follower", "followers"), ("CON", "streak", 365, "day best streak", "day best streak")]


def attr(v, cap):
    return max(1, min(20, round(20 * math.log10(v + 1) / math.log10(cap + 1))))


def level(s):
    xp = s["commits"] + 5 * s["prs"] + 3 * s["reviews"] + 2 * s["issues"] + 10 * s["stars"] + 5 * s["followers"]
    lv = int(math.sqrt(xp / 10)) + 1  # nível L começa em 10*(L-1)^2 xp
    lo, hi = 10 * (lv - 1) ** 2, 10 * lv ** 2
    return lv, xp - lo, hi - lo


def render(s):
    lv, xp, need = level(s)
    cls = CLASSES.get(s["lang"], "Adventurer")
    W, H, X = 880, 440, 324
    name_cell = min(3, 256 / (len(s["name"]) * 6))
    rows = []
    for i, (abbr, key, cap, one, many) in enumerate(ATTRS):
        a, y = attr(s[key], cap), 68 + i * 48
        pips = "".join(f'<rect class="pip{" on" if p < a else ""}" x="{432 + p * 18}" y="{y + 3}" width="14" height="14" rx="2"'
                       f' style="animation-delay:{0.4 + i * .1 + p * .03:.2f}s"/>' for p in range(20))
        rows.append(pixel_text(abbr, X, y, 3, "fg") +
                    f'<text class="num" x="392" y="{y + 19}">{a}</text>{pips}'
                    f'<text class="cap" x="432" y="{y + 36}">{s[key]:,} {one if s[key] == 1 else many}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(s['name'])}: level {lv} {s['lang']} {cls}, {s['commits']} commits, {s['prs']} pull requests">
<style>
:root{{--card:#151b23;--line:#3d444d;--fg:#f0f6fc;--mut:#9198a1;--green:#3fb950;--off:#3d444d;--gold:#e3b341}}
@media (prefers-color-scheme:light){{:root{{--card:#f6f8fa;--line:#d1d9e0;--fg:#1f2328;--mut:#59636e;--green:#1a7f37;--off:#d1d9e0;--gold:#bf8700}}}}
.fg{{fill:var(--fg)}} .mut{{fill:var(--mut)}}
.num{{font:700 20px -apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',sans-serif;fill:var(--fg)}}
.cap,.mono{{font:11px ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace;fill:var(--mut)}}
.pip{{fill:var(--off)}} .pip.on{{fill:var(--green);opacity:0;animation:in .2s ease-out forwards}}
.bar{{transform-box:fill-box;transform:scaleX(0);animation:grow 1.8s cubic-bezier(.2,.8,.3,1) 1s forwards}}
@keyframes in{{to{{opacity:1}}}} @keyframes grow{{to{{transform:scaleX(1)}}}}
@media (prefers-reduced-motion:reduce){{.pip.on{{opacity:1;animation:none}}.bar{{transform:none;animation:none}}}}
</style>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="var(--card)" stroke="var(--line)"/>
<rect x="23" y="23" width="256" height="256" rx="6" fill="none" stroke="var(--green)" stroke-width="2"/>
<image href="{s['avatar']}" x="31" y="31" width="240" height="240" style="image-rendering:pixelated" preserveAspectRatio="xMidYMid slice"/>
{pixel_text(s["name"], 31, 296, name_cell, "fg")}
<text class="mono" x="31" y="342" style="fill:var(--green);font-size:12px;letter-spacing:1px">LEVEL {lv} {escape(s['lang'].upper())} {cls.upper()}</text>
<text class="mono" x="31" y="362">class from top language · {escape(s['lang'])}</text>
{pixel_text("ATTRIBUTES", X, 34, 2, "mut")}
{"".join(rows)}
{pixel_text(f"XP  LV {lv} > {lv + 1}", X, 372, 2, "mut")}
<text class="mono" x="810" y="384" text-anchor="end">{xp:,} / {need:,} xp this level</text>
<rect x="{X}" y="394" width="486" height="18" rx="4" fill="var(--off)"/>
<rect class="bar" x="{X}" y="394" width="{486 * xp / need:.1f}" height="18" rx="4" fill="var(--gold)"/>
</svg>'''


if __name__ == "__main__":
    assert attr(0, 500) == 1 and attr(500, 500) == 20 and attr(10**6, 500) == 20
    assert level({"commits": 0, "prs": 0, "reviews": 0, "issues": 0, "stars": 0, "followers": 0}) == (1, 0, 10)
    assert pixel_text("I", 0, 0, 1, "c").count("<rect") == 7  # I: barra, 5 hastes, barra
    login, out = sys.argv[1], sys.argv[2]
    stats = fetch(login)
    print({k: v for k, v in stats.items() if k != "avatar"})
    open(out, "w", encoding="utf-8").write(render(stats))
