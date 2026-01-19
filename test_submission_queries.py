
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
        if "final_outputs" in summary and summary["final_outputs"]:
            return str(summary["final_outputs"])
        else:
            summarizer_node = next((n for n in context.plan_graph.nodes if context.plan_graph.nodes[n].get("agent") == "SummarizerAgent"), None)
            if summarizer_node:
                return str(context.plan_graph.nodes[summarizer_node].get("output"))
    return "No output produced."

async def main():
    console = Console()
    console.print(Panel.fit("[bold cyan]S16 Submission Test - Running Two Queries[/bold cyan]", border_style="blue"))
    
    multi_mcp = MultiMCP()
    await multi_mcp.start()

    try:
        agent_loop = AgentLoop4(multi_mcp=multi_mcp)
        
        # Query 1: Web search query about Dhurandhar Movie revenue
        query1 = "What's the latest revenue of Dhurandhar Movie"
        console.print(Panel.fit("[bold green]QUERY 1: Web Search Query[/bold green]", border_style="green"))
        result1 = await run_query(agent_loop, query1, console)
        console.print(Panel(result1, title="Query 1 Result", border_style="green"))
        
        console.print("\n" + "="*80 + "\n")
        
        # Query 2: RAG-based query (using documents in the system)
        query2 = "What are the key highlights from the DLF BRSR report?"
        console.print(Panel.fit("[bold yellow]QUERY 2: RAG-Based Query[/bold yellow]", border_style="yellow"))
        result2 = await run_query(agent_loop, query2, console)
        console.print(Panel(result2, title="Query 2 Result", border_style="yellow"))
        
        console.print("\n[bold green]✅ Both queries completed successfully![/bold green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
    finally:
        await multi_mcp.stop()

if __name__ == "__main__":
    asyncio.run(main())
