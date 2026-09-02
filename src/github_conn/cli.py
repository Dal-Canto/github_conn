"""Command-line interface for github_conn."""

import json
import logging
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from .client import GitHubClient
from .exceptions import (
    GitHubConnException,
    NotFoundError,
    UnauthorizedError,
    AuthenticationError,
)

console = Console()


def setup_logging(verbose: bool) -> None:
    """Setup logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@click.group()
@click.option(
    "--token",
    envvar="GITHUB_TOKEN",
    help="GitHub personal access token",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def main(ctx: click.Context, token: Optional[str], verbose: bool) -> None:
    """GitHub API CLI client - Easy access to GitHub data from terminal."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["client"] = GitHubClient(token=token)
    ctx.obj["token"] = token


@main.command()
@click.argument("username")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def user(ctx: click.Context, username: str, output_json: bool) -> None:
    """Get user profile information."""
    try:
        client: GitHubClient = ctx.obj["client"]
        user_data = client.get_user(username)

        if output_json:
            click.echo(json.dumps(user_data, indent=2))
        else:
            table = Table(title=f"User: {username}")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")

            for key, value in user_data.items():
                table.add_row(key, str(value))

            console.print(table)

    except NotFoundError:
        console.print(f"[red]Error: User '{username}' not found[/red]")
    except UnauthorizedError:
        console.print("[red]Error: Invalid authentication token[/red]")
    except GitHubConnException as e:
        console.print(f"[red]Error: {e}[/red]")


@main.command()
@click.argument("username")
@click.option("--per-page", default=30, help="Results per page (max 100)")
@click.option("--page", default=1, help="Page number")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def repos(
    ctx: click.Context,
    username: str,
    per_page: int,
    page: int,
    output_json: bool,
) -> None:
    """List repositories for a user."""
    try:
        client: GitHubClient = ctx.obj["client"]
        repos_data = client.get_repos(username, per_page=per_page, page=page)

        if output_json:
            click.echo(json.dumps(repos_data, indent=2))
        else:
            table = Table(title=f"Repositories - {username} (Page {page})")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="green")
            table.add_column("Language", style="yellow")
            table.add_column("Stars", style="magenta")

            for repo in repos_data:
                table.add_row(
                    repo["name"],
                    repo.get("description") or "N/A",
                    repo.get("language") or "N/A",
                    str(repo.get("stargazers_count", 0)),
                )

            console.print(table)
            console.print(
                f"\n[dim]Showing {len(repos_data)} repositories[/dim]"
            )

    except NotFoundError:
        console.print(f"[red]Error: User '{username}' not found[/red]")
    except GitHubConnException as e:
        console.print(f"[red]Error: {e}[/red]")


@main.command()
@click.argument("username")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def repos_names(ctx: click.Context, username: str, output_json: bool) -> None:
    """List repository names only."""
    try:
        client: GitHubClient = ctx.obj["client"]
        names = client.get_repo_names(username)

        if output_json:
            click.echo(json.dumps(names, indent=2))
        else:
            console.print(f"[bold]Repositories for {username}:[/bold]")
            for name in names:
                click.echo(f"  • {name}")
            console.print(f"\n[dim]Total: {len(names)} repositories[/dim]")

    except NotFoundError:
        console.print(f"[red]Error: User '{username}' not found[/red]")
    except GitHubConnException as e:
        console.print(f"[red]Error: {e}[/red]")


@main.command()
@click.argument("username")
@click.option("--per-page", default=30, help="Results per page (max 100)")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def followers(
    ctx: click.Context, username: str, per_page: int, output_json: bool
) -> None:
    """List followers for a user."""
    try:
        client: GitHubClient = ctx.obj["client"]
        followers_data = client.get_followers(username, per_page=per_page)

        if output_json:
            click.echo(json.dumps(followers_data, indent=2))
        else:
            console.print(f"[bold]Followers of {username}:[/bold]")
            for follower in followers_data:
                click.echo(f"  • {follower}")
            console.print(
                f"\n[dim]Total: {len(followers_data)} followers[/dim]"
            )

    except NotFoundError:
        console.print(f"[red]Error: User '{username}' not found[/red]")
    except GitHubConnException as e:
        console.print(f"[red]Error: {e}[/red]")


@main.command()
@click.argument("username")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def following(ctx: click.Context, username: str, output_json: bool) -> None:
    """List users that someone is following."""
    try:
        client: GitHubClient = ctx.obj["client"]
        following_data = client.get_following(username)

        if output_json:
            click.echo(json.dumps(following_data, indent=2))
        else:
            console.print(f"[bold]{username} is following:[/bold]")
            for user in following_data:
                click.echo(f"  • {user}")
            console.print(f"\n[dim]Total: {len(following_data)} users[/dim]")

    except NotFoundError:
        console.print(f"[red]Error: User '{username}' not found[/red]")
    except GitHubConnException as e:
        console.print(f"[red]Error: {e}[/red]")


@main.command()
@click.argument("username")
@click.argument("language")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def repos_by_language(
    ctx: click.Context, username: str, language: str, output_json: bool
) -> None:
    """List repositories filtered by programming language."""
    try:
        client: GitHubClient = ctx.obj["client"]
        repos_data = client.get_user_repos_by_language(username, language)

        if output_json:
            click.echo(json.dumps(repos_data, indent=2))
        else:
            table = Table(title=f"{language} Repositories - {username}")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="green")
            table.add_column("Stars", style="magenta")

            for repo in repos_data:
                table.add_row(
                    repo["name"],
                    repo.get("description") or "N/A",
                    str(repo.get("stargazers_count", 0)),
                )

            console.print(table)
            console.print(
                f"\n[dim]Found {len(repos_data)} {language} "
                f"repositories[/dim]"
            )

    except NotFoundError:
        console.print(f"[red]Error: User '{username}' not found[/red]")
    except GitHubConnException as e:
        console.print(f"[red]Error: {e}[/red]")


@main.command()
@click.option("--name", required=True, help="Repository name")
@click.option("--description", default="", help="Repository description")
@click.option("--private", is_flag=True, help="Make repository private")
@click.pass_context
def create_repo(
    ctx: click.Context, name: str, description: str, private: bool
) -> None:
    """Create a new repository (requires authentication)."""
    try:
        client: GitHubClient = ctx.obj["client"]

        if not ctx.obj.get("token"):
            console.print(
                "[red]Error: Authentication required. "
                "Set GITHUB_TOKEN or use --token[/red]"
            )
            return

        with console.status("[bold green]Creating repository..."):
            repo_data = client.create_repo(
                name, description=description, private=private
            )

        console.print("[green]✓ Repository created successfully![/green]")
        console.print(f"  Name: {repo_data['name']}")
        console.print(f"  URL: {repo_data['html_url']}")
        console.print(f"  Clone: {repo_data['clone_url']}")

    except AuthenticationError:
        console.print("[red]Error: No authentication token provided[/red]")
    except GitHubConnException as e:
        console.print(f"[red]Error: {e}[/red]")


@main.command()
def version() -> None:
    """Show version information."""
    from . import __version__
    click.echo(f"github_conn version {__version__}")


if __name__ == "__main__":
    main()
