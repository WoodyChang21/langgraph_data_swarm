import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Annotated, Optional
from dotenv import load_dotenv

from langchain_core.tools import tool, InjectedToolArg
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

from agents.llm_model import LLM
from agents.plot_agent.s3_html_utils import s3_uploader

load_dotenv()

# Plot output path
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PLOT_PATH = os.path.join(BASE_PATH, "plots")

class PlotAgent:
    def __init__(self):
        self.llm = LLM
        self.plot_dir = PLOT_PATH
        os.makedirs(self.plot_dir, exist_ok=True)

    def _get_system_prompt(self):
        return """You are a data visualization expert. Your role is to:
        1. Read CSV data from provided file paths or S3 URLs
        2. Analyze the data structure and recommend appropriate visualizations
        3. Create clear, informative plots using matplotlib or plotly
        4. Save plots to files and provide file paths

        When a user provides a CSV file path or S3 URL, you should:
        - Use the 'read_csv_data' tool to load the data
        - Use the 'create_plot' tool to generate visualizations
        - Suggest multiple visualization options when appropriate

        Always consider the data types and relationships when choosing plot types.
        
        Format the S3 URL as web embedding iframe. The ```html ``` code block should be used for markdown rendering.
        """

    def _format_plot_response(self, s3_url: str, plot_title: str) -> str:
        """Format the plot response for different frontends"""
        # Format with proper HTML code block for markdown rendering
        response = f"""✅ Plot created successfully: {plot_title}

**Interactive Visualization:**

```html
<iframe
  src="{s3_url}"
  width="100%"
  height="600px"
  frameborder="0">
</iframe>
```

**Direct Link:** {s3_url}
"""
        return response
    
    def _clean_plot_files(self, user_id: str):
        """Clean up old plot files, keeping only the last 10"""
        try:
            plot_dir = os.path.join(self.plot_dir, user_id)
            
            # Check if directory exists
            if not os.path.exists(plot_dir):
                return
            
            plot_files = [
                f for f in os.listdir(plot_dir)
                if f.startswith("plot_") and (f.endswith(".png") or f.endswith(".html"))
            ]
            plot_files.sort(reverse=True)
            
            # Delete old files, keeping only the 10 most recent
            for old_file in plot_files[10:]:
                try:
                    os.remove(os.path.join(plot_dir, old_file))
                except Exception as e:
                    # Log error but don't fail the whole operation
                    print(f"Warning: Could not delete old plot file {old_file}: {e}")
        except Exception as e:
            # Don't fail if cleanup fails
            print(f"Warning: Plot cleanup failed: {e}")

