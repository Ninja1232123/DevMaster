"""
DevMaster - Unified CLI orchestrating all developer tools.

Brings together:
- AI Debug Companion (error fixing)
- DevKnowledge (knowledge graph)
- CodeSeek (semantic search)
- DevNarrative (git storytelling)
- CodeArchaeology (code evolution)
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich import box

console = Console()

# Repository root - devmaster/devmaster/cli.py -> repo root
REPO_ROOT = Path(__file__).parent.parent.parent


@click.group()
@click.version_option(version="0.1.0")
def main():
    """
    🎯 DevMaster - Your Unified Developer Toolkit

    Orchestrates all your developer tools in one place.
    """
    pass


@main.command()
@click.option('--path', default='.', help='Repository path')
def init(path: str):
    """
    Initialize all developer tools at once.

    Sets up AI Debug Companion, DevNarrative, CodeArchaeology,
    CodeSeek, and DevKnowledge in your repository.
    """
    console.print("\n[bold cyan]Initializing DevMaster...[/bold cyan]\n")

    tools = [
        ("DevNarrative", "devnarrative init --repo"),
        ("CodeArchaeology", "codearch init --repo"),
    ]

    success_count = 0

    for tool_name, command in tools:
        try:
            console.print(f"[yellow]Setting up {tool_name}...[/yellow]")
            result = subprocess.run(
                f"{command} {path}",
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                console.print(f"  [green][OK] {tool_name} initialized[/green]")
                success_count += 1
            else:
                console.print(f"  [red][ERROR] {tool_name} failed[/red]")

        except Exception as e:
            console.print(f"  [red][ERROR] {tool_name} error: {e}[/red]")

    console.print(f"\n[bold green]✨ Initialized {success_count}/{len(tools)} tools[/bold green]")

    if success_count > 0:
        console.print("\n[cyan][INFO] Quick start:[/cyan]")
        console.print("  • devmaster status    - Check tool status")
        console.print("  • devmaster analyze   - Analyze your codebase")
        console.print("  • devmaster report    - Generate weekly report")


@main.command()
@click.option('--path', default='.', help='Repository path')
def status(path: str):
    """
    Show status dashboard of all tools.

    Displays configuration status, recent activity, and health checks.
    """
    console.print("\n[bold cyan]📊 DevMaster Status Dashboard[/bold cyan]\n")

    # Create status table
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Tool", style="cyan", width=20)
    table.add_column("Status", width=12)
    table.add_column("Info", width=50)

    # Check each tool
    tools_status = []

    # AI Debug Companion
    try:
        result = subprocess.run(["debug-companion", "--version"], capture_output=True)
        if result.returncode == 0:
            table.add_row(
                "[DEBUG] AI Debug Companion",
                "[green][OK] Ready[/green]",
                "Auto-fix errors with AI"
            )
            tools_status.append(True)
        else:
            table.add_row("[DEBUG] AI Debug Companion", "[red][ERROR] Not installed[/red]", "pip install -e ai-debug-companion")
            tools_status.append(False)
    except FileNotFoundError:
        table.add_row("[DEBUG] AI Debug Companion", "[red][ERROR] Not installed[/red]", "pip install -e ai-debug-companion")
        tools_status.append(False)

    # DevNarrative
    try:
        result = subprocess.run(["devnarrative", "--version"], capture_output=True)
        if result.returncode == 0:
            table.add_row(
                "[DOCS] DevNarrative",
                "[green][OK] Ready[/green]",
                "Git history as stories"
            )
            tools_status.append(True)
        else:
            table.add_row("[DOCS] DevNarrative", "[red][ERROR] Not installed[/red]", "pip install -e devnarrative")
            tools_status.append(False)
    except FileNotFoundError:
        table.add_row("[DOCS] DevNarrative", "[red][ERROR] Not installed[/red]", "pip install -e devnarrative")
        tools_status.append(False)

    # CodeArchaeology
    try:
        result = subprocess.run(["codearch", "--version"], capture_output=True)
        if result.returncode == 0:
            table.add_row(
                "[ARCH] CodeArchaeology",
                "[green][OK] Ready[/green]",
                "Analyze code evolution"
            )
            tools_status.append(True)
        else:
            table.add_row("[ARCH] CodeArchaeology", "[red][ERROR] Not installed[/red]", "pip install -e codearchaeology")
            tools_status.append(False)
    except FileNotFoundError:
        table.add_row("[ARCH] CodeArchaeology", "[red][ERROR] Not installed[/red]", "pip install -e codearchaeology")
        tools_status.append(False)

    # CodeSeek
    try:
        result = subprocess.run(["codeseek", "--version"], capture_output=True)
        if result.returncode == 0:
            table.add_row(
                "🔍 CodeSeek",
                "[green][OK] Ready[/green]",
                "Semantic code search"
            )
            tools_status.append(True)
        else:
            table.add_row("🔍 CodeSeek", "[yellow]⏳ Not installed[/yellow]", "pip install -e codeseek")
            tools_status.append(False)
    except FileNotFoundError:
        table.add_row("🔍 CodeSeek", "[yellow]⏳ Not installed[/yellow]", "pip install -e codeseek (heavy install)")
        tools_status.append(False)

    # DevKnowledge
    try:
        result = subprocess.run(["dk", "--version"], capture_output=True)
        if result.returncode == 0:
            table.add_row(
                "🧠 DevKnowledge",
                "[green][OK] Ready[/green]",
                "Personal knowledge graph"
            )
            tools_status.append(True)
        else:
            table.add_row("🧠 DevKnowledge", "[yellow]⏳ Not installed[/yellow]", "pip install -e devknowledge")
            tools_status.append(False)
    except FileNotFoundError:
        table.add_row("🧠 DevKnowledge", "[yellow]⏳ Not installed[/yellow]", "pip install -e devknowledge (heavy install)")
        tools_status.append(False)

    console.print(table)

    # Summary
    ready_count = sum(tools_status)
    total_count = len(tools_status)

    if ready_count == total_count:
        console.print(f"\n[bold green]🎉 All tools ready! ({ready_count}/{total_count})[/bold green]")
    elif ready_count > 0:
        console.print(f"\n[yellow]⚡ {ready_count}/{total_count} tools ready[/yellow]")
    else:
        console.print(f"\n[red][ERROR] No tools installed yet[/red]")
        console.print("\n[cyan][INFO] Run: devmaster install[/cyan]")


@main.command()
@click.option('--path', default='.', help='Repository path')
@click.option('--days', default=7, help='Number of days to analyze')
def analyze(path: str, days: int):
    """
    Comprehensive codebase analysis.

    Combines CodeArchaeology hotspots with CodeSeek exploration
    to identify technical debt and risks.
    """
    console.print(f"\n[bold cyan]🔬 Analyzing codebase...[/bold cyan]\n")

    # Run CodeArchaeology
    console.print("[yellow]Step 1: Finding code hotspots...[/yellow]")
    result = subprocess.run(
        ["codearch", "hotspots", "--repo", path],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        console.print(result.stdout)
    else:
        console.print("[red]CodeArchaeology analysis failed[/red]")

    # Run coupling analysis
    console.print("\n[yellow]Step 2: Analyzing file coupling...[/yellow]")
    result = subprocess.run(
        ["codearch", "coupling", "--repo", path],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        console.print(result.stdout)

    console.print("\n[green][OK] Analysis complete![/green]")
    console.print("\n[cyan][INFO] Next steps:[/cyan]")
    console.print("  • devmaster search <hotspot-file>  - Explore risky files")
    console.print("  • devmaster fix                     - Run with auto-fix")


@main.command()
@click.argument('query')
@click.option('--path', default='.', help='Repository path')
def search(query: str, path: str):
    """
    Unified search across code and knowledge.

    Searches both CodeSeek (for code) and DevKnowledge (for notes).
    """
    console.print(f"\n[bold cyan]🔍 Searching for: {query}[/bold cyan]\n")

    # Search code with CodeSeek
    console.print("[yellow][CODE] Code Results:[/yellow]")
    result = subprocess.run(
        ["codeseek", "find", query],
        capture_output=True,
        text=True,
        cwd=path
    )

    if result.returncode == 0:
        console.print(result.stdout or "[gray]No code results[/gray]")
    else:
        console.print("[gray]CodeSeek not available or not indexed[/gray]")

    # Search knowledge with DevKnowledge
    console.print("\n[yellow]🧠 Knowledge Results:[/yellow]")
    result = subprocess.run(
        ["dk", "search", query],
        capture_output=True,
        text=True,
        cwd=path
    )

    if result.returncode == 0:
        console.print(result.stdout or "[gray]No knowledge results[/gray]")
    else:
        console.print("[gray]DevKnowledge not available[/gray]")


@main.command()
@click.option('--path', default='.', help='Repository path')
@click.option('--format', type=click.Choice(['text', 'markdown', 'html']), default='text')
@click.option('--export', help='Export to file')
def report(path: str, format: str, export: Optional[str]):
    """
    Generate comprehensive weekly development report.

    Combines insights from DevNarrative, CodeArchaeology,
    and AI Debug Companion.
    """
    console.print("\n[bold cyan]📊 Generating Weekly Report...[/bold cyan]\n")

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("WEEKLY DEVELOPMENT REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Get narrative from DevNarrative
    console.print("[yellow]Collecting development narrative...[/yellow]")
    result = subprocess.run(
        ["devnarrative", "week", "--repo", path],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        report_lines.append("## [DOCS] This Week's Story")
        report_lines.append(result.stdout)
        report_lines.append("")

    # Get hotspots from CodeArchaeology
    console.print("[yellow]Analyzing code health...[/yellow]")
    result = subprocess.run(
        ["codearch", "stats", "--repo", path],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        report_lines.append("## [ARCH] Code Health")
        report_lines.append(result.stdout)
        report_lines.append("")

    # Combine report
    full_report = "\n".join(report_lines)

    if export:
        with open(export, 'w') as f:
            f.write(full_report)
        console.print(f"\n[green][OK] Report exported to: {export}[/green]")
    else:
        console.print(full_report)


@main.command()
@click.argument('script')
@click.option('--fix', is_flag=True, help='Apply fixes automatically')
@click.option('--auto', is_flag=True, help='Auto-apply high-confidence fixes without confirmation (requires --fix)')
def debug(script: str, fix: bool, auto: bool):
    """
    Debug a script with AI assistance.

    Runs the script with AI Debug Companion and optionally applies fixes.

    Examples:
      devmaster debug script.py                  # Just run and detect errors
      devmaster debug script.py --fix            # Detect and show fixes (with confirmation)
      devmaster debug script.py --fix --auto     # Auto-apply high-confidence fixes
    """
    console.print(f"\n[bold cyan][DEBUG] Debugging: {script}[/bold cyan]\n")

    if fix:
        cmd = ["debug-companion", "fix", "--apply", "--", "python", script]
        if auto:
            cmd.insert(3, "--auto")  # Insert --auto before --
    else:
        cmd = ["debug-companion", "exec", "--", "python", script]

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@main.command()
def install():
    """
    Install all developer tools.

    Installs AI Debug Companion, DevNarrative, CodeArchaeology,
    CodeSeek, and DevKnowledge.
    """
    console.print("\n[bold cyan]📦 Installing Developer Tools[/bold cyan]\n")

    tools = [
        ("AI Debug Companion", "ai-debug-companion", False),
        ("DevNarrative", "devnarrative", False),
        ("CodeArchaeology", "codearchaeology", False),
        ("CodeSeek", "codeseek", True),  # Heavy
        ("DevKnowledge", "devknowledge", True),  # Heavy
    ]

    for tool_name, dir_name, is_heavy in tools:
        if is_heavy:
            console.print(f"[yellow]⚠️  {tool_name} is a large install (ML dependencies)[/yellow]")
            if not click.confirm(f"Install {tool_name}?", default=False):
                console.print(f"[gray]Skipping {tool_name}[/gray]\n")
                continue

        console.print(f"[cyan]Installing {tool_name}...[/cyan]")

        # Use absolute path to find tool directory
        tool_path = REPO_ROOT / dir_name
        if not tool_path.exists():
            console.print(f"[red][ERROR] {tool_name} not found at {tool_path}[/red]\n")
            continue

        result = subprocess.run(
            f"pip install -e {tool_path}",
            shell=True,
            capture_output=True
        )

        if result.returncode == 0:
            console.print(f"[green][OK] {tool_name} installed[/green]\n")
        else:
            console.print(f"[red][ERROR] {tool_name} failed to install[/red]\n")
            if result.stderr:
                console.print(f"[red]{result.stderr.decode()}[/red]")

    console.print("[bold green]🎉 Installation complete![/bold green]")
    console.print("\n[cyan][INFO] Run: devmaster status[/cyan]")


@main.command()
def workflows():
    """
    Show available workflows.

    Workflows combine multiple tools for common tasks.
    """
    console.print("\n[bold cyan]🎯 Available Workflows[/bold cyan]\n")

    workflows = [
        ("analyze", "Find technical debt and hotspots", "CodeArchaeology + CodeSeek"),
        ("report", "Generate weekly development report", "DevNarrative + CodeArchaeology"),
        ("debug", "Debug with AI assistance", "AI Debug Companion + AI"),
        ("search", "Search code and knowledge", "CodeSeek + DevKnowledge"),
    ]

    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Tools Used", style="yellow")

    for cmd, desc, tools in workflows:
        table.add_row(f"devmaster {cmd}", desc, tools)

    console.print(table)

    console.print("\n[cyan][INFO] Examples:[/cyan]")
    console.print("  devmaster analyze                    - Analyze codebase")
    console.print("  devmaster search 'authentication'    - Search everywhere")
    console.print("  devmaster report --export report.md  - Export weekly report")
    console.print("  devmaster debug script.py --fix      - Debug with auto-fix")


@main.command()
@click.argument('license_key')
def activate(license_key: str):
    """
    Activate DevMaster Pro license.

    Get your license key from: https://devmaster.pro

    Example: devmaster activate DM-PRO-ABC123-XYZ789
    """
    from .license import get_license

    console.print("\n[cyan]🔑 Activating DevMaster Pro...[/cyan]\n")

    license = get_license()

    if license.activate(license_key):
        info = license.get_info()
        console.print("[bold green][OK] License activated successfully![/bold green]\n")
        console.print(f"[cyan]Tier:[/cyan] {info['tier'].upper()}")
        console.print(f"[cyan]Status:[/cyan] {info['status']}")
        console.print("\n[cyan]Unlocked Features:[/cyan]")
        for feature in info['features']:
            console.print(f"  {feature}")
        console.print("\n[green]🎉 You now have access to Pro features![/green]")
    else:
        console.print("[bold red][ERROR] Invalid license key[/bold red]\n")
        console.print("Please check your license key and try again.")
        console.print("\nLicense key format: DM-PRO-ABC123-XYZ789")
        console.print("Get your key at: https://devmaster.pro")
        sys.exit(1)


@main.command()
def deactivate():
    """Deactivate current license."""
    from .license import get_license

    license = get_license()

    if not license.is_active():
        console.print("[yellow]No active license to deactivate[/yellow]")
        return

    license.deactivate()
    console.print("[green][OK] License deactivated[/green]")


@main.command()
def license():
    """Show current license information."""
    from .license import get_license

    lic = get_license()
    info = lic.get_info()

    console.print("\n[bold cyan]📋 DevMaster License Information[/bold cyan]\n")

    # Create info table
    table = Table(show_header=False, box=box.ROUNDED)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Tier", info['tier'].upper())
    table.add_row("Status", "[OK] Active" if info['status'] == 'active' else "[ERROR] Inactive")

    if info.get('activated'):
        table.add_row("Activated", info['activated'][:10])

    console.print(table)

    console.print("\n[cyan]Available Features:[/cyan]")
    for feature in info['features']:
        console.print(f"  {feature}")

    if info['tier'] == 'free':
        console.print("\n[yellow][INFO] Upgrade to Pro for AI-powered features:[/yellow]")
        console.print("  • Auto-fix errors with AI")
        console.print("  • Cloud AI providers (Claude, GPT-4)")
        console.print("  • Advanced visualizations")
        console.print("  • Priority support")
        console.print("\n[cyan]Get Pro: https://devmaster.pro[/cyan]")


@main.command()
def upgrade():
    """Show upgrade options and pricing."""
    console.print("\n[bold cyan]💎 DevMaster Pro - Upgrade Options[/bold cyan]\n")

    # Pricing table
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Plan", style="cyan", width=15)
    table.add_column("Price", style="white", width=15)
    table.add_column("Features", style="white", width=50)

    table.add_row(
        "Free",
        "$0",
        "Local AI (Ollama), Basic tools, Community support"
    )

    table.add_row(
        "Pro",
        "$29/mo\n$249/year",
        "AI auto-fix, Cloud AI, Advanced viz, Code explanations, Priority support"
    )

    table.add_row(
        "Team",
        "$149/mo",
        "Everything in Pro + Team dashboard, Shared knowledge, Team analytics"
    )

    console.print(table)

    console.print("\n[yellow]🎁 Limited Time: Lifetime Access for $199[/yellow]")
    console.print("   First 100 customers only!")
    console.print("\n[cyan]Get started: https://devmaster.pro[/cyan]")


# ============================================================================
# PERSISTENT CODING COMPANION - Learning & Coaching Commands
# ============================================================================

@main.group()
def learn():
    """
    Persistent Coding Companion - Learn your style and help you improve.

    The companion that lives in your environment, learns how you code,
    and helps you become a better developer.
    """
    pass


@learn.command('start')
@click.option('--path', default='.', help='Repository path to learn from')
@click.option('--days', default=30, help='Days of history to analyze')
def learn_start(path: str, days: int):
    """
    Start learning from your codebase.

    Analyzes your code patterns, naming conventions, structure preferences,
    and common issues to build a profile of your coding style.
    """
    from .learner import CodingLearner

    console.print("\n[bold cyan]🧠 Starting Learning Session...[/bold cyan]\n")
    console.print(f"[dim]Repository: {path}[/dim]")
    console.print(f"[dim]Analyzing {days} days of history[/dim]\n")

    with CodingLearner() as learner:
        try:
            results = learner.learn_from_repo(path, days)

            console.print("[bold green]✨ Learning Complete![/bold green]\n")

            # Results table
            table = Table(show_header=False, box=box.ROUNDED)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Files Analyzed", str(results['files_analyzed']))
            table.add_row("Patterns Found", str(results['patterns_found']))
            table.add_row("Insights Generated", str(results['insights_generated']))
            table.add_row("Preferences Learned", str(results['preferences_learned']))

            console.print(table)

            console.print("\n[cyan]Next steps:[/cyan]")
            console.print("  • devmaster learn insights  - See what I learned")
            console.print("  • devmaster learn profile   - View your coding profile")
            console.print("  • devmaster learn improve   - Get improvement suggestions")

        except FileNotFoundError as e:
            console.print(f"[red]Error: {e}[/red]")


@learn.command('insights')
@click.option('--category', type=click.Choice(['strength', 'weakness', 'habit', 'preference']), help='Filter by category')
@click.option('--limit', default=10, help='Maximum insights to show')
def learn_insights(category: Optional[str], limit: int):
    """
    Show insights about your coding style.

    Displays patterns, habits, strengths, and areas for improvement
    that have been learned from your code.
    """
    from .learner import CodingLearner

    console.print("\n[bold cyan]💡 Your Coding Insights[/bold cyan]\n")

    with CodingLearner() as learner:
        insights = learner.get_insights(category, limit)

        if not insights:
            console.print("[yellow]No insights yet. Run 'devmaster learn start' first.[/yellow]")
            return

        for insight in insights:
            # Color based on category
            if insight.category == 'strength':
                icon = "💪"
                color = "green"
            elif insight.category == 'weakness':
                icon = "🎯"
                color = "yellow"
            elif insight.category == 'preference':
                icon = "⚙️"
                color = "blue"
            else:
                icon = "📝"
                color = "white"

            panel = Panel(
                f"[{color}]{insight.description}[/{color}]" +
                (f"\n\n[dim]💡 {insight.suggestion}[/dim]" if insight.suggestion else ""),
                title=f"{icon} {insight.title}",
                border_style=color
            )
            console.print(panel)
            console.print()


@learn.command('profile')
def learn_profile():
    """
    View your complete coding profile.

    Shows a summary of your coding style including:
    - Detected patterns and preferences
    - Strengths and areas for improvement
    - Common errors you make
    """
    from .learner import CodingLearner
    from .coach import CodingCoach

    console.print("\n[bold cyan]👤 Your Coding Profile[/bold cyan]\n")

    with CodingLearner() as learner:
        coach = CodingCoach(learner)

        profile = learner.get_coding_profile()
        style = coach.get_coding_style_summary()
        skills = coach.get_skill_radar()

        # Style Summary
        console.print("[bold]Coding Style[/bold]")
        console.print(f"  Paradigm: {style['primary_paradigm']}")
        console.print(f"  Naming: {style['naming_convention']}")

        if style['style_traits']:
            console.print(f"  Traits: {', '.join(style['style_traits'])}")

        console.print()

        # Skill Radar
        console.print("[bold]Skill Levels[/bold]")
        for skill, score in skills.items():
            bar_length = score // 5
            bar = "█" * bar_length + "░" * (20 - bar_length)
            color = "green" if score >= 70 else "yellow" if score >= 50 else "red"
            console.print(f"  {skill.replace('_', ' ').title():20} [{color}]{bar}[/{color}] {score}%")

        console.print()

        # Strengths
        if profile.get('strengths'):
            console.print("[bold green]💪 Strengths[/bold green]")
            for s in profile['strengths']:
                console.print(f"  • {s.get('name', '').replace('_', ' ')}: {s.get('description', '')}")
            console.print()

        # Areas to Improve
        if profile.get('areas_to_improve'):
            console.print("[bold yellow]🎯 Areas to Improve[/bold yellow]")
            for a in profile['areas_to_improve']:
                console.print(f"  • {a.get('name', '').replace('_', ' ')}: {a.get('description', '')}")
            console.print()

        # Common Errors
        if profile.get('common_errors'):
            console.print("[bold red]⚠️ Common Errors[/bold red]")
            for e in profile['common_errors'][:5]:
                console.print(f"  • {e['error_type']}: {e['count']} occurrences")


@learn.command('improve')
def learn_improve():
    """
    Get personalized improvement suggestions.

    Based on your detected patterns, provides actionable goals
    and tips to improve your code quality.
    """
    from .learner import CodingLearner
    from .coach import CodingCoach

    console.print("\n[bold cyan]📈 Your Improvement Plan[/bold cyan]\n")

    with CodingLearner() as learner:
        coach = CodingCoach(learner)

        # Daily tip
        tip = coach.get_daily_tip()
        tip_color = "green" if tip['type'] == 'recognition' else "yellow"

        panel = Panel(
            f"[{tip_color}]{tip['tip']}[/{tip_color}]" +
            (f"\n\n[dim]Reason: {tip['reason']}[/dim]" if tip.get('reason') else ""),
            title=f"✨ {tip['title']}",
            border_style=tip_color
        )
        console.print(panel)
        console.print()

        # Improvement goals
        goals = coach.get_improvement_goals()

        if goals:
            console.print("[bold]🎯 Improvement Goals[/bold]\n")

            for goal in goals:
                status_icon = "🟡" if goal.current_status == 'in_progress' else "⚪"
                progress_bar = "█" * (goal.progress_percent // 10) + "░" * (10 - goal.progress_percent // 10)

                console.print(f"{status_icon} [bold]{goal.title}[/bold]")
                console.print(f"   {goal.description}")
                console.print(f"   Progress: [{progress_bar}] {goal.progress_percent}%")

                if goal.tips:
                    console.print(f"   [dim]💡 Tip: {goal.tips[0]}[/dim]")

                console.print()

        # Encouragement
        encouragement = coach.get_encouragement()
        console.print(f"\n[italic cyan]🌟 {encouragement}[/italic cyan]")


@learn.command('progress')
@click.option('--metric', default='commits_per_period', help='Metric to track')
def learn_progress(metric: str):
    """
    Track your coding progress over time.

    Shows metrics like commits, lines changed, and coding patterns
    over recent periods.
    """
    from .learner import CodingLearner
    from .coach import CodingCoach

    console.print("\n[bold cyan]📊 Your Progress[/bold cyan]\n")

    with CodingLearner() as learner:
        coach = CodingCoach(learner)

        # Progress report
        report = coach.get_progress_report()

        table = Table(show_header=False, box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Strengths Detected", str(report.strengths_count))
        table.add_row("Insights Generated", str(report.improvements_made))
        table.add_row("Areas to Work On", str(report.areas_to_work_on))
        table.add_row("Coding Sessions", str(report.coding_streak))

        console.print(table)

        console.print(f"\n[bold green]📣 {report.highlight}[/bold green]")
        console.print(f"[yellow]👉 {report.next_focus}[/yellow]")

        # Metric history
        console.print(f"\n[bold]Recent {metric.replace('_', ' ')}:[/bold]")
        progress = learner.get_progress(metric, 5)

        if progress:
            for value, recorded_at in progress[:5]:
                console.print(f"  • {recorded_at[:10]}: {value:.0f}")
        else:
            console.print("  [dim]No data yet. Keep coding![/dim]")


@learn.command('tip')
def learn_tip():
    """
    Get your daily personalized coding tip.

    A quick tip based on what the companion has learned about your coding style.
    """
    from .learner import CodingLearner
    from .coach import CodingCoach

    with CodingLearner() as learner:
        coach = CodingCoach(learner)
        tip = coach.get_daily_tip()

        tip_color = "green" if tip['type'] == 'recognition' else "yellow" if tip['type'] == 'improvement' else "cyan"

        console.print()
        panel = Panel(
            f"[{tip_color}]{tip['tip']}[/{tip_color}]",
            title=f"✨ {tip['title']}",
            border_style=tip_color,
            padding=(1, 2)
        )
        console.print(panel)


# ============================================================================
# NERVOUS SYSTEM - Cross-Tool Integration Commands
# ============================================================================

@main.group()
def nerve():
    """
    The Nervous System - Cross-tool integration hub.

    Monitor event flow between tools, view integrations,
    and see how the ecosystem communicates.
    """
    pass


@nerve.command('status')
def nerve_status():
    """
    Show nervous system status and recent activity.

    Displays event flow, active integrations, and system health.
    """
    from .nervous_system import NervousSystem

    console.print("\n[bold cyan]🧠 Nervous System Status[/bold cyan]\n")

    ns = NervousSystem()

    # Get recent events
    events = ns.get_recent_events(limit=10)
    integrations = ns.get_integration_stats()

    # Event count
    console.print(f"[bold]Recent Events:[/bold] {len(events)}")

    if events:
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("Time", style="dim")
        table.add_column("Source", style="cyan")
        table.add_column("Event", style="green")
        table.add_column("Details", style="white")

        for event in events[:10]:
            time_str = event.timestamp[11:19] if event.timestamp else "?"
            details = str(event.payload)[:40] + "..." if len(str(event.payload)) > 40 else str(event.payload)
            table.add_row(
                time_str,
                event.source_tool,
                event.event_type,
                details
            )

        console.print(table)
    else:
        console.print("[dim]No events yet. Tools will publish events as they work.[/dim]")

    # Integration stats
    console.print(f"\n[bold]Active Integrations:[/bold] {len([i for i in integrations if i['enabled']])}")

    active = [i for i in integrations if i['trigger_count'] > 0]
    if active:
        console.print("\n[bold]Most Active:[/bold]")
        for i in active[:5]:
            console.print(f"  • {i['source_event']} → {i['target_tool']}: {i['trigger_count']} triggers")


@nerve.command('flow')
@click.option('--hours', default=24, help='Hours to analyze')
def nerve_flow(hours: int):
    """
    Show event flow between tools.

    Visualizes how events flow through the ecosystem.
    """
    from .nervous_system import NervousSystem

    console.print(f"\n[bold cyan]🔄 Event Flow (Last {hours}h)[/bold cyan]\n")

    ns = NervousSystem()
    flow = ns.get_event_flow(hours)

    if not flow:
        console.print("[dim]No events in this period.[/dim]")
        return

    for source, events in flow.items():
        console.print(f"[bold green]{source}[/bold green]")
        for event_type, count in events.items():
            bar = "█" * min(count, 20)
            console.print(f"  └─ {event_type}: {bar} ({count})")
        console.print()


@nerve.command('integrations')
def nerve_integrations():
    """
    List all registered integrations.

    Shows how tools are wired together.
    """
    from .nervous_system import NervousSystem

    console.print("\n[bold cyan]🔗 Tool Integrations[/bold cyan]\n")

    ns = NervousSystem()
    integrations = ns.get_integration_stats()

    table = Table(show_header=True, box=box.ROUNDED)
    table.add_column("Event", style="yellow")
    table.add_column("→", style="dim")
    table.add_column("Target", style="cyan")
    table.add_column("Action", style="green")
    table.add_column("Triggers", style="white")
    table.add_column("Status", style="white")

    for i in integrations:
        status = "[green]●[/green]" if i['enabled'] else "[red]○[/red]"
        table.add_row(
            i['source_event'],
            "→",
            i['target_tool'],
            i['action'],
            str(i['trigger_count']),
            status
        )

    console.print(table)

    console.print("\n[dim]These integrations fire automatically when events occur.[/dim]")


@nerve.command('test')
@click.argument('event_type', default='hotspot_detected')
def nerve_test(event_type: str):
    """
    Send a test event through the nervous system.

    Useful for verifying integrations are working.
    """
    from .nervous_system import NervousSystem, Event

    console.print(f"\n[bold cyan]🧪 Testing Event: {event_type}[/bold cyan]\n")

    ns = NervousSystem()

    # Create test event based on type
    test_payloads = {
        'hotspot_detected': {'file_path': 'test/example.py', 'churn_rate': 10, 'change_count': 50},
        'error_pattern_learned': {'error_type': 'KeyError', 'pattern': "data\\['key'\\]", 'frequency': 5},
        'fix_applied': {'error_type': 'KeyError', 'file_path': 'test.py', 'fix_applied': "data.get('key')"},
        'code_indexed': {'repo_path': '.', 'files_indexed': 100, 'symbols_found': 500},
    }

    payload = test_payloads.get(event_type, {'test': True})

    event = Event(
        event_type=event_type,
        source_tool='test_cli',
        payload=payload
    )

    event_id = ns.publish(event)
    console.print(f"[green]✓[/green] Event published with ID: {event_id}")
    console.print(f"[dim]Payload: {payload}[/dim]")


@nerve.command('watch')
def nerve_watch():
    """
    Show the current watchlist (files flagged by integrations).

    Files here get extra attention from the debugger.
    """
    from pathlib import Path
    import json

    console.print("\n[bold cyan]👁️ Watchlist[/bold cyan]\n")

    watchlist_path = Path("~/.devmaster/watchlist.json").expanduser()

    if not watchlist_path.exists():
        console.print("[dim]Watchlist is empty. CodeArchaeology will populate it.[/dim]")
        return

    try:
        watchlist = json.loads(watchlist_path.read_text())
    except:
        console.print("[red]Error reading watchlist[/red]")
        return

    if not watchlist:
        console.print("[dim]Watchlist is empty.[/dim]")
        return

    table = Table(show_header=True, box=box.ROUNDED)
    table.add_column("File", style="cyan")
    table.add_column("Churn Rate", style="yellow")
    table.add_column("Source", style="dim")
    table.add_column("Added", style="dim")

    for item in sorted(watchlist, key=lambda x: x.get('churn_rate', 0), reverse=True):
        table.add_row(
            item.get('file', '?'),
            str(item.get('churn_rate', '?')),
            item.get('source', '?'),
            item.get('added', '?')[:10] if item.get('added') else '?'
        )

    console.print(table)


@nerve.command('suggestions')
def nerve_suggestions():
    """
    Show pattern suggestions from the learner.

    These are error patterns that could be added to the debugger.
    """
    from pathlib import Path
    import json

    console.print("\n[bold cyan]💡 Pattern Suggestions[/bold cyan]\n")

    suggestions_path = Path("~/.devmaster/pattern_suggestions.json").expanduser()

    if not suggestions_path.exists():
        console.print("[dim]No suggestions yet. The learner will generate them.[/dim]")
        return

    try:
        suggestions = json.loads(suggestions_path.read_text())
    except:
        console.print("[red]Error reading suggestions[/red]")
        return

    if not suggestions:
        console.print("[dim]No suggestions yet.[/dim]")
        return

    for s in suggestions[-10:]:
        panel = Panel(
            f"[yellow]Pattern:[/yellow] {s.get('pattern', '?')}\n"
            f"[green]Fix:[/green] {s.get('fix_suggestion', '?')}\n"
            f"[dim]Seen {s.get('frequency', '?')} times[/dim]",
            title=f"🎯 {s.get('error_type', 'Unknown Error')}",
            border_style="yellow"
        )
        console.print(panel)
        console.print()


if __name__ == '__main__':
    main()
