from datetime import date

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


def get_current_season_year(today: date | None = None) -> int:
    today = today or date.today()
    return today.year if today.month >= 8 else today.year - 1


def get_position_movement(overall: dict) -> int:
    position = overall.get("position")
    starting_position = overall.get("startingPosition")
    if not isinstance(position, int) or not isinstance(starting_position, int):
        return 0
    return starting_position - position


def format_position_change(overall: dict) -> str:
    movement = get_position_movement(overall)
    if movement > 0:
        return f"🟢 ▲{movement}"
    if movement < 0:
        return f"🔴 ▼{abs(movement)}"
    return "⚪ —"


def format_ansi_position_change(overall: dict) -> str:
    movement = get_position_movement(overall)
    if movement > 0:
        color, indicator = 32, f"▲{movement}"
    elif movement < 0:
        color, indicator = 31, f"▼{abs(movement)}"
    else:
        color, indicator = 37, "—"
    return f"\x1b[{color}m{indicator:>4}\x1b[0m"


class Tables(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_table(self, matchweek: int | None = None):
        base_url = (
            "https://sdp-prem-prod.premier-league-prod.pulselive.com"
            f"/api/v5/competitions/8/seasons/{get_current_season_year()}"
        )

        if matchweek is None:
            url = f"{base_url}/standings"
        else:
            url = f"{base_url}/matchweeks/{matchweek}/standings"

        timeout = aiohttp.ClientTimeout(total=5)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                url,
                headers={
                    "Origin": "https://www.premierleague.com",
                    "Referer": "https://www.premierleague.com/",
                },
                timeout=timeout,
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_table_data(
        self,
        interaction: discord.Interaction,
        matchweek: int | None,
        previous: bool,
    ) -> dict | None:
        await interaction.response.defer()

        if previous and matchweek is not None:
            await interaction.followup.send(
                "Choose either a previous matchweek or a specific matchweek, not both."
            )
            return None

        try:
            if previous:
                current = await self.fetch_table()
                matchweek = current["matchweek"] - 1

                if matchweek < 1:
                    await interaction.followup.send(
                        "There isn't a previous matchweek yet."
                    )
                    return None

            data = await self.fetch_table(matchweek)

            if matchweek is not None and data.get("matchweek") != matchweek:
                await interaction.followup.send(
                    f"Standings for matchweek {matchweek} aren't available."
                )
                return None

            return data

        except aiohttp.ClientResponseError as exc:
            if exc.status == 404 and matchweek is not None:
                await interaction.followup.send(
                    f"Standings for matchweek {matchweek} aren't available."
                )
            else:
                await interaction.followup.send(
                    "Couldn't fetch the standings. Please try again later."
                )

        except (aiohttp.ClientError, TimeoutError, ValueError):
            await interaction.followup.send(
                "Couldn't fetch the standings. Please try again later."
            )

        return None

    def _simple_table_embed(self, data: dict) -> discord.Embed:
        entries = sorted(
            data["tables"][0]["entries"],
            key=lambda entry: entry["overall"]["position"],
        )

        groups = {"Top 10": [], "Mid Table": [], "Relegation Zone": []}

        for entry in entries:
            stats = entry["overall"]
            position = stats["position"]
            line = (
                f"{format_position_change(stats)} {position}. "
                f"{entry['team']['name']} – {stats['points']} pts"
            )

            if position <= 10:
                groups["Top 10"].append(line)
            elif position <= 17:
                groups["Mid Table"].append(line)
            else:
                groups["Relegation Zone"].append(line)

        embed = discord.Embed(
            title=f"{data['competition']['name']} {data['season']['name']}",
            description=f"Matchweek {data['matchweek']} Table",
            color=discord.Color.orange(),
        )

        for group_name, lines in groups.items():
            if lines:
                embed.add_field(name=group_name, value="\n".join(lines), inline=False)

        return embed

    def _detailed_table_embed(self, data: dict) -> discord.Embed:
        entries = sorted(
            data["tables"][0]["entries"],
            key=lambda entry: entry["overall"]["position"],
        )
        groups = {"Top 10": [], "Mid Table": [], "Relegation Zone": []}
        header = (
            f"{'#':>2} {'Move':>4} {'Team':<14} {'P':>2} {'W':>2} {'D':>2} "
            f"{'L':>2} {'GF':>3} {'GA':>3} {'GD':>4} {'Pts':>3}"
        )

        for entry in entries:
            team = entry["team"]
            stats = entry["overall"]
            name = team.get("shortName") or team["name"]
            position = stats["position"]
            goal_difference = stats["goalsFor"] - stats["goalsAgainst"]

            line = (
                f"{position:>2} {format_ansi_position_change(stats)} {name:<14.14} "
                f"{stats['played']:>2} "
                f"{stats['won']:>2} "
                f"{stats['drawn']:>2} "
                f"{stats['lost']:>2} "
                f"{stats['goalsFor']:>3} "
                f"{stats['goalsAgainst']:>3} "
                f"{goal_difference:>+4} "
                f"{stats['points']:>3}"
            )

            if position <= 10:
                groups["Top 10"].append(line)
            elif position <= 17:
                groups["Mid Table"].append(line)
            else:
                groups["Relegation Zone"].append(line)

        embed = discord.Embed(
            title=f"{data['competition']['name']} {data['season']['name']}",
            description=f"Matchweek {data['matchweek']} Table",
            color=discord.Color.orange(),
        )

        for group_name, lines in groups.items():
            if lines:
                table = "\n".join([header, *lines])
                embed.add_field(
                    name=group_name,
                    value=f"```ansi\n{table}\n```",
                    inline=False,
                )
        return embed

    async def _send_table(
        self,
        interaction: discord.Interaction,
        detailed: bool,
        matchweek: int | None,
        previous: bool,
    ):
        data = await self.get_table_data(interaction, matchweek, previous)
        if data is None:
            return

        embed = (
            self._detailed_table_embed(data)
            if detailed
            else self._simple_table_embed(data)
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="table", description="Show the simple Premier League table."
    )
    @app_commands.describe(
        matchweek="Show standings for a specific matchweek",
        previous="Show the previous matchweek's standings",
    )
    async def pl_table(
        self,
        interaction: discord.Interaction,
        matchweek: app_commands.Range[int, 1, 38] | None = None,
        previous: bool = False,
    ):
        await self._send_table(interaction, False, matchweek, previous)

    @app_commands.command(
        name="table-detailed",
        description="Show the detailed Premier League table.",
    )
    @app_commands.describe(
        matchweek="Show standings for a specific matchweek",
        previous="Show the previous matchweek's standings",
    )
    async def pl_table_detailed(
        self,
        interaction: discord.Interaction,
        matchweek: app_commands.Range[int, 1, 38] | None = None,
        previous: bool = False,
    ):
        await self._send_table(interaction, True, matchweek, previous)


async def setup(bot):
    await bot.add_cog(Tables(bot))
