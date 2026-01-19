
import asyncio
import sys
import os
from rich.console import Console
from rich.panel import Panel

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.loop import AgentLoop4
from mcp_servers.multi_mcp import MultiMCP

async def run_query(agent_loop, query, console):
    """Helper to run a query and get text output"""
    console.print(f"\n[bold cyan]Running Query:[/bold cyan] {query}\n")
    
    context = await agent_loop.run(
        query=query,
        file_manifest=[],
        globals_schema={},
        uploaded_files=[]
    )
    
    if context:
        summary = context.get_execution_summary()
        console.print("\n[bold]Execution Summary:[/bold]")
        console.print(f"  Total Steps: {summary.get('total_steps', 0)}")
        console.print(f"  Completed: {summary.get('completed_steps', 0)}")
        console.print(f"  Failed: {summary.get('failed_steps', 0)}")
        
        if "final_outputs" in summary and summary["final_outputs"]:
            return str(summary["final_outputs"])
        else:
            summarizer_node = next((n for n in context.plan_graph.nodes if context.plan_graph.nodes[n].get("agent") == "SummarizerAgent"), None)
            if summarizer_node:
                return str(context.plan_graph.nodes[summarizer_node].get("output"))
    return "No output produced."

async def main():
    console = Console()
    console.print(Panel.fit("[bold cyan]Query 1: Dhurandhar Movie Revenue[/bold cyan]", border_style="blue"))
    
    multi_mcp = MultiMCP()
    await multi_mcp.start()

    try:
        agent_loop = AgentLoop4(multi_mcp=multi_mcp)
        
        # Query 1: Web search query about Dhurandhar Movie revenue
        query1 = "What's the latest revenue of Dhurandhar Movie"
        result1 = await run_query(agent_loop, query1, console)
        console.print(Panel(result1, title="Query 1 Result - Dhurandhar Movie Revenue", border_style="green"))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
    finally:
        await multi_mcp.stop()

if __name__ == "__main__":
    asyncio.run(main())
