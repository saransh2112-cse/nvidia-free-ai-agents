import os
import asyncio
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Rich imports for a beautiful CLI
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.text import Text

load_dotenv()
console = Console()

api_key = os.getenv("NVIDIA_API_KEY")
if not api_key or api_key == "your_api_key_here":
    console.print(Panel("[bold red]Please set your NVIDIA_API_KEY in the .env file[/bold red]", title="Error"))
    exit(1)

client = AsyncOpenAI(
  base_url="https://integrate.api.nvidia.com/v1",
  api_key=api_key
)

# Planner model: Fast and cheap 
PLANNER_MODEL = "meta/llama-3.1-8b-instruct"
# Writer model: Switched to Llama 3.1 8B to make the entire swarm blazing fast
WRITER_MODEL = "meta/llama-3.1-8b-instruct"

async def generate_outline(topic):
    prompt = f"""
    You are an expert technical planner. 
    Topic: {topic}
    Generate a JSON array of 3 distinct sub-topics that need to be covered to explain this topic comprehensively.
    Return ONLY a valid JSON array of strings, without any markdown formatting, backticks, or extra text.
    Example: ["Introduction to X", "Core Concepts", "Real-world Applications"]
    """
    
    response = await client.chat.completions.create(
        model=PLANNER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.3
    )
    
    content = response.choices[0].message.content.strip()
    try:
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
        
        outline = json.loads(content)
        return outline
    except Exception as e:
        # Fallback outline
        return ["Introduction", "Key Architectural Components", "Future Implications"]

async def write_section(topic, section_title, progress, task_id):
    prompt = f"""
    You are an expert technical writer creating a section for a comprehensive guide on "{topic}".
    Write the section titled "{section_title}".
    Provide detailed, professional, and engaging content. Use markdown formatting.
    Do not write the overall introduction or conclusion, just focus purely on this specific section.
    Limit the response to 3-4 paragraphs.
    """
    
    try:
        response = await client.chat.completions.create(
            model=WRITER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        # Complete the progress task
        progress.update(task_id, advance=1, description=f"[bold green]✔ Finished: {section_title}[/bold green]")
        return f"## {section_title}\n\n{response.choices[0].message.content}\n\n"
    except Exception as e:
        progress.update(task_id, advance=1, description=f"[bold red]✖ Error: {section_title}[/bold red]")
        return f"## {section_title}\n\nError generating content: {e}\n\n"

async def main():
    topic = "The Future of Autonomous Multi-Agent Systems"
    
    console.print(Panel(f"[bold cyan]Target Topic:[/bold cyan] {topic}", 
                        title="[bold yellow]🐝 Asynchronous Research Swarm Init[/bold yellow]", 
                        expand=False))
    
    # Step 1: Generate Outline
    with console.status(f"[bold magenta]Planner Agent ({PLANNER_MODEL}) is generating the architecture...[/bold magenta]", spinner="dots4"):
        outline = await generate_outline(topic)
    
    console.print(f"[bold green]✔ Outline Generated Successfully![/bold green]")
    for i, section in enumerate(outline, 1):
        console.print(f"   [cyan]{i}.[/cyan] {section}")
    print("\n")
    
    console.print(f"[bold yellow]🚀 Deploying Swarm Agents ({WRITER_MODEL}) in Parallel...[/bold yellow]\n")
    
    # Step 2: Write Sections concurrently with rich Progress
    sections = []
    with Progress(
        SpinnerColumn(spinner_name="earth"),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False
    ) as progress:
        
        # Create a progress task for each section
        tasks = []
        for section in outline:
            task_id = progress.add_task(f"[blue]Agent researching: {section}[/blue]", total=1)
            tasks.append(write_section(topic, section, progress, task_id))
            
        sections = await asyncio.gather(*tasks)
    
    # Step 3: Compile Report
    print("\n")
    with console.status("[bold magenta]Compiling final Markdown report...[/bold magenta]"):
        report = f"# Comprehensive Guide: {topic}\n\n"
        for section in sections:
            report += section
            
        output_file = "Research_Report.md"
        with open(output_file, "w") as f:
            f.write(report)
            
    console.print(Panel(f"[bold green]🎉 Swarm execution complete![/bold green]\n\n"
                        f"Report successfully saved to [bold white]'{output_file}'[/bold white].\n"
                        f"Total concurrent tasks processed: [bold cyan]{len(outline)}[/bold cyan]", 
                        title="[bold yellow]Success[/bold yellow]", 
                        expand=False))

if __name__ == "__main__":
    asyncio.run(main())
