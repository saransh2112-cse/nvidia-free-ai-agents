import os
import sys
import json
import asyncio
from openai import AsyncOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

if not api_key:
    print("Error: NVIDIA_API_KEY not found in environment.")
    sys.exit(1)

client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

MODEL = "meta/llama-3.1-70b-instruct"
console = Console()

# Define the expected JSON schema via Pydantic
class InvoiceExtraction(BaseModel):
    vendor_name: str = Field(description="Name of the company sending the invoice")
    invoice_number: str = Field(description="Unique invoice identifier")
    total_amount: float = Field(description="Total amount due")
    currency: str = Field(description="Currency code like USD, EUR")
    items: list[str] = Field(description="List of items or services purchased")

schema_json = InvoiceExtraction.model_json_schema()

async def extract_data(file_path: str):
    if not os.path.exists(file_path):
        console.print(f"[red]Error:[/red] File {file_path} not found.")
        sys.exit(1)
        
    with open(file_path, "r") as f:
        text = f.read()
        
    console.print(f"[yellow]Reading file '{file_path}' ({len(text)} characters)[/yellow]")
    console.print("[cyan]Extracting structured data using NVIDIA API...[/cyan]")
    
    system_prompt = f"""You are an expert data extraction agent.
Your task is to extract information from the following text and return it as a pure JSON object.
Do NOT wrap the JSON in markdown blocks (no ```json ... ```).
Just return the raw JSON matching this schema:
{json.dumps(schema_json, indent=2)}
"""

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.1, # Low temperature for more deterministic extraction
            max_tokens=1024
        )
        
        raw_output = response.choices[0].message.content.strip()
        
        # Clean up in case the model returns markdown anyway
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]
            
        parsed_data = json.loads(raw_output.strip())
        
        # Display the result beautifully using Rich
        json_str = json.dumps(parsed_data, indent=4)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        console.print(Panel(syntax, title="[bold green]Extracted Data[/bold green]", expand=False))
        
        # Save output to a file
        output_file = file_path + ".extracted.json"
        with open(output_file, "w") as f:
            json.dump(parsed_data, f, indent=4)
        console.print(f"[green]Data successfully saved to {output_file}[/green]")
        
    except json.JSONDecodeError:
        console.print("[red]Failed to parse output as JSON. Raw output:[/red]")
        console.print(raw_output)
    except Exception as e:
        console.print(f"[red]Error during extraction:[/red] {str(e)}")

def main():
    if len(sys.argv) < 2:
        console.print("Usage: python cli.py <path_to_text_file>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    asyncio.run(extract_data(file_path))

if __name__ == "__main__":
    main()
