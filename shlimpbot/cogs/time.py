import math
from typing import Optional, Dict, Callable

import dateparser
import pendulum
from nextcord.ext import commands
from pendulum.tz.zoneinfo.exceptions import InvalidTimezone


def delilah_time(dt: pendulum.DateTime) -> str:
    dt = dt.in_timezone('America/New_York')
    dt_plus_one = dt.add(hours=1)

    hour = (dt.hour if dt.minute > 58 or dt.minute < 38 else dt_plus_one.hour) % 12

    answer = ""

    if (minute := dt.minute) in [58, 59, 0, 1, 2]:
        answer += f"{hour} o'clock"
    elif minute in range(2, 8):
        answer += f"a long {hour}"
    elif minute in range(8, 14):
        answer += f"a short quarter past {hour}"
    elif minute in range(14, 16):
        answer += f"quarter past {hour}"
    elif minute in range(18, 23):
        answer += f"a long quarter past {hour}"
    elif minute in range(23, 29):
        answer += f"a short half past {hour}"
    elif minute in range(29, 32):
        answer += f"half past {hour}"
    elif minute in range(32, 38):
        answer += f"a long half past {hour}"
    elif minute in range(38, 44):
        answer += f"a long quarter until {hour}"
    elif minute in range(44, 47):
        answer += f"quarter until {hour}"
    elif minute in range(47, 52):
        answer += f"a short quarter until {hour}"
    else:
        answer += f'a short {hour}'

    return answer


def beats_time(dt: pendulum.DateTime) -> str:
    dt = dt.in_timezone('CET')
    beats = math.floor(((dt.minute * 60) + (dt.hour * 3600) + dt.second) / 86.4)
    return f"@{beats}"


BONUS_FORMATS: Dict[str, Callable[[pendulum.DateTime], str]] = {'delilah': delilah_time, 'beats': beats_time,
                                                                'internet': beats_time}


class TimeCog(commands.Cog):
    @commands.group()
    async def time(self, ctx: commands.Context):
        pass

    @time.command()
    async def now(self, ctx: commands.Context, *, timezone: Optional[str] = 'UTC'):
        if timezone in BONUS_FORMATS:
            return await ctx.reply(BONUS_FORMATS[timezone](pendulum.now()), mention_author=False)
        try:
            dt_now = pendulum.now(timezone)
        except InvalidTimezone:
            return await ctx.send(f"Didn't recognise timezone {timezone}")

        await ctx.reply(dt_now.to_rfc850_string(), mention_author=False)

    @time.command()
    async def codes(self, ctx: commands.Context, *, dt_string: Optional[str]):
        if dt_string:
            dt = dateparser.parse(dt_string)
            if dt is None:
                return await ctx.reply(f'{dt_string} is not a valid date string')
        else:
            dt = pendulum.now('UTC')

        unix_time = int(dt.timestamp())
        responses = []
        for suffix in ["", ":t", ":T", ":d", ":D", ":f", ":F", ":R"]:
            responses.append(f"`<t:{unix_time}{suffix}>`    <t:{unix_time}{suffix}>")

        await ctx.reply('\n'.join(responses), mention_author=False)


def setup(bot):
    bot.add_cog(TimeCog())