# ==================================== Tools ==============================================
    
    def _get_read_csv_tool(self):
        """Tool to read CSV data from file path or S3 URL"""
        
        @tool
        def read_csv_data(
            csv_path: Annotated[str, "File path or S3 URL to the CSV file"]
        ) -> str:
            """Read and analyze CSV data from a file path or S3 URL.
            
            Use this tool FIRST before creating plots to understand the data structure.
            
            Args:
                csv_path: Full file path (e.g., 'agents/sql_search_agent/csv/user123/data_20250104.csv') 
                         or S3 URL (e.g., 'https://s3.amazonaws.com/bucket/data.csv')
            
            Returns:
                Data summary including:
                - Number of rows and columns
                - Column names and their data types
                - Preview of first 5 rows
                - CSV path for use in create_plot
            
            Always use this tool to inspect data before calling create_plot.
            """
            try:
                # Check if it's an S3 URL
                if csv_path.startswith("http://") or csv_path.startswith("https://"):
                    df = pd.read_csv(csv_path)
                else:
                    df = pd.read_csv(csv_path)
                
                if df.empty:
                    return "The CSV file is empty."
                
                # Create a summary of the data
                summary = []
                summary.append(f"Data loaded successfully!")
                summary.append(f"Number of rows: {len(df)}")
                summary.append(f"Number of columns: {len(df.columns)}")
                summary.append(f"\nColumns and types:")
                for col in df.columns:
                    summary.append(f"  - {col}: {df[col].dtype}")
                
                summary.append(f"\nFirst 5 rows:")
                summary.append(df.head(5).to_string())
                
                # Store the dataframe path for plotting
                return "\n".join(summary) + f"\n\nCSV path for plotting: {csv_path}"
                
            except Exception as e:
                return f"Error reading CSV: {str(e)}"
        
        return read_csv_data

    def _get_plot_tool(self):
        """Tool to create various types of plots"""
        
        @tool
        def create_plot(
            csv_path: Annotated[str, "File path or S3 URL to the CSV file"],
            plot_type: Annotated[str, "Type of plot: 'bar', 'line', 'scatter', 'pie', 'histogram', or 'box'"],
            config: Annotated[RunnableConfig, InjectedToolArg],
            x_column: Annotated[Optional[str], "Column name for x-axis"] = None,
            y_column: Annotated[Optional[str], "Column name for y-axis"] = None,
            title: Annotated[Optional[str], "Plot title (auto-generated if not provided)"] = None,
            group_by: Annotated[Optional[str], "Column to group by for aggregations"] = None,
        ) -> str:
            """Create an interactive visualization plot from CSV data.
            
            IMPORTANT: Always call read_csv_data FIRST to understand the data structure.
            
            Args:
                csv_path: Same path received from SQL Agent or read_csv_data output
                plot_type: Choose ONE: 'bar', 'line', 'scatter', 'pie', 'histogram', 'box'
                x_column: Column name for x-axis (required for most plots)
                y_column: Column name for y-axis (required for most plots)
                title: Custom plot title (optional, will auto-generate if not provided)
                group_by: Column to group/aggregate data by (optional, use for bar/pie charts)
            
            Plot type guidelines:
                - 'bar': Show counts or values by category (use group_by to aggregate)
                - 'line': Show trends over time (needs x and y columns)
                - 'scatter': Show relationship between two variables (needs x and y)
                - 'pie': Show proportions (use group_by and y_column)
                - 'histogram': Show distribution of one variable (needs x_column only)
                - 'box': Show statistical distribution (needs x and y columns)
            
            Returns:
                Success message with ```html ``` code block with an iframe element.
                Example: "Plot created successfully! Saved to: /path/to/plot_20250104_120000.html (Size: 847,234 bytes)"
            
            The generated plot is an interactive HTML file that can be opened in a browser.
            """
            try:
                # Extract user_id from config's thread_id
                user_id = config.get("configurable", {}).get("thread_id", "default") if config else "default"
                
                # Validate csv_path
                if not csv_path:
                    return "Error: csv_path is required"
                
                # Check if URL is valid S3 URL ending with .csv. If not, ask SQL Agent to export the data to CSV file first.
                if not (csv_path.endswith('.csv') and csv_path.startswith('https://')):
                    return f"Error: Invalid file path. Must be a S3 URL ending with .csv, got: {csv_path}. Ask SQL Agent to export the data to CSV file first."
                
                # Read the data (pandas handles both URLs and local paths)
                df = pd.read_csv(csv_path)
                
                if df.empty:
                    return "Cannot create plot: CSV file is empty. Ask SQL Agent to export the data to CSV file first."
                
                # Generate timestamp for unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]  # Include milliseconds (YYYYMMDD_HHMMSS_mmm)
                plot_dir = os.path.join(self.plot_dir, user_id)
                
                # Ensure directory exists with proper permissions
                try:
                    os.makedirs(plot_dir, exist_ok=True)
                except Exception as e:
                    return f"Error creating plot directory: {str(e)}"
                
                # Set default title if not provided
                if not title:
                    title = f"{plot_type.capitalize()} Plot"
                
                # Create plots based on type
                if plot_type.lower() == "bar":
                    if group_by:
                        # Aggregate data if group_by is specified
                        df_grouped = df.groupby(group_by)[y_column].sum().reset_index()
                        fig = px.bar(df_grouped, x=group_by, y=y_column, title=title)
                    else:
                        fig = px.bar(df, x=x_column, y=y_column, title=title)
                    
                elif plot_type.lower() == "line":
                    fig = px.line(df, x=x_column, y=y_column, title=title)
                    
                elif plot_type.lower() == "scatter":
                    fig = px.scatter(df, x=x_column, y=y_column, title=title)
                    
                elif plot_type.lower() == "pie":
                    if group_by:
                        df_grouped = df.groupby(group_by)[y_column].sum().reset_index()
                        fig = px.pie(df_grouped, names=group_by, values=y_column, title=title)
                    else:
                        fig = px.pie(df, names=x_column, values=y_column, title=title)
                    
                elif plot_type.lower() == "histogram":
                    fig = px.histogram(df, x=x_column, title=title)
                    
                elif plot_type.lower() == "box":
                    fig = px.box(df, x=x_column, y=y_column, title=title)
                    
                else:
                    return f"Unsupported plot type: {plot_type}"
                
                # Save the plot with absolute path
                plot_filename = f"plot_{timestamp}.html"
                plot_path = os.path.join(plot_dir, plot_filename)
                
                # Write the HTML file
                try:
                    fig.write_html(plot_path)
                    
                    # Verify file was created
                    if not os.path.exists(plot_path):
                        return f"Error: Plot file was not created at {plot_path}"
                    
                except Exception as e:
                    return f"Error saving plot: {str(e)}"
                
                # Clean up old plots
                self._clean_plot_files(user_id)
                
                # Upload to S3 for universal access
                s3_url = s3_uploader.upload_html(plot_path, user_id)
                
                # Return absolute path for clarity
                abs_plot_path = os.path.abspath(plot_path)
                
                if s3_url:
                    # Format response for different frontends
                    return self._format_plot_response(s3_url, title or f"{plot_type.capitalize()} Plot")
                else:
                    return f"Plot created successfully! Saved to: {abs_plot_path}\n⚠️ Warning: S3 upload failed, plot only available locally."
                
            except Exception as e:
                return f"Error creating plot: {str(e)}" 
        return create_plot

    def _get_tools(self):
        """Get all tools for the plot agent"""
        return [
            self._get_read_csv_tool(),
            self._get_plot_tool()
        ]

# ==================================== Agent ==============================================
    
    async def create_plot_agent(self):
        tools = self._get_tools()
        agent = create_react_agent(
            self.llm,
            tools,
            prompt=self._get_system_prompt()
        )
        return agent
    
    async def invoke_plot_agent(self, user_id: str, message: str):
        """Invoke the plot agent with a message"""
        agent = await self.create_plot_agent()
        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=message)]},
            config={"configurable": {"thread_id": user_id}}
        )
        return response["messages"][-1].content

plot_agent = PlotAgent()

if __name__ == "__main__":
    import asyncio
    
    async def main():
        user_id = "test_user"
        
        # Test with a CSV file path
        test_message = """
        Read the CSV file from agents/sql_search_agent/csv/1/data_20250101_120000.csv
        and create a bar chart showing the data.
        """
        
        response = await plot_agent.invoke_plot_agent(user_id, test_message)
        print(response)
    
    asyncio.run(main())

