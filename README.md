# AI Co-Scientist: Multi-Agent Scientific Research Framework

## Overview

AI Co-Scientist is a comprehensive multi-agent AI system designed for scientific research and hypothesis generation. Inspired by the framework described in "Towards an AI Co-Scientist," this system leverages specialized LLM-powered agents to generate, evaluate, and refine scientific hypotheses across multiple disciplines.

The development of this repository was inspired by the paper "Towards an AI Co-Scientist," which can be found [here](https://arxiv.org/pdf/2502.18864).

## 🧩 System Architecture

### Research context and gene tables

You can provide a Markdown research context with a candidate gene list, or multiple CSV gene tables with a separate Markdown description for each table. See [context and gene table instructions](CONTEXT_AND_GENE_TABLE.md), including synthetic examples and local validation commands. A model-generated hypothesis is not a validated biomarker or therapeutic target.

The system implements multiple specialized agents, each with a specific role in the scientific research process:

1. **Base Agent** - Parent class for all agents, handles core LLM interactions
2. **Generation Agent** - Generates initial scientific hypotheses from multiple perspectives
3. **Reflection Agent** - Acts as a peer reviewer, critically evaluating hypotheses
4. **Ranking Agent** - Compares and scores hypotheses using tournament-style evaluation
5. **Evolution Agent** - Refines and improves promising hypotheses
6. **Proximity Agent** - Ensures hypotheses remain relevant to research goals
7. **Meta-Review Agent** - Synthesizes research findings into comprehensive reports
8. **Supervisor Agent** - Coordinates the entire multi-agent system workflow

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/ai-coscientist.git
cd ai-coscientist
```

2. Create and activate a virtual environment:
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Create a `.env` file in the project root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

### Usage

#### Command Line Interface

Run the system from the command line:

```
python -m src.main --goal "To investigate the relationship between microbiome diversity and autoimmune disorders in urban populations" --iterations 3 --output ./results
```

Options:
- `--goal` or `-g`: Research goal to pursue
- `--model` or `-m`: LLM model to use (default: GPT-4o)
- `--temp` or `-t`: Temperature for LLM generation (default: 0.4)
- `--iterations` or `-i`: Number of refinement iterations (default: 3)
- `--output` or `-o`: Output directory for results
- `--verbose` or `-v`: Enable verbose logging

#### Python API

```python
from src import AICoScientist

# Initialize the system
acs = AICoScientist()

# Run full workflow
results = acs.run_full_workflow(
    research_goal="To investigate the relationship between microbiome diversity and autoimmune disorders in urban populations",
    iterations=3,
    output_dir="./results"
)

# Access results
top_hypothesis = results["hypotheses"][0]["hypothesis"]
print(f"Top hypothesis: {top_hypothesis}")
print(f"Executive summary: {results['report']['executive_summary']}")
```
## Output
![image](https://github.com/user-attachments/assets/d41a43fd-a272-4a37-a2e3-f2b8f5d674d1)


## 📂 Project Structure

```
ACS - AI CoScientist/
├── .env                  # Environment variables (create this file)
├── requirements.txt      # Project dependencies
├── README.md            # Project documentation
└── src/                 # Source code
    ├── __init__.py      # Package initialization
    ├── main.py          # Main application entry point
    ├── agents/          # Agent implementations
    ├── tools/           # Tool implementations
    ├── utils/           # Utility functions
    └── config/          # Configuration files
```

## 🔧 Configuration

The system's behavior can be configured through parameters in `src/config/config.py` or by passing a custom configuration dictionary to the `AICoScientist` constructor.

Key configuration options:
- `AGENT_DEFAULT_MODEL`: Default LLM model to use (e.g., "gpt-4o-2024-05-13")
- `AGENT_DEFAULT_TEMPERATURE`: Default temperature for LLM generation
- `MAX_ITERATIONS`: Maximum number of iterations for hypothesis refinement
- `MAX_TOKENS`: Maximum number of tokens for LLM responses

## 🔍 Features

- **Multi-Agent Collaboration**: Specialized agents working together to generate and refine scientific hypotheses
- **Iterative Refinement**: Hypotheses are continuously improved through multiple refinement cycles
- **Quality Evaluation**: Rigorous evaluation of hypotheses for scientific validity and relevance
- **Comprehensive Reporting**: Detailed research reports with executive summaries and ranked hypotheses
- **Tool Integration**: Scientific search, reasoning, and citation tools to enhance the research process

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Inspired by the paper "Towards an AI Co-Scientist"
- Built with OpenAI's LLM technologies
- Leverages the LangChain framework

